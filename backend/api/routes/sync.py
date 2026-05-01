from fastapi import APIRouter, HTTPException, Request

from ...models.schemas import SyncTask, SyncTaskCreate, SyncPlan, SyncResult
from ...models.database import save_sync_task, get_sync_tasks, add_audit_log
from ...services.sync_engine import create_dry_run_plan
from ...services.sync_queue import enqueue_sync_task, get_queue_size

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
async def execute(task_data: SyncTaskCreate, request: Request) -> SyncResult:
    try:
        actor = getattr(request.state, "user", "web_user")
        ip = request.client.host if request.client else ""
        task = SyncTask(
            local_path=task_data.local_path,
            bucket_id=task_data.bucket_id,
            bucket_prefix=task_data.bucket_prefix,
            direction=task_data.direction,
            filter=task_data.filter,
            delete=task_data.delete
        )
        task.status = "queued"
        task.message = "任务已进入队列"
        save_sync_task(task)
        add_audit_log(
            actor,
            "sync_execute",
            "sync_task",
            f"提交同步任务: {task.id}",
            {
                "task_id": task.id,
                "local_path": task.local_path,
                "bucket_id": task.bucket_id,
                "bucket_prefix": task.bucket_prefix,
                "direction": task.direction,
                "delete": task.delete
            },
            ip
        )
        await enqueue_sync_task(task, actor=actor, ip=ip)
        return SyncResult(
            task_id=task.id,
            status="queued",
            message=f"任务已入队，当前队列长度: {get_queue_size()}",
            stats={},
            queued=True
        )
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
