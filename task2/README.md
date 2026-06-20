# Task 2: Continuous CPU Profiling Tool

This directory contains a containerized continuous CPU profiling tool for the CVM extra-credit task. It keeps `perf record` running in fixed windows, stores historical samples, lets users query a time range, and generates an SVG flame graph.

## Architecture

```text
Docker container
  -> profiler.collector
     -> perf record -F 99 -e cpu-clock -a -g -- sleep <window>
     -> data/samples/*.perf.data
     -> data/index.jsonl
  -> profiler.storage
     -> query samples by time range
     -> clean samples older than retention window
  -> profiler.flamegraph
     -> perf script
     -> FlameGraph stackcollapse/flamegraph scripts
     -> data/flamegraphs/*.svg
  -> profiler.server
     -> Web UI and JSON API on port 8080
  -> profiler.cli
     -> command-line status/list/flamegraph operations
```

The official FlameGraph scripts are used when available. If they are missing, the tool falls back to a simple built-in SVG flame graph renderer so that the query flow remains usable.

## Quick Start

Build the image from source:

```bash
cd task2
docker build -t cpu-profiler ./src
```

Run the profiler:

```bash
docker run --privileged --pid=host -d \
  -p 8080:8080 \
  -v "$(pwd)/data:/data" \
  -v /etc/localtime:/etc/localtime:ro \
  -e TZ=Asia/Shanghai \
  -e WINDOW_SECONDS=60 \
  -e RETENTION_HOURS=24 \
  --name cpu-profiler \
  cpu-profiler
```

Open the Web UI:

```text
http://localhost:8080
```

For a quick test, use shorter windows:

```bash
docker run --privileged --pid=host -d \
  -p 8080:8080 \
  -v "$(pwd)/data:/data" \
  -v /etc/localtime:/etc/localtime:ro \
  -e TZ=Asia/Shanghai \
  -e WINDOW_SECONDS=10 \
  -e RETENTION_HOURS=1 \
  --name cpu-profiler \
  cpu-profiler
```

## Load From Exported Image

After exporting the image:

```bash
docker save cpu-profiler -o profiler.tar
```

The reviewer can run:

```bash
docker load -i profiler.tar
docker run --privileged --pid=host -d \
  -p 8080:8080 \
  -v "$(pwd)/data:/data" \
  -v /etc/localtime:/etc/localtime:ro \
  -e TZ=Asia/Shanghai \
  --name cpu-profiler \
  cpu-profiler
```

`--privileged` is required because `perf` needs access to kernel profiling interfaces and PMU-related resources. `--pid=host` helps system-wide profiling see processes outside the profiler container.

## CLI Usage

Run commands inside the container:

```bash
docker exec -it cpu-profiler python3 -m profiler.cli status
docker exec -it cpu-profiler python3 -m profiler.cli list --hours 1
docker exec -it cpu-profiler python3 -m profiler.cli flamegraph \
  --from "2026-06-20 03:00:00" \
  --to "2026-06-20 03:05:00"
```

The flame graph command prints the generated SVG path, for example:

```text
/data/flamegraphs/flame_20260620_030000_20260620_030500.svg
```

## Local WSL Run

Docker is the recommended verification path. If you want to run the Web server directly in WSL for debugging, install Flask first:

```bash
sudo apt install -y python3-flask
cd task2/src
DATA_DIR=../data START_COLLECTOR=0 python3 -m profiler.server
```

Then open:

```text
http://localhost:8080
```

Set `START_COLLECTOR=1` and run with sufficient `perf` permission when you want local background collection.

## Web API

```text
GET  /api/status
GET  /api/samples?hours=24
POST /api/flamegraph
GET  /flamegraphs/<svg-file>
```

Example:

```bash
curl -X POST http://localhost:8080/api/flamegraph \
  -H "Content-Type: application/json" \
  -d '{"start":"2026-06-20 03:00:00","end":"2026-06-20 03:05:00"}'
```

## CPU Spike Verification

1. Start the profiler container.
2. Wait until at least one sample window has been collected.
3. Run:

```bash
bash task2/test/test_scenario.sh
```

4. Record the printed start/end time.
5. Query that time range in the Web UI or CLI.
6. Check whether the flame graph contains `stress-ng` / matrix computation frames.

## Important Environment Variables

| Variable | Default | Description |
|---|---:|---|
| `WINDOW_SECONDS` | `60` | Duration of each `perf record` window |
| `RETENTION_HOURS` | `24` | How long historical samples are kept |
| `SAMPLE_FREQ` | `99` | Sampling frequency passed to `perf record -F` |
| `PERF_EVENT` | `cpu-clock` | Event used by `perf record -e` |
| `PERF_SCOPE` | `system` | `system` adds `-a`; `process` profiles only the sleep command |
| `DATA_DIR` | `/data` | Root directory for samples, index, and flame graphs |
| `FLAMEGRAPH_DIR` | `/opt/FlameGraph` | Directory containing FlameGraph scripts |
| `TZ` | `Asia/Shanghai` | Time zone used by sample windows and Web UI |
| `START_COLLECTOR` | `1` | Set to `0` to run the Web server without background collection |

## Design Tradeoffs

- Fixed time windows make lookup simple and predictable.
- File-based storage is easier to review than a database and is enough for a 24-hour retention window.
- `cpu-clock` is the default event because it works in more virtualized environments than hardware PMU events.
- The tool records system-wide samples by default, which is suitable for post-incident analysis.
- The fallback SVG renderer is intentionally simple; official FlameGraph output is preferred when the scripts are available.
