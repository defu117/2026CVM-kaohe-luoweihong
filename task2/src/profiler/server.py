from __future__ import annotations

import os
from dataclasses import asdict
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from .collector import PerfCollector
from .config import ensure_directories, load_settings
from .flamegraph import FlameGraphError, FlameGraphGenerator
from .storage import Storage
from .timeutil import parse_time

settings = load_settings()
ensure_directories(settings)
storage = Storage(settings)
collector = PerfCollector(settings, storage)
generator = FlameGraphGenerator(settings, storage)
collector_autostart_enabled = settings.start_collector

static_dir = Path(__file__).resolve().parent.parent / "static"
app = Flask(__name__, static_folder=str(static_dir), static_url_path="/static")


@app.before_request
def _ensure_collector_started() -> None:
    if collector_autostart_enabled and not collector.running:
        collector.start()


@app.route("/")
def index():
    return send_from_directory(static_dir, "index.html")


@app.route("/api/status")
def api_status():
    status = storage.status()
    status.update(
        {
            "collector_running": collector.running,
            "collector_autostart_enabled": collector_autostart_enabled,
            "collector_last_error": collector.last_error,
            "collector_last_command": collector.last_command,
            "pid": os.getpid(),
        }
    )
    return jsonify(status)


@app.route("/api/samples")
def api_samples():
    hours = int(request.args.get("hours", "24"))
    samples = storage.recent_samples(hours)
    return jsonify([asdict(sample) for sample in samples])


@app.route("/api/flamegraph", methods=["POST"])
def api_flamegraph():
    payload = request.get_json(silent=True) or request.form
    try:
        start = parse_time(payload.get("start", ""))
        end = parse_time(payload.get("end", ""))
        result = generator.generate(start, end)
        return jsonify(result)
    except (ValueError, FlameGraphError) as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/collector/start", methods=["POST"])
def api_collector_start():
    global collector_autostart_enabled
    collector_autostart_enabled = True
    collector.start()
    return jsonify({"collector_running": collector.running})


@app.route("/api/collector/stop", methods=["POST"])
def api_collector_stop():
    global collector_autostart_enabled
    collector_autostart_enabled = False
    collector.stop()
    return jsonify({"collector_running": collector.running})


@app.route("/flamegraphs/<path:filename>")
def flamegraph_file(filename: str):
    return send_from_directory(settings.flamegraphs_dir, filename)


def main() -> None:
    if collector_autostart_enabled:
        collector.start()
    app.run(host=settings.host, port=settings.port, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
