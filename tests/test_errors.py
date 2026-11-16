from __future__ import annotations

import pytest

from streamstats.errors import (
    InvalidEventError,
    InvalidTimestampError,
    StreamStatsError,
    UnsupportedFormatError,
)
from streamstats.models import validate_event


def test_hierarchy():
    assert issubclass(UnsupportedFormatError, StreamStatsError)
    assert issubclass(InvalidEventError, StreamStatsError)
    assert issubclass(InvalidTimestampError, InvalidEventError)

def test_validate_missing_field():
    with pytest.raises(InvalidEventError) as ei:
        validate_event({"timestamp": "2024-01-01T00:00:00"}, file="f", line=2)
    assert ei.value.field == "level"

def test_validate_bad_timestamp():
    with pytest.raises(InvalidTimestampError) as ei:
        validate_event({"timestamp": "bad", "level": "INFO",
                        "source": "a", "message": "m"}, file="f", line=7)
    assert ei.value.line == 7
    assert ei.value.field == "timestamp"

def test_validate_bad_level():
    with pytest.raises(InvalidEventError) as ei:
        validate_event({"timestamp": "2024-01-01T00:00:00", "level": "NOTICE",
                        "source": "a", "message": "m"}, file="f", line=1)
    assert ei.value.field == "level"

def test_validate_empty_source():
    with pytest.raises(InvalidEventError) as ei:
        validate_event({"timestamp": "2024-01-01T00:00:00", "level": "INFO",
                        "source": "  ", "message": "m"}, file="f", line=1)
    assert ei.value.field == "source"

def test_validate_bad_message_type():
    with pytest.raises(InvalidEventError):
        validate_event({"timestamp": "2024-01-01T00:00:00", "level": "INFO",
                        "source": "a", "message": 123}, file="f", line=1)
