from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from .collector import PerfCollector
from .config import ensure_directories, load_settings
from .flamegraph import FlameGraphGenerator
from .storage import Storage
from .timeutil import parse_time


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Continuous CPU profiler CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("status", help="show profiler status")

    list_parser = subparsers.add_parser("list", help="list recent sample windows")
    list_parser.add_argument("--hours", type=int, default=24)

    flame_parser = subparsers.add_parser("flamegraph", help="generate flame graph for a time range")
    flame_parser.add_argument("--from", dest="start", required=True)
    flame_parser.add_argument("--to", dest="end", required=True)

    subparsers.add_parser("collect-once", help="run one perf collection window")
    subparsers.add_parser("cleanup", help="remove expired samples")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    settings = load_settings()
    ensure_directories(settings)
    storage = Storage(settings)

    if args.command == "status":
        print(json.dumps(storage.status(), ensure_ascii=False, indent=2))
        return 0

    if args.command == "list":
        samples = storage.recent_samples(args.hours)
        print(json.dumps([asdict(sample) for sample in samples], ensure_ascii=False, indent=2))
        return 0

    if args.command == "flamegraph":
        generator = FlameGraphGenerator(settings, storage)
        result = generator.generate(parse_time(args.start), parse_time(args.end))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if args.command == "collect-once":
        collector = PerfCollector(settings, storage)
        sample = collector.collect_once()
        print(json.dumps(asdict(sample), ensure_ascii=False, indent=2))
        return 0

    if args.command == "cleanup":
        removed = storage.cleanup_expired()
        print(json.dumps({"removed": removed}, ensure_ascii=False, indent=2))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())

