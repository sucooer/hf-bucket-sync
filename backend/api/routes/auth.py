from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Header, Request, Query
import os

from ...services.auth_token import issue_token, verify_token
from ...models.database import add_audit_log

router = APIRouter(prefix="/api/auth", tags=["auth"])

WEB_PASSWORD = os.environ.get("WEB_PASSWORD", "hf123456")


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
    if password == WEB_PASSWORD:
        token, expires_at = issue_token("web_user")
        add_audit_log("web_user", "login", "auth", "登录成功", {"expires_at": expires_at}, ip)
        return {
            "success": True,
            "token": token,
            "expires_at": datetime.fromtimestamp(expires_at, tz=timezone.utc).isoformat(),
            "expires_at_epoch": expires_at
        }
    add_audit_log("anonymous", "login_failed", "auth", "登录失败", {}, ip)
    raise HTTPException(status_code=401, detail="密码错误")


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
