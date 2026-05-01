import os
import time
from pathlib import Path
from typing import Optional
from datetime import datetime

from huggingface_hub import sync_bucket as hf_sync_bucket

from ..models.schemas import SyncTask, SyncFilter, SyncPlan, SyncResult, NotificationConfig
from ..models.database import save_sync_task, update_sync_task_status, get_notification_settings
from .hf_client import get_hf_client
from .notification import send_sync_notification, notification_service

SYNC_RETRY_MAX_ATTEMPTS = max(1, int(os.environ.get("SYNC_RETRY_MAX_ATTEMPTS", "3")))
SYNC_RETRY_BASE_DELAY_SECONDS = max(0.1, float(os.environ.get("SYNC_RETRY_BASE_DELAY_SECONDS", "1")))
TRANSIENT_ERROR_KEYWORDS = [
    "timeout", "timed out", "connection", "network", "temporarily", "unreachable", "reset by peer", "503", "502"
]

def create_dry_run_plan(task: SyncTask) -> SyncPlan:
    try:
        client = get_hf_client()

        source = task.local_path
        if task.direction == "upload":
            destination = f"hf://buckets/{task.bucket_id}/{task.bucket_prefix}".rstrip("/")
        else:
            destination = f"hf://buckets/{task.bucket_id}/{task.bucket_prefix}".rstrip("/")
            source = destination

        result = hf_sync_bucket(
            source=source,
            destination=destination,
            delete=task.delete,
            include=task.filter.include_patterns if task.filter.include_patterns else None,
            exclude=task.filter.exclude_patterns if task.filter.exclude_patterns else None,
            dry_run=True,
            verbose=False
        )

        plan = SyncPlan()
        if result:
            for item in result:
                action = item.action.value if hasattr(item.action, 'value') else str(item.action)
                file_info = {
                    "path": item.path,
                    "size": item.size if hasattr(item, 'size') else 0
                }

                if action == "upload":
                    plan.uploads.append(file_info)
                    plan.total_size += file_info["size"]
                elif action == "download":
                    plan.downloads.append(file_info)
                    plan.total_size += file_info["size"]
                elif action == "delete":
                    plan.deletes.append(file_info)
                elif action == "skip":
                    plan.skips.append(file_info)

        return plan

    except Exception as e:
        return SyncPlan()


async def _send_notification(task_name: str, status: str, message: str, stats: dict = None):
    settings = get_notification_settings()
    channels = []

    if notification_service.has_channel("telegram") and settings.telegram.enabled:
        channels.append("telegram")
    if notification_service.has_channel("serverchan") and settings.serverchan.enabled:
        channels.append("serverchan")

    if not channels:
        return

    should_notify = (status == "completed" and settings.notify_on_success) or \
                   (status == "failed" and settings.notify_on_failure)

    if should_notify:
        await send_sync_notification(task_name, status, message, stats, channels)


def _is_transient_error(error_text: str) -> bool:
    text = (error_text or "").lower()
    return any(keyword in text for keyword in TRANSIENT_ERROR_KEYWORDS)


def _run_sync_once(task: SyncTask):
    source = task.local_path
    if task.direction == "upload":
        destination = f"hf://buckets/{task.bucket_id}/{task.bucket_prefix}".rstrip("/")
    else:
        destination = task.local_path
        source = f"hf://buckets/{task.bucket_id}/{task.bucket_prefix}".rstrip("/")
    return hf_sync_bucket(
        source=source,
        destination=destination,
        delete=task.delete,
        include=task.filter.include_patterns if task.filter.include_patterns else None,
        exclude=task.filter.exclude_patterns if task.filter.exclude_patterns else None,
        dry_run=False,
        verbose=True
    )


def execute_sync_task(task: SyncTask) -> SyncResult:
    task.status = "running"
    save_sync_task(task)

    try:
        client = get_hf_client()

        result = None
        final_error = None
        for attempt in range(1, SYNC_RETRY_MAX_ATTEMPTS + 1):
            try:
                result = _run_sync_once(task)
                final_error = None
                break
            except Exception as exc:
                final_error = exc
                if attempt >= SYNC_RETRY_MAX_ATTEMPTS or not _is_transient_error(str(exc)):
                    break
                time.sleep(SYNC_RETRY_BASE_DELAY_SECONDS * (2 ** (attempt - 1)))
        if final_error:
            raise final_error

        uploads = 0
        downloads = 0
        deletes = 0
        skips = 0

        if result:
            for item in result:
                action = item.action.value if hasattr(item.action, 'value') else str(item.action)
                if action == "upload":
                    uploads += 1
                elif action == "download":
                    downloads += 1
                elif action == "delete":
                    deletes += 1
                elif action == "skip":
                    skips += 1

        stats = {
            "uploads": uploads,
            "downloads": downloads,
            "deletes": deletes,
            "skips": skips,
            "total": uploads + downloads + deletes + skips
        }

        task.status = "completed"
        task.completed_at = datetime.now()
        task.stats = stats
        task.message = f"Synced: {uploads} uploads, {downloads} downloads, {deletes} deletes, {skips} skips"
        save_sync_task(task)

        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(_send_notification(
                    task.local_path,
                    "completed",
                    task.message,
                    stats
                ))
            else:
                loop.run_until_complete(_send_notification(
                    task.local_path,
                    "completed",
                    task.message,
                    stats
                ))
        except Exception:
            pass

        return SyncResult(
            task_id=task.id,
            status="completed",
            message=task.message,
            stats=stats
        )

    except Exception as e:
        task.status = "failed"
        task.completed_at = datetime.now()
        task.message = f"Sync failed: {str(e)}"
        save_sync_task(task)

        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(_send_notification(
                    task.local_path,
                    "failed",
                    task.message,
                    {}
                ))
            else:
                loop.run_until_complete(_send_notification(
                    task.local_path,
                    "failed",
                    task.message,
                    {}
                ))
        except Exception:
            pass

        return SyncResult(
            task_id=task.id,
            status="failed",
            message=str(e),
            stats={}
        )


def execute_schedule_sync(schedule_data: dict) -> SyncResult:
    task = SyncTask(
        local_path=schedule_data["local_path"],
        bucket_id=schedule_data["bucket_id"],
        bucket_prefix=schedule_data.get("bucket_prefix", ""),
        direction=schedule_data.get("direction", "upload"),
        filter=schedule_data.get("filter", SyncFilter()),
        delete=schedule_data.get("delete", False)
    )

    return execute_sync_task(task)
