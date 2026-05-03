from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Header, Request, Query
import time
import random
import asyncio

from ...config.security import verify_web_password

from ...services.auth_token import issue_token, verify_token
from ...models.database import add_audit_log

router = APIRouter(prefix="/api/auth", tags=["auth"])

LOGIN_WINDOW_SECONDS = 60
MAX_LOGIN_ATTEMPTS = 5
FAILED_LOGIN_DELAY_MIN_SECONDS = 0.2
FAILED_LOGIN_DELAY_MAX_SECONDS = 0.4
_FAILED_LOGINS: dict[str, list[float]] = {}


def _is_rate_limited(ip: str) -> bool:
    now = time.time()
    attempts = _FAILED_LOGINS.get(ip, [])
    attempts = [ts for ts in attempts if now - ts <= LOGIN_WINDOW_SECONDS]
    _FAILED_LOGINS[ip] = attempts
    return len(attempts) >= MAX_LOGIN_ATTEMPTS


def _mark_login_failure(ip: str) -> None:
    now = time.time()
    attempts = _FAILED_LOGINS.get(ip, [])
    attempts.append(now)
    _FAILED_LOGINS[ip] = [ts for ts in attempts if now - ts <= LOGIN_WINDOW_SECONDS]


def _pick_password(payload: dict) -> str:
    if not isinstance(payload, dict):
        return ""
    for key in ("password", "admin_password", "adminPassword", "key", "secret"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


@router.post("/login")
async def login(request: Request, password: str = Query(default="")) -> dict:
    password = (password or "").strip()
    if not password:
        try:
            body = await request.json()
            password = _pick_password(body)
        except Exception:
            password = ""
    if not password:
        try:
            form = await request.form()
            password = _pick_password(dict(form))
        except Exception:
            password = ""

    ip = request.client.host if request.client else ""
    if _is_rate_limited(ip):
        await asyncio.sleep(random.uniform(FAILED_LOGIN_DELAY_MIN_SECONDS, FAILED_LOGIN_DELAY_MAX_SECONDS))
        raise HTTPException(status_code=429, detail="认证失败")

    if verify_web_password(password):
        token, expires_at = issue_token("web_user")
        _FAILED_LOGINS.pop(ip, None)
        add_audit_log("web_user", "login", "auth", "登录成功", {"expires_at": expires_at}, ip)
        return {
            "success": True,
            "token": token,
            "expires_at": datetime.fromtimestamp(expires_at, tz=timezone.utc).isoformat(),
            "expires_at_epoch": expires_at
        }
    _mark_login_failure(ip)
    add_audit_log("anonymous", "login_failed", "auth", "登录失败", {}, ip)
    await asyncio.sleep(random.uniform(FAILED_LOGIN_DELAY_MIN_SECONDS, FAILED_LOGIN_DELAY_MAX_SECONDS))
    raise HTTPException(status_code=401, detail="认证失败")


@router.get("/check")
async def check_auth(x_auth_token: str = Header(default="")) -> dict:
    try:
        payload = verify_token(x_auth_token)
    except Exception:
        raise HTTPException(status_code=401, detail="未认证")
    return {"authenticated": True, "subject": payload.get("sub", "web_user"), "expires_at": payload.get("exp")}


@router.post("/logout")
async def logout(request: Request) -> dict:
    user = getattr(request.state, "user", "web_user")
    ip = request.client.host if request.client else ""
    add_audit_log(user, "logout", "auth", "退出登录", {}, ip)
    return {"success": True}
