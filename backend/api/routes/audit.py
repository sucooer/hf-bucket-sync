from fastapi import APIRouter, HTTPException

from ...models.database import get_audit_logs

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("/logs")
async def list_logs(limit: int = 100):
    try:
        return get_audit_logs(limit=max(1, min(limit, 500)))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
