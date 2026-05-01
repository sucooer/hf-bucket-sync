import json
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from uuid import uuid4


def generate_id() -> str:
    return str(uuid4())[:8]


class FileInfo(BaseModel):
    name: str
    path: str
    is_dir: bool
    size: int = 0
    modified: Optional[datetime] = None


class BucketInfo(BaseModel):
    id: str
    private: bool
    size: int
    total_files: int
    created_at: Optional[datetime] = None


class BucketFile(BaseModel):
    path: str
    type: str
    size: int = 0


class SyncFilter(BaseModel):
    include_patterns: list[str] = ["*"]
    exclude_patterns: list[str] = []
    min_size: Optional[int] = None
    max_size: Optional[int] = None


class NotificationConfig(BaseModel):
    enabled: bool = False
    channels: list[str] = []


class TelegramConfig(BaseModel):
    enabled: bool = False
    bot_token: str = ""
    chat_id: str = ""


class ServerChanConfig(BaseModel):
    enabled: bool = False
    sendkey: str = ""


class NotificationSettings(BaseModel):
    telegram: TelegramConfig = Field(default_factory=TelegramConfig)
    serverchan: ServerChanConfig = Field(default_factory=ServerChanConfig)
    notify_on_success: bool = True
    notify_on_failure: bool = True
    template_success: str = Field(default="")
    template_failure: str = Field(default="")


class NotificationTemplates:
    DEFAULT_SUCCESS_TEMPLATE = """## ✅ 同步任务完成

**任务**: `{task_name}`

**状态**: 成功完成

**时间**: `{datetime}`

### 同步统计
- 📤 上传: `{uploads}` 个文件
- 📥 下载: `{downloads}` 个文件
- 🗑️ 删除: `{deletes}` 个文件
- ⏭️ 跳过: `{skips}` 个文件

---
*由 HF Bucket Sync 发送*"""

    DEFAULT_FAILURE_TEMPLATE = """## ❌ 同步任务失败

**任务**: `{task_name}`

**状态**: 执行失败

**时间**: `{datetime}`

### 错误信息
```
{message}
```

---
*由 HF Bucket Sync 发送*"""


class SyncTaskCreate(BaseModel):
    local_path: str
    bucket_id: str
    bucket_prefix: str = ""
    direction: str = "upload"
    filter: SyncFilter = Field(default_factory=SyncFilter)
    delete: bool = False
    notification: NotificationConfig = Field(default_factory=NotificationConfig)


class SyncTask(BaseModel):
    id: str = Field(default_factory=generate_id)
    local_path: str
    bucket_id: str
    bucket_prefix: str = ""
    direction: str = "upload"
    filter: SyncFilter = Field(default_factory=SyncFilter)
    delete: bool = False
    notification: NotificationConfig = Field(default_factory=NotificationConfig)
    status: str = "pending"
    message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    stats: Optional[dict] = None


class SyncPlan(BaseModel):
    uploads: list[dict] = []
    downloads: list[dict] = []
    deletes: list[dict] = []
    skips: list[dict] = []
    total_size: int = 0


class SyncResult(BaseModel):
    task_id: str
    status: str
    message: str
    stats: dict


class ScheduleCreate(BaseModel):
    name: str
    local_path: str
    bucket_id: str
    bucket_prefix: str = ""
    cron: str
    direction: str = "upload"
    filter: SyncFilter = Field(default_factory=SyncFilter)
    delete: bool = False
    enabled: bool = True
    notification: NotificationConfig = Field(default_factory=NotificationConfig)


class ScheduleUpdate(BaseModel):
    name: Optional[str] = None
    local_path: Optional[str] = None
    bucket_id: Optional[str] = None
    bucket_prefix: Optional[str] = None
    cron: Optional[str] = None
    direction: Optional[str] = None
    filter: Optional[SyncFilter] = None
    delete: Optional[bool] = None
    enabled: Optional[bool] = None
    notification: Optional[NotificationConfig] = None


class Schedule(BaseModel):
    id: str = Field(default_factory=generate_id)
    name: str
    local_path: str
    bucket_id: str
    bucket_prefix: str = ""
    cron: str
    direction: str = "upload"
    filter: SyncFilter = Field(default_factory=SyncFilter)
    delete: bool = False
    enabled: bool = True
    notification: NotificationConfig = Field(default_factory=NotificationConfig)
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)