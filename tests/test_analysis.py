from __future__ import annotations

import logging

import pytest

from streamstats.analysis import analyze_files, top_error_sources
from streamstats.errors import InvalidEventError

logger = logging.getLogger("streamstats-tests")

def _rows():
    return [
        {"timestamp": "2024-01-01T10:00:00", "level": "INFO",
         "source": "a", "message": "x"},
        {"timestamp": "2024-01-01T09:00:00", "level": "ERROR",
         "source": "b", "message": "y"},
        {"timestamp": "2024-01-01T11:00:00", "level": "CRITICAL",
         "source": "b", "message": "z"},
    ]

def test_aggregation_and_first_last():
    files = [("f1", iter([(2, r) for r in _rows()]))]
    stats = analyze_files(files)
    assert stats.total == 3
    assert stats.by_level["ERROR"] == 1
    assert stats.by_source["b"] == 2
    assert stats.first_ts.isoformat().startswith("2024-01-01T09")
    assert stats.last_ts.isoformat().startswith("2024-01-01T11")

def test_strict_mode_raises():
    files = [("f1", iter([(2, {"timestamp": "bad", "level": "INFO",
                                "source": "a", "message": "m"})]))]
    with pytest.raises(InvalidEventError):
        analyze_files(files)

def test_skip_invalid_counts_and_continues():
    bad = {"timestamp": "bad", "level": "INFO", "source": "a", "message": "m"}
    good = {"timestamp": "2024-01-01T00:00:00", "level": "INFO",
            "source": "a", "message": "m"}
    files = [("f1", iter([(2, bad), (3, good)]))]
    stats = analyze_files(files, skip_invalid=True)
    assert stats.total == 1
    assert stats.skipped == 1

def test_multiple_files_aggregate():
    f1 = [("f1", iter([(2, _rows()[0])]))]
    f2 = [("f2", iter([(2, _rows()[1])]))]
    stats = analyze_files(f1 + f2)
    assert stats.total == 2

def test_top_error_sources_deterministic():
    files = [("f", iter([
        (2, {"timestamp": "2024-01-01T00:00:00", "level": "ERROR",
             "source": "z", "message": "m"}),
        (3, {"timestamp": "2024-01-01T00:00:00", "level": "ERROR",
             "source": "a", "message": "m"}),
        (4, {"timestamp": "2024-01-01T00:00:00", "level": "ERROR",
             "source": "a", "message": "m"}),
    ]))]
    stats = analyze_files(files)
    top = top_error_sources(stats, n=5)
    assert top[0] == ("a", 2)
    assert top[1] == ("z", 1)

def test_top_n_parameter():
    files = [("f", iter([
        (2, {"timestamp": "2024-01-01T00:00:00", "level": "ERROR",
             "source": s, "message": "m"}) for s in ["a", "b", "c"]
    ]))]
    stats = analyze_files(files)
    assert len(top_error_sources(stats, n=2)) == 2
