from __future__ import annotations

import json
import logging

import pytest

logger = logging.getLogger("streamstats-tests")


@pytest.fixture
def sample_rows():
    return [
        {"timestamp": "2024-01-01T10:00:00", "level": "INFO",
         "source": "svc-a", "message": "start"},
        {"timestamp": "2024-01-01T10:01:00", "level": "ERROR",
         "source": "svc-b", "message": "boom"},
        {"timestamp": "2024-01-01T10:02:00", "level": "CRITICAL",
         "source": "svc-b", "message": "критично"},
        {"timestamp": "2024-01-01T10:03:00", "level": "WARNING",
         "source": "svc-a", "message": "warn"},
    ]


@pytest.fixture
def csv_file(tmp_path, sample_rows):
    path = tmp_path / "events.csv"
    headers = ["timestamp", "level", "source", "message"]
    lines = [",".join(headers)]
    for row in sample_rows:
        lines.append(",".join(row[h] for h in headers))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


@pytest.fixture
def jsonl_file(tmp_path, sample_rows):
    path = tmp_path / "events.jsonl"
    path.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in sample_rows) + "\n",
        encoding="utf-8",
    )
    return path
