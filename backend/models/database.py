import sqlite3
import json
from datetime import datetime
from typing import Optional
from pathlib import Path

from .schemas import SyncTask, Schedule, SyncFilter, NotificationSettings


DB_PATH = Path("/app/data/app.db")


def get_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sync_tasks (
            id TEXT PRIMARY KEY,
            local_path TEXT NOT NULL,
            bucket_id TEXT NOT NULL,
            bucket_prefix TEXT DEFAULT '',
            direction TEXT DEFAULT 'upload',
            filter_json TEXT,
            delete_flag INTEGER DEFAULT 0,
            status TEXT DEFAULT 'pending',
            message TEXT,
            created_at TEXT,
            completed_at TEXT,
            stats_json TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schedules (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            local_path TEXT NOT NULL,
            bucket_id TEXT NOT NULL,
            bucket_prefix TEXT DEFAULT '',
            cron TEXT NOT NULL,
            direction TEXT DEFAULT 'upload',
            filter_json TEXT,
            delete_flag INTEGER DEFAULT 0,
            enabled INTEGER DEFAULT 1,
            last_run TEXT,
            next_run TEXT,
            created_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notification_settings (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            telegram_enabled INTEGER DEFAULT 0,
            telegram_bot_token TEXT DEFAULT '',
            telegram_chat_id TEXT DEFAULT '',
            serverchan_enabled INTEGER DEFAULT 0,
            serverchan_sendkey TEXT DEFAULT '',
            notify_on_success INTEGER DEFAULT 1,
            notify_on_failure INTEGER DEFAULT 1,
            template_success TEXT DEFAULT '',
            template_failure TEXT DEFAULT '',
            updated_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            actor TEXT NOT NULL,
            action TEXT NOT NULL,
            resource TEXT DEFAULT '',
            summary TEXT DEFAULT '',
            payload_json TEXT DEFAULT '',
            ip TEXT DEFAULT '',
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM notification_settings")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO notification_settings (id, updated_at)
            VALUES (1, ?)
        """, (datetime.now().isoformat(),))

    conn.commit()
    conn.close()


def save_sync_task(task: SyncTask):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO sync_tasks
        (id, local_path, bucket_id, bucket_prefix, direction, filter_json,
         delete_flag, status, message, created_at, completed_at, stats_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        task.id,
        task.local_path,
        task.bucket_id,
        task.bucket_prefix,
        task.direction,
        task.filter.model_dump_json(),
        int(task.delete),
        task.status,
        task.message,
        task.created_at.isoformat(),
        task.completed_at.isoformat() if task.completed_at else None,
        task.stats.json() if task.stats else None
    ))
    conn.commit()
    conn.close()


def get_sync_tasks(limit: int = 50) -> list[SyncTask]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM sync_tasks ORDER BY created_at DESC LIMIT ?
    """, (limit,))

    tasks = []
    for row in cursor.fetchall():
        filter_data = SyncFilter.model_validate_json(row["filter_json"]) if row["filter_json"] else SyncFilter()
        tasks.append(SyncTask(
            id=row["id"],
            local_path=row["local_path"],
            bucket_id=row["bucket_id"],
            bucket_prefix=row["bucket_prefix"],
            direction=row["direction"],
            filter=filter_data,
            delete=bool(row["delete_flag"]),
            status=row["status"],
            message=row["message"],
            created_at=datetime.fromisoformat(row["created_at"]),
            completed_at=datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None,
            stats=json.loads(row["stats_json"]) if row["stats_json"] else None
        ))
    conn.close()
    return tasks


def update_sync_task_status(task_id: str, status: str, message: Optional[str] = None,
                            stats: Optional[dict] = None, completed_at: Optional[datetime] = None):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE sync_tasks
        SET status = ?, message = ?, stats_json = ?, completed_at = ?
        WHERE id = ?
    """, (status, message, json.dumps(stats) if stats else None,
          completed_at.isoformat() if completed_at else None, task_id))
    conn.commit()
    conn.close()


def save_schedule(schedule: Schedule) -> Schedule:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO schedules
        (id, name, local_path, bucket_id, bucket_prefix, cron, direction,
         filter_json, delete_flag, enabled, last_run, next_run, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        schedule.id,
        schedule.name,
        schedule.local_path,
        schedule.bucket_id,
        schedule.bucket_prefix,
        schedule.cron,
        schedule.direction,
        schedule.filter.model_dump_json(),
        int(schedule.delete),
        int(schedule.enabled),
        schedule.last_run.isoformat() if schedule.last_run else None,
        schedule.next_run.isoformat() if schedule.next_run else None,
        schedule.created_at.isoformat()
    ))
    conn.commit()
    conn.close()
    return schedule


def get_schedules() -> list[Schedule]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM schedules ORDER BY created_at DESC")

    schedules = []
    for row in cursor.fetchall():
        filter_data = SyncFilter.model_validate_json(row["filter_json"]) if row["filter_json"] else SyncFilter()
        schedules.append(Schedule(
            id=row["id"],
            name=row["name"],
            local_path=row["local_path"],
            bucket_id=row["bucket_id"],
            bucket_prefix=row["bucket_prefix"],
            cron=row["cron"],
            direction=row["direction"],
            filter=filter_data,
            delete=bool(row["delete_flag"]),
            enabled=bool(row["enabled"]),
            last_run=datetime.fromisoformat(row["last_run"]) if row["last_run"] else None,
            next_run=datetime.fromisoformat(row["next_run"]) if row["next_run"] else None,
            created_at=datetime.fromisoformat(row["created_at"])
        ))
    conn.close()
    return schedules


def get_schedule_by_id(schedule_id: str) -> Optional[Schedule]:
    schedules = get_schedules()
    for s in schedules:
        if s.id == schedule_id:
            return s
    return None


def delete_schedule(schedule_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM schedules WHERE id = ?", (schedule_id,))
    conn.commit()
    conn.close()


def update_schedule_runs(schedule_id: str, last_run: datetime, next_run: Optional[datetime] = None):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE schedules
        SET last_run = ?, next_run = ?
        WHERE id = ?
    """, (last_run.isoformat(), next_run.isoformat() if next_run else None, schedule_id))
    conn.commit()
    conn.close()


def get_notification_settings() -> NotificationSettings:
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(notification_settings)")
    columns = {row[1] for row in cursor.fetchall()}

    cursor.execute("SELECT * FROM notification_settings WHERE id = 1")
    row = cursor.fetchone()
    conn.close()

    if not row:
        return NotificationSettings()

    return NotificationSettings(
        telegram={
            "enabled": bool(row["telegram_enabled"]),
            "bot_token": row["telegram_bot_token"] or "",
            "chat_id": row["telegram_chat_id"] or ""
        },
        serverchan={
            "enabled": bool(row["serverchan_enabled"]),
            "sendkey": row["serverchan_sendkey"] or ""
        },
        notify_on_success=bool(row["notify_on_success"]),
        notify_on_failure=bool(row["notify_on_failure"]),
        template_success=row["template_success"] if "template_success" in columns and row["template_success"] else "",
        template_failure=row["template_failure"] if "template_failure" in columns and row["template_failure"] else ""
    )


def save_notification_settings(settings: NotificationSettings):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(notification_settings)")
    columns = {row[1] for row in cursor.fetchall()}

    if "template_success" not in columns:
        cursor.execute("ALTER TABLE notification_settings ADD COLUMN template_success TEXT DEFAULT ''")

    if "template_failure" not in columns:
        cursor.execute("ALTER TABLE notification_settings ADD COLUMN template_failure TEXT DEFAULT ''")

    cursor.execute("""
        UPDATE notification_settings
        SET telegram_enabled = ?,
            telegram_bot_token = ?,
            telegram_chat_id = ?,
            serverchan_enabled = ?,
            serverchan_sendkey = ?,
            notify_on_success = ?,
            notify_on_failure = ?,
            template_success = ?,
            template_failure = ?,
            updated_at = ?
        WHERE id = 1
    """, (
        int(settings.telegram.enabled),
        settings.telegram.bot_token,
        settings.telegram.chat_id,
        int(settings.serverchan.enabled),
        settings.serverchan.sendkey,
        int(settings.notify_on_success),
        int(settings.notify_on_failure),
        settings.template_success,
        settings.template_failure,
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()


def add_audit_log(actor: str, action: str, resource: str = "", summary: str = "",
                  payload: Optional[dict] = None, ip: str = ""):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO audit_logs (actor, action, resource, summary, payload_json, ip, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        actor or "anonymous",
        action,
        resource,
        summary,
        json.dumps(payload or {}, ensure_ascii=False),
        ip or "",
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()


def get_audit_logs(limit: int = 100):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


init_db()
