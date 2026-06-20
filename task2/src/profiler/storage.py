from __future__ import annotations

import json
import os
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable, List

from .config import Settings, ensure_directories
from .timeutil import format_display, now_local, parse_time


@dataclass
class SampleWindow:
    start: str
    end: str
    file: str
    status: str = "ok"
    size_bytes: int = 0
    error: str = ""

    @property
    def start_dt(self) -> datetime:
        return parse_time(self.start)

    @property
    def end_dt(self) -> datetime:
        return parse_time(self.end)

    def overlaps(self, start: datetime, end: datetime) -> bool:
        return self.start_dt < end and self.end_dt > start


class Storage:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        ensure_directories(settings)

    def append_sample(self, sample: SampleWindow) -> None:
        self.settings.index_file.parent.mkdir(parents=True, exist_ok=True)
        with self.settings.index_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(asdict(sample), ensure_ascii=False) + "\n")

    def load_samples(self) -> List[SampleWindow]:
        if not self.settings.index_file.exists():
            return []

        samples: List[SampleWindow] = []
        with self.settings.index_file.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    samples.append(SampleWindow(**data))
                except (TypeError, ValueError, json.JSONDecodeError):
                    continue
        return samples

    def rewrite_index(self, samples: Iterable[SampleWindow]) -> None:
        tmp_file = self.settings.index_file.with_suffix(".jsonl.tmp")
        with tmp_file.open("w", encoding="utf-8") as handle:
            for sample in samples:
                handle.write(json.dumps(asdict(sample), ensure_ascii=False) + "\n")
        tmp_file.replace(self.settings.index_file)

    def query(self, start: datetime, end: datetime) -> List[SampleWindow]:
        if start >= end:
            raise ValueError("start time must be earlier than end time")

        matched = []
        for sample in self.load_samples():
            sample_path = Path(sample.file)
            if sample.status != "ok" or not sample_path.exists():
                continue
            if sample.overlaps(start, end):
                matched.append(sample)
        return sorted(matched, key=lambda item: item.start)

    def recent_samples(self, hours: int) -> List[SampleWindow]:
        cutoff = now_local() - timedelta(hours=max(1, hours))
        return [
            sample
            for sample in self.load_samples()
            if sample.end_dt >= cutoff
        ]

    def cleanup_expired(self) -> int:
        cutoff = now_local() - timedelta(hours=self.settings.retention_hours)
        kept: List[SampleWindow] = []
        removed = 0

        for sample in self.load_samples():
            if sample.end_dt >= cutoff:
                kept.append(sample)
                continue

            sample_path = Path(sample.file)
            if sample_path.exists():
                try:
                    sample_path.unlink()
                    removed += 1
                except OSError:
                    pass

        self.rewrite_index(kept)
        return removed

    def disk_summary(self) -> dict:
        usage = shutil.disk_usage(self.settings.data_dir)
        total_sample_bytes = 0
        for root, _, files in os.walk(self.settings.data_dir):
            for filename in files:
                path = Path(root) / filename
                try:
                    total_sample_bytes += path.stat().st_size
                except OSError:
                    continue

        return {
            "total_bytes": usage.total,
            "used_bytes": usage.used,
            "free_bytes": usage.free,
            "data_bytes": total_sample_bytes,
        }

    def status(self) -> dict:
        samples = self.load_samples()
        latest = samples[-1] if samples else None
        return {
            "sample_count": len(samples),
            "latest_sample": asdict(latest) if latest else None,
            "data_dir": str(self.settings.data_dir),
            "window_seconds": self.settings.window_seconds,
            "retention_hours": self.settings.retention_hours,
            "sample_freq": self.settings.sample_freq,
            "perf_event": self.settings.perf_event,
            "perf_scope": self.settings.perf_scope,
            "perf_bin": self.settings.perf_bin,
            "now": format_display(now_local()),
            "disk": self.disk_summary(),
        }

