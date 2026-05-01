from fastapi import APIRouter, HTTPException, Header
import os

router = APIRouter(prefix="/api/auth", tags=["auth"])

WEB_PASSWORD = os.environ.get("WEB_PASSWORD", "hf123456")
AUTH_TOKEN = "hf-bucket-sync-auth"


@router.post("/login")
async def login(password: str) -> dict:
    if password == WEB_PASSWORD:
        return {"success": True, "token": AUTH_TOKEN}
    raise HTTPException(status_code=401, detail="密码错误")


@router.get("/check")
async def check_auth(x_auth_token: str = Header(default="")) -> dict:
    if x_auth_token != AUTH_TOKEN:
        raise HTTPException(status_code=401, detail="未认证")
    return {"authenticated": True}
