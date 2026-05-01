import asyncio
import os
from datetime import datetime

from ..models.schemas import SyncTask
from ..models.database import update_sync_task_status, add_audit_log
from .sync_engine import execute_sync_task


SYNC_MAX_CONCURRENCY = max(1, int(os.environ.get("SYNC_MAX_CONCURRENCY", "1")))

_queue = asyncio.Queue()
_workers = []
_started = False


async def _worker_loop(worker_id: int):
    while True:
        item = await _queue.get()
        task: SyncTask = item["task"]
        actor = item.get("actor", "web_user")
        ip = item.get("ip", "")
        try:
            update_sync_task_status(task.id, "running", "任务执行中")
            add_audit_log(actor, "sync_start", "sync_task", f"任务开始: {task.id}", {"task_id": task.id}, ip)
            result = await asyncio.to_thread(execute_sync_task, task)
            add_audit_log(
                actor,
                "sync_finish",
                "sync_task",
                f"任务结束: {task.id} ({result.status})",
                {"task_id": task.id, "status": result.status, "stats": result.stats},
                ip
            )
        except Exception as exc:
            update_sync_task_status(task.id, "failed", f"队列执行失败: {exc}", completed_at=datetime.now())
            add_audit_log(actor, "sync_failed", "sync_task", f"任务异常: {task.id}", {"error": str(exc)}, ip)
        finally:
            _queue.task_done()


def start_sync_workers():
    global _started
    if _started:
        return
    for i in range(SYNC_MAX_CONCURRENCY):
        _workers.append(asyncio.create_task(_worker_loop(i + 1)))
    _started = True


def stop_sync_workers():
    for worker in _workers:
        worker.cancel()
    _workers.clear()


async def enqueue_sync_task(task: SyncTask, actor: str, ip: str):
    await _queue.put({"task": task, "actor": actor, "ip": ip})
    add_audit_log(
        actor,
        "sync_enqueue",
        "sync_task",
        f"任务入队: {task.id}",
        {
            "task_id": task.id,
            "bucket_id": task.bucket_id,
            "direction": task.direction,
            "delete": task.delete
        },
        ip
    )


def get_queue_size() -> int:
    return _queue.qsize()
