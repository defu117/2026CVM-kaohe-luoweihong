# AI 辅助记录摘要

本实验使用 ChatGPT/Codex 辅助完成以下工作：

1. 拆解 CVM 考题要求，确定仓库目录结构和完成顺序。
2. 排查 WSL2 中 `perf` 与内核版本不匹配问题，最终使用 `/usr/lib/linux-tools/6.8.0-124-generic/perf` 完成采集。
3. 编写 `cache_line_test.c`，用于测试不同 stride 对数组遍历性能的影响。
4. 修复 `CLOCK_MONOTONIC` 与 `posix_memalign` 相关编译问题。
5. 生成 stride 性能曲线图和 stride=1、stride=64 火焰图。
6. 辅助整理 perf stat、火焰图和 Cache Line 拐点分析。

