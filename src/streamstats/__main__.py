import argparse
import json
import logging
import sys
from pathlib import Path

from .analysis import analyze_files
from .errors import StreamStatsError
from .parsers import get_parser
from .report import build_report


def make_argparser():
    parser = argparse.ArgumentParser(prog="streamstats")
    sub = parser.add_subparsers(dest="cmd")
    sub.required = True

    a = sub.add_parser("analyze")
    a.add_argument("inputs", nargs="+")
    a.add_argument("--format", required=True, choices=["csv", "jsonl"])
    a.add_argument("--output")
    a.add_argument("--skip-invalid", action="store_true")
    a.add_argument("--top", type=int, default=5)
    return parser

def collect_inputs(paths, fmt):
    parser = get_parser(fmt)
    result = []
    for p in paths:
        p = Path(p)

        def gen(path=p, parser=parser):
            f = path.open("r", encoding="utf-8", newline="")
            try:
                yield from parser(f, file=str(path))
            finally:
                f.close()

        result.append((str(p), gen()))
    return result

def main(argv=None):
    args = make_argparser().parse_args(argv)
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

    try:
        inputs = collect_inputs(args.inputs, args.format)
        stats = analyze_files(inputs, skip_invalid=args.skip_invalid)
        report = build_report(stats, top_n=args.top)
    except StreamStatsError as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        return 2

    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        print(text)
    return 0

if __name__ == "__main__":
    sys.exit(main())
