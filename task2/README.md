# 题目 2：持续 CPU Profiling 工具

本目录实现了一个容器化的持续 CPU Profiling 工具，用于完成 CVM 加分题。工具会在后台按固定时间窗口持续运行 `perf record`，保存历史采样数据；当需要复盘某个时间段的 CPU 异常时，可以输入起止时间，自动定位对应采样文件并生成 SVG 火焰图。

## 架构设计

```text
Docker 容器
  -> profiler.collector
     -> perf record -F 99 -e cpu-clock -a -g -- sleep <window>
     -> data/samples/*.perf.data
     -> data/index.jsonl
  -> profiler.storage
     -> 按时间段查询采样窗口
     -> 清理超过保留时间的历史数据
  -> profiler.flamegraph
     -> perf script
     -> FlameGraph stackcollapse/flamegraph 脚本
     -> data/flamegraphs/*.svg
  -> profiler.server
     -> 8080 端口提供 Web 页面和 JSON API
  -> profiler.cli
     -> 提供 status / list / flamegraph 等命令行操作
```

生成火焰图时会优先使用 Brendan Gregg 的 FlameGraph 工具链。如果容器中没有 FlameGraph 脚本，程序会退回到内置的简化 SVG 渲染器，保证回查流程仍然可用。

## 快速启动

构建镜像：

```bash
cd task2
docker build -t cpu-profiler ./src
```

启动 profiler 容器：

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

浏览器访问：

```text
http://localhost:8080
```

如果只是快速测试，可以缩短采样窗口：

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

## 从导出的镜像启动

本地导出镜像：

```bash
docker save cpu-profiler -o profiler.tar
```

由于 `profiler.tar` 约 158MB，超过 GitHub 普通文件 100MB 限制，已上传到 GitHub Release 附件：

[下载 profiler.tar](https://github.com/defu117/2026CVM-kaohe-luoweihong/releases/download/task2-profiler-v1/profiler.tar)

评审方可以通过以下方式加载并启动：

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

说明：

- `--privileged`：`perf` 需要访问内核 profiling 接口以及相关性能计数资源。
- `--pid=host`：用于系统级采样，便于 profiler 容器观察宿主 Docker 环境中的其他进程。
- `-v /etc/localtime:/etc/localtime:ro` 和 `TZ=Asia/Shanghai`：保证容器中的时间与 WSL/主机时间一致，便于按时间段回查。

## CLI 使用方式

在容器中查看状态：

```bash
docker exec -it cpu-profiler python3 -m profiler.cli status
```

列出最近 1 小时采样窗口：

```bash
docker exec -it cpu-profiler python3 -m profiler.cli list --hours 1
```

按时间段生成火焰图：

```bash
docker exec -it cpu-profiler python3 -m profiler.cli flamegraph \
  --from "2026-06-20 21:35:49" \
  --to "2026-06-20 21:37:31"
```

命令会输出生成的 SVG 路径，例如：

```text
/data/flamegraphs/flame_20260620_213549_20260620_213731.svg
```

## WSL 本地调试

推荐使用 Docker 方式验证。如果需要在 WSL 中直接调试 Web 服务，需要先安装 Flask：

```bash
sudo apt install -y python3-flask
cd task2/src
DATA_DIR=../data START_COLLECTOR=0 python3 -m profiler.server
```

然后访问：

```text
http://localhost:8080
```

如果要在 WSL 本地直接启动后台采集，需要将 `START_COLLECTOR=1`，并确保当前用户有足够的 `perf` 权限。

## Web API

```text
GET  /api/status
GET  /api/samples?hours=24
POST /api/flamegraph
GET  /flamegraphs/<svg-file>
```

示例：

```bash
curl -X POST http://localhost:8080/api/flamegraph \
  -H "Content-Type: application/json" \
  -d '{"start":"2026-06-20 21:35:49","end":"2026-06-20 21:37:31"}'
```

## CPU 飙升验证

本项目最终验证时使用 Docker 容器构造 CPU 飙升场景。这样 profiler 容器可以通过系统级采样捕获同一 Docker 环境中的压力负载。

```bash
date '+Start: %F %T'

docker run --rm --name cpu-spike \
  --entrypoint stress-ng \
  cpu-profiler \
  --cpu 2 --cpu-method matrixprod -t 90s

date '+End: %F %T'
```

记录开始和结束时间后，在 Web 页面中输入相同时间段并点击 `Generate FlameGraph`，或者使用 CLI：

```bash
docker exec cpu-profiler python3 -m profiler.cli flamegraph \
  --from "2026-06-20 21:35:49" \
  --to "2026-06-20 21:37:31"
```

验证成功的标志是：生成的火焰图中能看到 `stress-ng` / `stress-ng-cpu` 相关调用栈。

详细验证材料见：

```text
task2/test/README.md
task2/test/results/verification-summary.md
task2/test/screenshots/
```

## 重要环境变量

| 变量 | 默认值 | 说明 |
|---|---:|---|
| `WINDOW_SECONDS` | `60` | 每个 `perf record` 采样窗口的持续时间 |
| `RETENTION_HOURS` | `24` | 历史采样数据保留时长 |
| `SAMPLE_FREQ` | `99` | 传给 `perf record -F` 的采样频率 |
| `PERF_EVENT` | `cpu-clock` | `perf record -e` 使用的事件 |
| `PERF_SCOPE` | `system` | `system` 表示追加 `-a` 做系统级采样；`process` 表示仅采样 sleep 进程 |
| `DATA_DIR` | `/data` | 采样文件、索引和火焰图的根目录 |
| `FLAMEGRAPH_DIR` | `/opt/FlameGraph` | FlameGraph 脚本所在目录 |
| `TZ` | `Asia/Shanghai` | 采样窗口和 Web 页面使用的时区 |
| `START_COLLECTOR` | `1` | 设置为 `0` 时只启动 Web 服务，不启动后台采集 |

## 设计权衡

- 使用固定时间窗口保存采样数据，便于按时间段回查和自动清理。
- 使用文件系统和 `index.jsonl` 管理历史数据，避免引入数据库，结构更容易评审。
- 默认使用 `cpu-clock` 事件，比硬件 PMU 事件更适合 WSL / Docker Desktop 等虚拟化环境。
- 默认使用系统级采样，适合模拟线上服务故障复盘场景。
- 内置简化 SVG 渲染器只是兜底方案，正常情况下优先使用官方 FlameGraph 输出。
