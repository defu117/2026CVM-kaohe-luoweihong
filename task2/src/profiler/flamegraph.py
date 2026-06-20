from __future__ import annotations

import html
import json
import subprocess
from collections import Counter, defaultdict
from dataclasses import asdict
from pathlib import Path
from typing import Dict, Iterable, List

from .config import Settings
from .logging_util import append_log
from .storage import SampleWindow, Storage
from .timeutil import format_filename


class FlameGraphError(RuntimeError):
    pass


class FlameGraphGenerator:
    def __init__(self, settings: Settings, storage: Storage) -> None:
        self.settings = settings
        self.storage = storage

    def generate(self, start, end) -> dict:
        samples = self.storage.query(start, end)
        if not samples:
            raise FlameGraphError("no perf samples found for the selected time range")

        safe_name = f"flame_{format_filename(start)}_{format_filename(end)}"
        combined_perf = self.settings.tmp_dir / f"{safe_name}.perf"
        folded_file = self.settings.tmp_dir / f"{safe_name}.folded"
        svg_file = self.settings.flamegraphs_dir / f"{safe_name}.svg"
        meta_file = self.settings.flamegraphs_dir / f"{safe_name}.json"

        self._perf_script(samples, combined_perf)

        used_official = self._try_official_flamegraph(combined_perf, folded_file, svg_file, start, end)
        if not used_official:
            stacks = collapse_perf_script(combined_perf)
            if not stacks:
                raise FlameGraphError("perf script produced no stack frames")
            render_fallback_svg(stacks, svg_file, f"CPU FlameGraph {start} - {end}")

        metadata = {
            "start": str(start),
            "end": str(end),
            "svg": str(svg_file),
            "url": f"/flamegraphs/{svg_file.name}",
            "samples": [asdict(sample) for sample in samples],
            "sample_count": len(samples),
            "renderer": "official FlameGraph" if used_official else "built-in fallback",
        }
        meta_file.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
        append_log(self.settings.log_file, f"flamegraph generated: {svg_file}")
        return metadata

    def _perf_script(self, samples: Iterable[SampleWindow], output_file: Path) -> None:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with output_file.open("w", encoding="utf-8", errors="replace") as out:
            for sample in samples:
                command = [self.settings.perf_bin, "script", "-i", sample.file]
                append_log(self.settings.log_file, "running: " + " ".join(command))
                result = subprocess.run(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    errors="replace",
                    check=False,
                )
                if result.returncode != 0:
                    raise FlameGraphError(result.stderr.strip() or "perf script failed")
                out.write(result.stdout)
                if result.stdout and not result.stdout.endswith("\n"):
                    out.write("\n")

    def _try_official_flamegraph(self, perf_script_file: Path, folded_file: Path, svg_file: Path, start, end) -> bool:
        stackcollapse = self.settings.flamegraph_dir / "stackcollapse-perf.pl"
        flamegraph = self.settings.flamegraph_dir / "flamegraph.pl"
        if not stackcollapse.exists() or not flamegraph.exists():
            append_log(self.settings.log_file, "official FlameGraph scripts not found; using fallback renderer")
            return False

        try:
            with folded_file.open("w", encoding="utf-8") as folded:
                collapse_result = subprocess.run(
                    ["perl", str(stackcollapse), str(perf_script_file)],
                    stdout=folded,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False,
                )
            if collapse_result.returncode != 0:
                append_log(self.settings.log_file, "stackcollapse failed: " + collapse_result.stderr.strip())
                return False

            with folded_file.open("r", encoding="utf-8", errors="replace") as folded:
                with svg_file.open("w", encoding="utf-8") as svg:
                    flame_result = subprocess.run(
                        [
                            "perl",
                            str(flamegraph),
                            "--title",
                            f"CPU FlameGraph {start} - {end}",
                        ],
                        stdin=folded,
                        stdout=svg,
                        stderr=subprocess.PIPE,
                        text=True,
                        check=False,
                    )
            if flame_result.returncode != 0:
                append_log(self.settings.log_file, "flamegraph.pl failed: " + flame_result.stderr.strip())
                return False
            return True
        except OSError as exc:
            append_log(self.settings.log_file, f"official FlameGraph execution failed: {exc}")
            return False


