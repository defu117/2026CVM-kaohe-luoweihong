from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


def _int_env(name: str, default: int, minimum: int) -> int:
    raw = os.environ.get(name, str(default)).strip()
    try:
        value = int(raw)
    except ValueError:
        return default
    return max(minimum, value)


def _find_perf_binary(configured: str) -> str:
    if configured and configured != "perf":
        return configured

    found = shutil.which("perf")
    if found and _perf_works(found):
        return found

    tools_root = Path("/usr/lib/linux-tools")
    if tools_root.exists():
        candidates = sorted(tools_root.glob("*/perf"), reverse=True)
        for candidate in candidates:
            if candidate.is_file() and _perf_works(str(candidate)):
                return str(candidate)

    return "perf"


def _perf_works(candidate: str) -> bool:
    try:
        result = subprocess.run(
            [candidate, "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=3,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    samples_dir: Path
    flamegraphs_dir: Path
    tmp_dir: Path
    index_file: Path
    log_file: Path
    window_seconds: int
    retention_hours: int
    sample_freq: int
    perf_event: str
    perf_scope: str
    perf_bin: str
    flamegraph_dir: Path
    host: str
    port: int
    start_collector: bool


def load_settings() -> Settings:
    data_dir = Path(os.environ.get("DATA_DIR", "/data")).resolve()
    perf_bin = _find_perf_binary(os.environ.get("PERF_BIN", "perf"))

    return Settings(
        data_dir=data_dir,
        samples_dir=data_dir / "samples",
        flamegraphs_dir=data_dir / "flamegraphs",
        tmp_dir=data_dir / "tmp",
        index_file=data_dir / "index.jsonl",
        log_file=data_dir / "profiler.log",
        window_seconds=_int_env("WINDOW_SECONDS", 60, 1),
        retention_hours=_int_env("RETENTION_HOURS", 24, 1),
        sample_freq=_int_env("SAMPLE_FREQ", 99, 1),
        perf_event=os.environ.get("PERF_EVENT", "cpu-clock").strip() or "cpu-clock",
        perf_scope=os.environ.get("PERF_SCOPE", "system").strip().lower() or "system",
        perf_bin=perf_bin,
        flamegraph_dir=Path(os.environ.get("FLAMEGRAPH_DIR", "/opt/FlameGraph")).resolve(),
        host=os.environ.get("HOST", "0.0.0.0"),
        port=_int_env("PORT", 8080, 1),
        start_collector=os.environ.get("START_COLLECTOR", "1").strip() not in {"0", "false", "False"},
    )


def ensure_directories(settings: Settings) -> None:
    settings.samples_dir.mkdir(parents=True, exist_ok=True)
    settings.flamegraphs_dir.mkdir(parents=True, exist_ok=True)
    settings.tmp_dir.mkdir(parents=True, exist_ok=True)
    settings.data_dir.mkdir(parents=True, exist_ok=True)
