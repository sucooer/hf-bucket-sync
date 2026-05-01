from fastapi import APIRouter, HTTPException, Request

from ...models.schemas import NotificationSettings
from ...models.database import get_notification_settings, save_notification_settings, add_audit_log
from ...services.notification import notification_service

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("/settings")
async def get_settings() -> NotificationSettings:
    return get_notification_settings()


@router.post("/settings")
async def update_settings(settings: NotificationSettings, request: Request) -> NotificationSettings:
    save_notification_settings(settings)
    actor = getattr(request.state, "user", "web_user")
    ip = request.client.host if request.client else ""
    add_audit_log(
        actor,
        "config_update",
        "notification_settings",
        "更新通知配置",
        {
            "telegram_enabled": settings.telegram.enabled,
            "serverchan_enabled": settings.serverchan.enabled,
            "notify_on_success": settings.notify_on_success,
            "notify_on_failure": settings.notify_on_failure
        },
        ip
    )

    notification_service.unregister("telegram")
    notification_service.unregister("serverchan")

    if settings.telegram.enabled and settings.telegram.bot_token and settings.telegram.chat_id:
        notification_service.register_telegram(
            bot_token=settings.telegram.bot_token,
            chat_id=settings.telegram.chat_id
        )

    if settings.serverchan.enabled and settings.serverchan.sendkey:
        notification_service.register_serverchan(
            sendkey=settings.serverchan.sendkey
        )

    return settings


def notification_result_to_dict(result) -> dict:
    return {
        "success": result.success,
        "message": result.message,
        "error": result.error
    }


@router.post("/test")
async def test_notification(channel: str = None) -> dict:
    settings = get_notification_settings()

    if channel == "telegram" and settings.telegram.enabled:
        result = await notification_service.send_notification(
            title="HF Bucket Sync 测试消息",
            content="这是一条测试消息，用于验证 Telegram 通知配置是否正确。",
            channels=["telegram"]
        )
        return {"telegram": notification_result_to_dict(result["telegram"])}

    elif channel == "serverchan" and settings.serverchan.enabled:
        result = await notification_service.send_notification(
            title="HF Bucket Sync 测试消息",
            content="这是一条测试消息，用于验证方塘通知配置是否正确。",
            channels=["serverchan"]
        )
        return {"serverchan": notification_result_to_dict(result["serverchan"])}

    else:
        channels = []
        results = {}

        if settings.telegram.enabled:
            channels.append("telegram")
        if settings.serverchan.enabled:
            channels.append("serverchan")

        if not channels:
            raise HTTPException(status_code=400, detail="没有配置任何通知渠道")

        results = await notification_service.send_notification(
            title="HF Bucket Sync 测试消息",
            content="这是一条测试消息，用于验证通知配置是否正确。",
            channels=channels
        )

        return {k: notification_result_to_dict(v) for k, v in results.items()}
