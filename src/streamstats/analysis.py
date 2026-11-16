import logging
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime

from .errors import StreamStatsError
from .models import Event, validate_event

log = logging.getLogger(__name__)


@dataclass
class Stats:
    total: int = 0
    by_level: Counter = field(default_factory=Counter)
    by_source: Counter = field(default_factory=Counter)
    errors_by_source: Counter = field(default_factory=Counter)
    first_ts: datetime | None = None
    last_ts: datetime | None = None
    skipped: int = 0

    def add(self, event: Event) -> None:
        self.total += 1
        self.by_level[event.level] += 1
        self.by_source[event.source] += 1

        if event.level == "ERROR" or event.level == "CRITICAL":
            self.errors_by_source[event.source] += 1

        if self.first_ts is None:
            self.first_ts = event.timestamp
        elif event.timestamp < self.first_ts:
            self.first_ts = event.timestamp

        if self.last_ts is None:
            self.last_ts = event.timestamp
        elif event.timestamp > self.last_ts:
            self.last_ts = event.timestamp

def iter_events(raw_iter, file, skip_invalid, stats):
    iterator = iter(raw_iter)
    while True:
        try:
            line_no, raw = next(iterator)
        except StopIteration:
            break
        except StreamStatsError as e:
            if not skip_invalid:
                raise
            log.warning("ошибка парсера: %s", e)
            stats.skipped += 1
            continue
        try:
            event = validate_event(raw, file=file, line=line_no)
        except StreamStatsError as e:
            if not skip_invalid:
                raise
            log.warning("файл %s, строка %s: %s", file, line_no, e)
            stats.skipped += 1
            continue
            
        yield event

        
def analyze_files(files, skip_invalid: bool = False) -> Stats:
    stats = Stats()
    for name, raw_iter in files:
        for event in iter_events(raw_iter, name, skip_invalid, stats):
            stats.add(event)
    return stats

def top_error_sources(stats: Stats, n: int = 5):
    items = list(stats.errors_by_source.items())
    items.sort(key=lambda kv: (-kv[1], kv[0]))
    return items[:n]
