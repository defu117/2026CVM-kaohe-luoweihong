from __future__ import annotations

from datetime import datetime

DISPLAY_FORMAT = "%Y-%m-%d %H:%M:%S"
FILENAME_FORMAT = "%Y%m%d_%H%M%S"


def now_local() -> datetime:
    return datetime.now().astimezone().replace(tzinfo=None)


def format_display(value: datetime) -> str:
    return value.strftime(DISPLAY_FORMAT)


def format_filename(value: datetime) -> str:
    return value.strftime(FILENAME_FORMAT)


def parse_time(value: str) -> datetime:
    text = value.strip()
    if not text:
        raise ValueError("time value is empty")

    if text.isdigit():
        return datetime.fromtimestamp(int(text))

    normalized = text.replace("T", " ")
    if len(normalized) == 16:
        normalized = normalized + ":00"

    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        pass

    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(normalized, fmt)
        except ValueError:
            continue

    raise ValueError(f"unsupported time format: {value!r}")

