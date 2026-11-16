from __future__ import annotations

import io

import pytest

from streamstats.errors import InvalidEventError
from streamstats.parsers import parse_jsonl


def test_jsonl_parses_rows():
    data = '{"timestamp":"2024-01-01T00:00:00","level":"INFO","source":"a","message":"hi"}\n'
    rows = list(parse_jsonl(io.StringIO(data)))
    assert rows[0][0] == 1
    assert rows[0][1]["source"] == "a"

def test_jsonl_invalid_json_reports_line():
    data = '{"ok":1}\n{broken\n'
    with pytest.raises(InvalidEventError) as ei:
        list(parse_jsonl(io.StringIO(data)))
    assert ei.value.line == 2

def test_jsonl_not_object():
    data = "[1,2,3]\n"
    with pytest.raises(InvalidEventError):
        list(parse_jsonl(io.StringIO(data)))

def test_jsonl_skips_blank_lines():
    assert list(parse_jsonl(io.StringIO("\n\n"))) == []

def test_jsonl_unicode():
    data = '{"timestamp":"2024-01-01T00:00:00","level":"INFO","source":"s","message":"кириллица"}\n'
    rows = list(parse_jsonl(io.StringIO(data)))
    assert rows[0][1]["message"] == "кириллица"
