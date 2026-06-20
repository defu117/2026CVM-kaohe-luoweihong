# 题目 2 验证总结

## 验证环境

- Profiler 镜像：`cpu-profiler`
- Profiler 容器：`cpu-profiler`
- Web 页面：`http://localhost:8080`
- 采集方式：系统级 `perf record`
- 时区：`Asia/Shanghai` / CST `+0800`

## CPU 飙升场景

为了让 profiler 容器能够采集到压力负载，本次 CPU 飙升场景也在 Docker 容器中构造。测试负载使用 `stress-ng` 的 `matrixprod` 方法，启动 2 个 CPU worker，持续运行 90 秒。

```bash
date '+Start: %F %T'

docker run --rm --name cpu-spike \
  --entrypoint stress-ng \
  cpu-profiler \
  --cpu 2 --cpu-method matrixprod -t 90s

date '+End: %F %T'
```

记录到的终端输出如下：

```text
Start: 2026-06-20 21:35:49
stress-ng: info:  [1] setting to a 1 min, 30 secs run per stressor
stress-ng: info:  [1] dispatching hogs: 2 cpu
stress-ng: info:  [1] passed: 2: cpu (2)
stress-ng: info:  [1] successful run completed in 1 min, 41.49 secs
End: 2026-06-20 21:37:31
```

## 按时间段回查

在 Web 页面中回查以下历史时间段：

```text
2026-06-20 21:35:49 ~ 2026-06-20 21:37:31
```

同样的回查操作也可以通过 CLI 复现：

```bash
docker exec cpu-profiler python3 -m profiler.cli flamegraph \
  --from "2026-06-20 21:35:49" \
  --to "2026-06-20 21:37:31"
```

生成的火焰图文件为：

```text
task2/test/results/cpu-spike-flamegraph.svg
```

## 验证结果

生成的火焰图中可以看到 `stress-ng` 和 `stress-ng-cpu` 相关调用栈，说明本工具成功完成了以下流程：

- 后台持续保存 CPU 采样数据；
- 根据指定时间段定位历史采样文件；
- 对 CPU 飙升时间段生成火焰图；
- 在故障结束后仍能回查当时的 CPU 热点。

火焰图中仍然可以看到 `do_idle` / `default_idle_call` 等 idle 调用栈，这是因为 profiler 使用的是系统级采样模式。系统中未被压力负载占满的 CPU 仍会处于 idle 状态，因此这些调用栈出现在火焰图中是合理的。

## Docker 镜像导出

本地已使用以下命令导出镜像：

```bash
docker save cpu-profiler -o task2/profiler.tar
```

导出的 `profiler.tar` 约为 158 MB，超过 GitHub 普通文件 100 MB 限制。因此该文件保留在本地，并已通过 `.gitignore` 忽略。如果评审需要预构建镜像 tar 包，应将其上传到 GitHub Release 附件中。

## 截图证据

- `../screenshots/01-profiler-running.png`
- `../screenshots/02-cpu-spike-terminal.png`
- `../screenshots/03-stress-ng-flamegraph.png`
