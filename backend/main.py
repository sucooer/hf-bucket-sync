from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
import re
import os

from .api.routes import files, buckets, sync, schedule, notifications, auth
from .api.routes.schedule import start_scheduler, stop_scheduler
from .models.database import get_notification_settings
from .services.notification import register_notification_channels

WEB_PASSWORD = os.environ.get("WEB_PASSWORD", "hf123456")

app = FastAPI(
    title="HF Bucket Sync",
    description="HuggingFace Bucket Synchronization Tool",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(files.router)
app.include_router(buckets.router)
app.include_router(sync.router)
app.include_router(schedule.router)
app.include_router(notifications.router)
app.include_router(auth.router)


@app.on_event("startup")
async def startup_event():
    settings = get_notification_settings()
    register_notification_channels({
        "telegram": {
            "enabled": settings.telegram.enabled,
            "bot_token": settings.telegram.bot_token,
            "chat_id": settings.telegram.chat_id
        },
        "serverchan": {
            "enabled": settings.serverchan.enabled,
            "sendkey": settings.serverchan.sendkey
        }
    })
    start_scheduler()


@app.on_event("shutdown")
async def shutdown_event():
    stop_scheduler()


@app.get("/api/health")
async def health():
    return {"status": "healthy", "service": "hf-bucket-sync"}


@app.get("/api/auth/check")
async def check_auth():
    return {"authenticated": True}


web_dist = Path("/app/web/dist")

def is_api_path(path: str) -> bool:
    return path.startswith("api/")

def is_static_file(path: str) -> bool:
    return bool(re.match(r'.*\.[a-zA-Z0-9]+$', path)) and not path.startswith("api/")

def serve_index():
    if web_dist.exists():
        index = web_dist / "index.html"
        if index.exists():
            return FileResponse(str(index))
    return JSONResponse({"detail": "Not Found"}, status_code=404)


@app.get("/")
async def root():
    return serve_index()


@app.get("/{path:path}")
async def catch_all(path: str):
    if is_api_path(path):
        return JSONResponse({"detail": "Not Found"}, status_code=404)

    if is_static_file(path):
        file_path = web_dist / path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        return JSONResponse({"detail": "Not Found"}, status_code=404)

    return serve_index()