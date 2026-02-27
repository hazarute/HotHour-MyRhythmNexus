from datetime import datetime
from zoneinfo import ZoneInfo


TR_TIMEZONE = ZoneInfo("Europe/Istanbul")


def now_tr() -> datetime:
    return datetime.now(TR_TIMEZONE)


def to_tr_aware(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=TR_TIMEZONE)
    return value.astimezone(TR_TIMEZONE)
