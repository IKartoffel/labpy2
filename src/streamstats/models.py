from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .errors import InvalidEventError, InvalidTimestampError

VALID_LEVELS: frozenset[str] = frozenset(
    {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
)
REQUIRED_FIELDS: tuple[str, ...] = ("timestamp", "level", "source", "message")


@dataclass(frozen=True, slots=True)
class Event:
    timestamp: datetime
    level: str
    source: str
    message: str


def _parse_timestamp(raw: Any, *, file: str, line: int) -> datetime:
    if not isinstance(raw, str) or not raw.strip():
        raise InvalidTimestampError(
            "timestamp missing or empty", file=file, line=line, field="timestamp"
        )
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as exc:
        raise InvalidTimestampError(
            f"invalid timestamp {raw!r}", file=file, line=line, field="timestamp"
        ) from exc


def validate_event(raw: dict[str, Any], *, file: str, line: int) -> Event:
    for field in REQUIRED_FIELDS:
        if field not in raw:
            raise InvalidEventError(
                f"missing field {field!r}", file=file, line=line, field=field
            )

    ts_raw = raw["timestamp"]
    timestamp = _parse_timestamp(ts_raw, file=file, line=line)

    level = raw["level"]
    if not isinstance(level, str) or level not in VALID_LEVELS:
        raise InvalidEventError(
            f"invalid level {level!r}", file=file, line=line, field="level"
        )

    source = raw["source"]
    if not isinstance(source, str) or not source.strip():
        raise InvalidEventError(
            "source must be non-empty string", file=file, line=line, field="source"
        )

    message = raw["message"]
    if not isinstance(message, str):
        raise InvalidEventError(
            "message must be a string", file=file, line=line, field="message"
        )

    return Event(timestamp=timestamp, level=level, source=source, message=message)
