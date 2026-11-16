from .analysis import Stats, top_error_sources


def build_report(stats: Stats, top_n: int = 5) -> dict:
    report = {
        "total_events": stats.total,
        "by_level": dict(stats.by_level),
        "by_source": dict(stats.by_source),
        "top_error_sources": [
            {"source": src, "count": cnt}
            for src, cnt in top_error_sources(stats, top_n)
        ],
        "skipped_lines": stats.skipped,
        "first_timestamp": None,
        "last_timestamp": None,
    }

    if stats.first_ts is not None:
        report["first_timestamp"] = stats.first_ts.isoformat()
    if stats.last_ts is not None:
        report["last_timestamp"] = stats.last_ts.isoformat()

    return report
