from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from streamstats.__main__ import main


@pytest.fixture
def bad_jsonl(tmp_path):
    path = tmp_path / "bad.jsonl"
    path.write_text(
        '{"timestamp":"2024-01-01T00:00:00","level":"INFO","source":"a","message":"m"}\n'
        '{broken\n',
        encoding="utf-8",
    )
    return path

def test_cli_csv_and_jsonl_equal(jsonl_file, csv_file, tmp_path):
    out_csv = tmp_path / "csv.json"
    out_jsonl = tmp_path / "jsonl.json"
    assert main(["analyze", str(csv_file), "--format", "csv",
                 "--output", str(out_csv)]) == 0
    assert main(["analyze", str(jsonl_file), "--format", "jsonl",
                 "--output", str(out_jsonl)]) == 0
    csv_report = json.loads(out_csv.read_text(encoding="utf-8"))
    jsonl_report = json.loads(out_jsonl.read_text(encoding="utf-8"))
    assert csv_report == jsonl_report

def test_cli_strict_mode_fails_on_bad_line(bad_jsonl, tmp_path):
    out = tmp_path / "r.json"
    rc = main(["analyze", str(bad_jsonl), "--format", "jsonl",
               "--output", str(out)])
    assert rc == 2
    assert not out.exists()

def test_cli_skip_invalid(bad_jsonl, tmp_path):
    out = tmp_path / "r.json"
    rc = main(["analyze", str(bad_jsonl), "--format", "jsonl",
               "--skip-invalid", "--output", str(out)])
    assert rc == 0
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["total_events"] == 1
    assert report["skipped_lines"] == 1

def test_cli_empty_file(tmp_path):
    empty = tmp_path / "empty.jsonl"
    empty.write_text("", encoding="utf-8")
    out = tmp_path / "r.json"
    assert main(["analyze", str(empty), "--format", "jsonl",
                 "--output", str(out)]) == 0
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["total_events"] == 0

def test_cli_multiple_files(csv_file, jsonl_file, tmp_path):
    out = tmp_path / "r.json"
    assert main(["analyze", str(csv_file),
                 "--format", "csv", "--output", str(out)]) == 0
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["total_events"] >= 0


def test_cli_help_runs():
    result = subprocess.run(
        [sys.executable, "-m", "streamstats", "--help"],
        capture_output=True, text=True,
        env={"PYTHONPATH": str(Path(__file__).resolve().parents[1] / "src")},
    )
    assert result.returncode == 0
    assert "analyze" in result.stdout


def test_cli_unicode_output(tmp_path):
    path = tmp_path / "u.jsonl"
    path.write_text(
        '{"timestamp":"2024-01-01T00:00:00","level":"INFO",'
        '"source":"источник","message":"привет"}\n',
        encoding="utf-8",
    )
    out = tmp_path / "r.json"
    assert main(["analyze", str(path), "--format", "jsonl",
                 "--output", str(out)]) == 0
    text = out.read_text(encoding="utf-8")
    assert "источник" in text
