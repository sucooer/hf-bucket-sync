from .files import router as files_router
from .buckets import router as buckets_router
from .sync import router as sync_router
from .schedule import router as schedule_router
from .notifications import router as notifications_router
from .auth import router as auth_router
from .audit import router as audit_router

__all__ = ["files_router", "buckets_router", "sync_router", "schedule_router", "notifications_router", "auth_router", "audit_router"]
