from __future__ import annotations

from datetime import datetime

from streamstats.analysis import Stats
from streamstats.models import Event
from streamstats.report import build_report


def test_empty_report():
    stats = Stats()
    report = build_report(stats)
    assert report["total_events"] == 0
    assert report["first_timestamp"] is None
    assert report["last_timestamp"] is None
    assert report["top_error_sources"] == []

def test_report_contents():
    stats = Stats()
    stats.add(Event(datetime(2024, 1, 1, 10), "ERROR", "a", "m"))
    stats.add(Event(datetime(2024, 1, 1, 11), "INFO", "b", "m"))
    report = build_report(stats)
    assert report["total_events"] == 2
    assert report["by_level"] == {"ERROR": 1, "INFO": 1}
    assert report["top_error_sources"] == [{"source": "a", "count": 1}]
    assert report["first_timestamp"].startswith("2024-01-01T10")
    assert report["last_timestamp"].startswith("2024-01-01T11")
