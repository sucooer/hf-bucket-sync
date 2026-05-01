import httpx
import json
from typing import Optional
from datetime import datetime


class NotificationResult:
    def __init__(self, success: bool, message: str = "", error: str = None):
        self.success = success
        self.message = message
        self.error = error


class TelegramNotifier:
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}"

    async def send(self, title: str, content: str, **kwargs) -> NotificationResult:
        try:
            message = f"*{title}*\n\n{content}"

            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{self.api_url}/sendMessage",
                    json={
                        "chat_id": self.chat_id,
                        "text": message,
                        "parse_mode": "Markdown"
                    }
                )

                data = response.json()
                if data.get("ok"):
                    return NotificationResult(success=True, message="消息已发送")
                else:
                    return NotificationResult(
                        success=False,
                        error=data.get("description", "发送失败")
                    )
        except Exception as e:
            return NotificationResult(success=False, error=str(e))


class ServerChanNotifier:
    def __init__(self, sendkey: str):
        self.sendkey = sendkey

    def _get_url(self) -> str:
        import re
        match = re.match(r'^sctp(\d+)t', self.sendkey)
        if match:
            uid = match.group(1)
            return f"https://{uid}.push.ft07.com/send/{self.sendkey}.send"
        return f"https://{self.sendkey}.push.ft07.com/send/{self.sendkey}.send"

    async def send(self, title: str, content: str, **kwargs) -> NotificationResult:
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(
                    self._get_url(),
                    params={"title": title, "desp": content}
                )

                if response.status_code == 200:
                    try:
                        data = response.json()
                        if data.get("code") == 0:
                            return NotificationResult(success=True, message="消息已发送")
                        else:
                            return NotificationResult(
                                success=False,
                                error=data.get("errmsg", data.get("error", "发送失败"))
                            )
                    except Exception:
                        return NotificationResult(success=False, error=f"响应格式错误: {response.text[:100]}")
                else:
                    return NotificationResult(success=False, error=f"HTTP {response.status_code}: {response.text[:100]}")
        except Exception as e:
            return NotificationResult(success=False, error=str(e))


class NotificationService:
    def __init__(self):
        self.handlers = {}

    def register_telegram(self, bot_token: str, chat_id: str):
        self.handlers["telegram"] = TelegramNotifier(bot_token, chat_id)

    def register_serverchan(self, sendkey: str):
        self.handlers["serverchan"] = ServerChanNotifier(sendkey)

    def unregister(self, channel: str):
        if channel in self.handlers:
            del self.handlers[channel]

    async def send_notification(
        self,
        title: str,
        content: str,
        channels: list[str] = None
    ) -> dict:
        if channels is None:
            channels = list(self.handlers.keys())

        results = {}
        for channel in channels:
            if channel not in self.handlers:
                results[channel] = NotificationResult(
                    success=False,
                    error=f"Channel {channel} not configured"
                )
                continue

            handler = self.handlers[channel]
            result = await handler.send(title, content)
            results[channel] = result

        return results

    def has_channel(self, channel: str) -> bool:
        return channel in self.handlers

    def get_configured_channels(self) -> list[str]:
        return list(self.handlers.keys())


notification_service = NotificationService()


def render_template(template: str, task_name: str, status: str, message: str, stats: dict = None) -> str:
    if not template:
        return message

    from ..models.database import get_notification_settings
    settings = get_notification_settings()

    default_success = """## ✅ 同步任务完成

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

    default_failure = """## ❌ 同步任务失败

**任务**: `{task_name}`

**状态**: 执行失败

**时间**: `{datetime}`

### 错误信息
```
{message}
```

---
*由 HF Bucket Sync 发送*"""

    if status == 'completed':
        default_tpl = default_success
    else:
        default_tpl = default_failure

    content = template if template else default_tpl

    replacements = {
        '{task_name}': task_name,
        '{datetime}': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        '{message}': message,
        '{uploads}': str(stats.get('uploads', 0)) if stats else '0',
        '{downloads}': str(stats.get('downloads', 0)) if stats else '0',
        '{deletes}': str(stats.get('deletes', 0)) if stats else '0',
        '{skips}': str(stats.get('skips', 0)) if stats else '0',
        '{total}': str(stats.get('total', 0)) if stats else '0',
        '{status}': '✅ 成功' if status == 'completed' else '❌ 失败',
    }

    for key, value in replacements.items():
        content = content.replace(key, value)

    return content


async def send_sync_notification(
    task_name: str,
    status: str,
    message: str,
    stats: dict = None,
    channels: list[str] = None
) -> dict:
    title = f"同步任务{'成功' if status == 'completed' else '失败'}: {task_name}"

    from ..models.database import get_notification_settings
    settings = get_notification_settings()

    if status == 'completed':
        template = settings.template_success
    else:
        template = settings.template_failure

    content = render_template(template, task_name, status, message, stats)

    return await notification_service.send_notification(title, content, channels)


async def send_schedule_notification(
    schedule_name: str,
    status: str,
    message: str,
    channels: list[str] = None
) -> dict:
    title = f"定时任务{'执行成功' if status == 'completed' else '执行失败'}: {schedule_name}"

    content = f"""
任务状态: {'✅ 成功' if status == 'completed' else '❌ 失败'}
时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{message}
"""

    return await notification_service.send_notification(title, content, channels)


def register_notification_channels(config: dict):
    if config.get("telegram", {}).get("enabled"):
        notification_service.register_telegram(
            bot_token=config["telegram"]["bot_token"],
            chat_id=config["telegram"]["chat_id"]
        )

    if config.get("serverchan", {}).get("enabled"):
        notification_service.register_serverchan(
            sendkey=config["serverchan"]["sendkey"]
        )