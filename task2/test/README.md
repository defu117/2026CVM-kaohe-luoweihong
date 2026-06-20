# 题目 2 验证材料

本目录用于保存题目 2 的测试验证材料，包括 CPU 飙升构造记录、按时间段回查生成的火焰图，以及验证过程总结。

## CPU 飙升场景

最终验证时使用单独的 Docker 容器构造 CPU 飙升场景。这样 `cpu-profiler` 容器可以通过系统级 `perf record` 采集到同一 Docker 环境中的压力负载。

```bash
date '+Start: %F %T'

docker run --rm --name cpu-spike \
  --entrypoint stress-ng \
  cpu-profiler \
  --cpu 2 --cpu-method matrixprod -t 90s

date '+End: %F %T'
```

记录到的测试时间段为：

```text
Start: 2026-06-20 21:35:49
End:   2026-06-20 21:37:31
```

## 验证文件说明

- `screenshots/01-profiler-running.png`：Web 页面显示持续采集器正在运行。
- `screenshots/02-cpu-spike-terminal.png`：终端中构造 CPU 飙升场景的命令和输出。
- `screenshots/03-stress-ng-flamegraph.png`：回查 CPU 飙升时间段后生成的火焰图截图。
- `results/cpu-spike-flamegraph.svg`：生成的 SVG 火焰图原文件。
- `results/verification-summary.md`：验证过程和结果总结。

预期结果是：回查指定时间段后生成的火焰图中可以看到 `stress-ng` / `stress-ng-cpu` 相关调用栈。
