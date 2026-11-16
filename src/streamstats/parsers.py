import csv
import json
from collections.abc import Iterator
from typing import IO, Any

from .errors import InvalidEventError, UnsupportedFormatError

REQUIRED_COLUMNS = ("timestamp", "level", "source", "message")


def parse_csv(stream: IO[str], file: str = "<stream>") -> Iterator[tuple[int, dict[str, Any]]]:
    reader = csv.DictReader(stream)
    if reader.fieldnames is None:
        return
    for col in REQUIRED_COLUMNS:
        if col not in reader.fieldnames:
            raise UnsupportedFormatError(
                f"в CSV нет колонки {col!r} (файл {file})"
            )

    line_no = 1
    for row in reader:
        line_no += 1
        yield line_no, dict(row)


def parse_jsonl(stream: IO[str], file: str = "<stream>") -> Iterator[tuple[int, dict[str, Any]]]:
    line_no = 0
    for line in stream:
        line_no += 1
        line = line.strip()
        if line == "":
            continue

        try:
            data = json.loads(line)
        except json.JSONDecodeError as e:
            raise InvalidEventError(
                f"не смог распарсить JSON: {e.msg}",
                file=file,
                line=line_no,
                field="<json>",
            ) from e

        if not isinstance(data, dict):
            raise InvalidEventError(
                "строка JSONL должна быть объектом",
                file=file,
                line=line_no,
                field="<json>",
            )

        yield line_no, data


PARSERS = {
    "csv": parse_csv,
    "jsonl": parse_jsonl,
}

def get_parser(fmt: str):
    try:
        return PARSERS[fmt]
    except KeyError as exc:
        raise UnsupportedFormatError(f"unsupported format: {fmt!r}") from exc
