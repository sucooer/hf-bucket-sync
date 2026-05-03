from datetime import datetime, timezone


def utc_now_iso_z() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def parse_api_datetime(value: str) -> datetime:
    if not value:
        raise ValueError('datetime value is empty')
    if value.endswith('Z'):
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        # Legacy records were stored without timezone in UTC.
        return parsed.replace(tzinfo=timezone.utc)
    return parsed