def collapse_perf_script(perf_script_file: Path) -> Counter:
    stacks: Counter = Counter()
    frames: List[str] = []

    with perf_script_file.open("r", encoding="utf-8", errors="replace") as handle:
        for raw_line in handle:
            line = raw_line.rstrip("\n")
            if not line.strip():
                if frames:
                    stacks[";".join(reversed(frames))] += 1
                    frames = []
                continue

            if line.startswith("\t") or line.startswith(" "):
                frame = _extract_frame_name(line)
                if frame:
                    frames.append(frame)

    if frames:
        stacks[";".join(reversed(frames))] += 1

    return stacks


def _extract_frame_name(line: str) -> str:
    text = line.strip()
    if not text:
        return ""

    parts = text.split()
    if len(parts) >= 2 and all(ch in "0123456789abcdefABCDEF" for ch in parts[0]):
        symbol = parts[1]
    else:
        symbol = parts[0]

    symbol = symbol.split("+", 1)[0]
    return symbol[:120]


class _Node(defaultdict):
    def __init__(self) -> None:
        super().__init__(_Node)
        self.value = 0


def _build_tree(stacks: Counter) -> _Node:
    root = _Node()
    for stack, count in stacks.items():
        node = root
        node.value += count
        for frame in stack.split(";"):
            node = node[frame]
            node.value += count
    return root


def render_fallback_svg(stacks: Counter, output_file: Path, title: str) -> None:
    width = 1200
    frame_height = 18
    padding_top = 42
    padding_bottom = 30
    root = _build_tree(stacks)
    max_depth = _tree_depth(root)
    height = padding_top + padding_bottom + (max_depth + 1) * frame_height
    total = max(root.value, 1)

    rects: List[str] = []
    _render_node_children(root, 0, padding_top, width, frame_height, total, rects)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(
        "\n".join(
            [
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
                "<style>",
                "text{font-family:Arial,sans-serif;font-size:12px;fill:#111827}",
                ".frame:hover{stroke:#111827;stroke-width:1.5}",
                "</style>",
                f'<text x="16" y="24" font-size="17" font-weight="700">{html.escape(title)}</text>',
                *rects,
                "</svg>",
            ]
        ),
        encoding="utf-8",
    )


def _tree_depth(node: _Node) -> int:
    if not node:
        return 0
    return 1 + max(_tree_depth(child) for child in node.values())


def _render_node_children(
    node: _Node,
    x: float,
    y: float,
    width: float,
    frame_height: int,
    total: int,
    rects: List[str],
) -> None:
    cursor = x
    children: Dict[str, _Node] = dict(sorted(node.items(), key=lambda item: item[1].value, reverse=True))
    for name, child in children.items():
        child_width = width * child.value / max(node.value, 1)
        if child_width < 0.5:
            continue

        color = _color_for(name)
        pct = child.value * 100 / total
        safe_name = html.escape(name)
        label = safe_name if child_width > 80 else ""
        rects.append(
            f'<g class="frame"><title>{safe_name} ({child.value} samples, {pct:.2f}%)</title>'
            f'<rect x="{cursor:.2f}" y="{y:.2f}" width="{child_width:.2f}" height="{frame_height - 1}" '
            f'fill="{color}" rx="1" ry="1"/>'
            f'<text x="{cursor + 3:.2f}" y="{y + 13:.2f}">{label}</text></g>'
        )
        _render_node_children(child, cursor, y + frame_height, child_width, frame_height, total, rects)
        cursor += child_width


def _color_for(name: str) -> str:
    value = sum(ord(ch) for ch in name)
    hue = 24 + value % 44
    saturation = 72 + value % 18
    lightness = 62 + value % 12
    return f"hsl({hue},{saturation}%,{lightness}%)"

