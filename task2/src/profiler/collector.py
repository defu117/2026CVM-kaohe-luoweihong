from __future__ import annotations

import subprocess
import threading
from pathlib import Path
from typing import List

from .config import Settings
from .logging_util import append_log
from .storage import SampleWindow, Storage
from .timeutil import format_display, format_filename, now_local


class PerfCollector:
    def __init__(self, settings: Settings, storage: Storage) -> None:
        self.settings = settings
        self.storage = storage
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()
        self.last_error = ""
        self.last_command: List[str] = []

    @property
    def running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self) -> None:
        with self._lock:
            if self.running:
                return
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._run_loop, name="perf-collector", daemon=True)
            self._thread.start()
            append_log(self.settings.log_file, "collector started")

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=self.settings.window_seconds + 5)
            append_log(self.settings.log_file, "collector stopped")

    def collect_once(self) -> SampleWindow:
        start = now_local()
        output_file = self.settings.samples_dir / (
            f"{format_filename(start)}_{self.settings.window_seconds}s.perf.data"
        )

        command = self._build_perf_command(output_file)
        self.last_command = command
        append_log(self.settings.log_file, "running: " + " ".join(command))

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

        end = now_local()
        size_bytes = output_file.stat().st_size if output_file.exists() else 0
        error = result.stderr.strip()[-2000:]

        if result.returncode == 0 and size_bytes > 0:
            sample = SampleWindow(
                start=format_display(start),
                end=format_display(end),
                file=str(output_file),
                status="ok",
                size_bytes=size_bytes,
            )
            self.last_error = ""
            append_log(self.settings.log_file, f"sample saved: {output_file}")
        else:
            sample = SampleWindow(
                start=format_display(start),
                end=format_display(end),
                file=str(output_file),
                status="error",
                size_bytes=size_bytes,
                error=error or f"perf exited with code {result.returncode}",
            )
            self.last_error = sample.error
            append_log(self.settings.log_file, f"sample failed: {sample.error}")

        self.storage.append_sample(sample)
        removed = self.storage.cleanup_expired()
        if removed:
            append_log(self.settings.log_file, f"cleanup removed {removed} expired samples")
        return sample

    def _build_perf_command(self, output_file: Path) -> List[str]:
        command = [
            self.settings.perf_bin,
            "record",
            "-F",
            str(self.settings.sample_freq),
            "-e",
            self.settings.perf_event,
            "-g",
            "-o",
            str(output_file),
        ]

        if self.settings.perf_scope == "system":
            command.append("-a")

        command.extend(["--", "sleep", str(self.settings.window_seconds)])
        return command

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                self.collect_once()
            except Exception as exc:  # pragma: no cover - defensive runtime guard
                self.last_error = str(exc)
                append_log(self.settings.log_file, f"collector exception: {exc}")
                self._stop_event.wait(5)

