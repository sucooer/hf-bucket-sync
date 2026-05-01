from fastapi import APIRouter, HTTPException
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import pytz

from ...models.schemas import Schedule, ScheduleCreate, ScheduleUpdate
from ...models.database import save_schedule, get_schedules, get_schedule_by_id, delete_schedule, update_schedule_runs
from ...services.sync_engine import execute_schedule_sync

router = APIRouter(prefix="/api/schedules", tags=["schedules"])

scheduler = AsyncIOScheduler(timezone=pytz.timezone("Asia/Shanghai"))


def run_sync_job(schedule_id: str, schedule_data: dict):
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = execute_schedule_sync(schedule_data)
        update_schedule_runs(schedule_id, datetime.now())
    except Exception as e:
        print(f"Scheduled sync failed: {e}")
    finally:
        loop.close()


def add_job_to_scheduler(schedule: Schedule):
    try:
        parts = schedule.cron.split()
        if len(parts) == 5:
            trigger = CronTrigger(
                minute=parts[0],
                hour=parts[1],
                day=parts[2],
                month=parts[3],
                day_of_week=parts[4],
                timezone=pytz.timezone("Asia/Shanghai")
            )
        elif len(parts) == 4:
            trigger = CronTrigger(
                minute=parts[0],
                hour=parts[1],
                day=parts[2],
                month=parts[3],
                timezone=pytz.timezone("Asia/Shanghai")
            )
        elif len(parts) == 3:
            trigger = CronTrigger(
                minute=parts[0],
                hour=parts[1],
                day_of_week=parts[2],
                timezone=pytz.timezone("Asia/Shanghai")
            )
        else:
            trigger = CronTrigger(minute="*/5")

        job_data = {
            "local_path": schedule.local_path,
            "bucket_id": schedule.bucket_id,
            "bucket_prefix": schedule.bucket_prefix,
            "direction": schedule.direction,
            "filter": schedule.filter.model_dump() if hasattr(schedule.filter, 'model_dump') else {},
            "delete": schedule.delete
        }

        scheduler.add_job(
            run_sync_job,
            trigger=trigger,
            args=[schedule.id, job_data],
            id=schedule.id,
            replace_existing=True
        )
    except Exception as e:
        print(f"Failed to add job to scheduler: {e}")


def remove_job_from_scheduler(schedule_id: str):
    try:
        scheduler.remove_job(schedule_id)
    except Exception:
        pass


@router.post("", response_model=Schedule)
async def create_schedule(data: ScheduleCreate) -> Schedule:
    try:
        schedule = Schedule(
            name=data.name,
            local_path=data.local_path,
            bucket_id=data.bucket_id,
            bucket_prefix=data.bucket_prefix,
            cron=data.cron,
            direction=data.direction,
            filter=data.filter,
            delete=data.delete,
            enabled=data.enabled
        )

        saved = save_schedule(schedule)

        if saved.enabled:
            add_job_to_scheduler(saved)

        return saved
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def list_schedules() -> list[Schedule]:
    try:
        schedules = get_schedules()
        for s in schedules:
            if scheduler.running:
                try:
                    job = scheduler.get_job(s.id)
                    if job:
                        s.next_run = job.next_run_time
                except Exception:
                    pass
        return schedules
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{schedule_id}")
async def get_schedule(schedule_id: str) -> Schedule:
    schedule = get_schedule_by_id(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule


@router.put("/{schedule_id}", response_model=Schedule)
async def update_schedule(schedule_id: str, data: ScheduleUpdate) -> Schedule:
    schedule = get_schedule_by_id(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    if data.name is not None:
        schedule.name = data.name
    if data.cron is not None:
        schedule.cron = data.cron
        remove_job_from_scheduler(schedule_id)
        if schedule.enabled:
            add_job_to_scheduler(schedule)
    if data.enabled is not None:
        schedule.enabled = data.enabled
        if data.enabled:
            add_job_to_scheduler(schedule)
        else:
            remove_job_from_scheduler(schedule_id)
    if data.local_path is not None:
        schedule.local_path = data.local_path
    if data.bucket_id is not None:
        schedule.bucket_id = data.bucket_id
    if data.bucket_prefix is not None:
        schedule.bucket_prefix = data.bucket_prefix
    if data.delete is not None:
        schedule.delete = data.delete

    return save_schedule(schedule)


@router.delete("/{schedule_id}")
async def delete_schedule_route(schedule_id: str):
    schedule = get_schedule_by_id(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    remove_job_from_scheduler(schedule_id)
    delete_schedule(schedule_id)
    return {"status": "deleted", "id": schedule_id}


def start_scheduler():
    if not scheduler.running:
        schedules = get_schedules()
        for s in schedules:
            if s.enabled:
                add_job_to_scheduler(s)
        scheduler.start()


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()