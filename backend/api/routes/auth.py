from fastapi import APIRouter, HTTPException
import os

router = APIRouter(prefix="/api/auth", tags=["auth"])

WEB_PASSWORD = os.environ.get("WEB_PASSWORD", "hf123456")


@router.post("/login")
async def login(password: str) -> dict:
    if password == WEB_PASSWORD:
        return {"success": True, "token": "hf-bucket-sync-auth"}
    raise HTTPException(status_code=401, detail="密码错误")


@router.get("/check")
async def check_auth() -> dict:
    return {"authenticated": True}