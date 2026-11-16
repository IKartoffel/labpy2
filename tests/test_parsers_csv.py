from __future__ import annotations

import io

import pytest

from streamstats.errors import UnsupportedFormatError
from streamstats.parsers import parse_csv


def test_csv_parses_rows():
    data = "timestamp,level,source,message\n2024-01-01T00:00:00,INFO,a,hi\n"
    rows = list(parse_csv(io.StringIO(data)))
    assert rows[0][0] == 2
    assert rows[0][1]["source"] == "a"


def test_csv_missing_columns():
    data = "timestamp,level\n2024-01-01T00:00:00,INFO\n"
    with pytest.raises(UnsupportedFormatError):
        list(parse_csv(io.StringIO(data)))


def test_csv_empty_file_yields_nothing():
    assert list(parse_csv(io.StringIO(""))) == []


def test_csv_unicode():
    data = "timestamp,level,source,message\n2024-01-01T00:00:00,INFO,источник,привет\n"
    rows = list(parse_csv(io.StringIO(data)))
    assert rows[0][1]["message"] == "привет"
