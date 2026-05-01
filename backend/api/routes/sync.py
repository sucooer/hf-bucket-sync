from fastapi import APIRouter, HTTPException
from typing import Optional

from ...models.schemas import SyncTask, SyncTaskCreate, SyncPlan, SyncResult
from ...models.database import save_sync_task, get_sync_tasks, update_sync_task_status
from ...services.sync_engine import create_dry_run_plan, execute_sync_task

router = APIRouter(prefix="/api/sync", tags=["sync"])


@router.post("/dry-run", response_model=SyncPlan)
async def dry_run(task_data: SyncTaskCreate) -> SyncPlan:
    try:
        task = SyncTask(
            local_path=task_data.local_path,
            bucket_id=task_data.bucket_id,
            bucket_prefix=task_data.bucket_prefix,
            direction=task_data.direction,
            filter=task_data.filter,
            delete=task_data.delete
        )
        return create_dry_run_plan(task)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute", response_model=SyncResult)
async def execute(task_data: SyncTaskCreate) -> SyncResult:
    try:
        task = SyncTask(
            local_path=task_data.local_path,
            bucket_id=task_data.bucket_id,
            bucket_prefix=task_data.bucket_prefix,
            direction=task_data.direction,
            filter=task_data.filter,
            delete=task_data.delete
        )
        save_sync_task(task)
        return execute_sync_task(task)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_history(limit: int = 50) -> list[SyncTask]:
    try:
        return get_sync_tasks(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/task/{task_id}")
async def get_task(task_id: str) -> SyncTask:
    tasks = get_sync_tasks(100)
    for task in tasks:
        if task.id == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")