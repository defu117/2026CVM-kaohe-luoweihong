# 题目 2 AI 辅助记录摘要

本题使用 AI 辅助设计并实现了一个容器化的持续 CPU Profiling 工具。

AI 主要辅助完成了以下工作：

1. 将题目 2 拆解为后台采集、历史存储、时间段回查、火焰图生成、CLI、Web 页面、Docker 容器化和测试验证几个模块。
2. 设计固定时间窗口的 `perf record` 持续采样方案。
3. 实现基于 `index.jsonl` 的采样窗口索引和过期数据清理逻辑。
4. 实现按起止时间回查历史 perf 采样文件。
5. 实现通过 FlameGraph 工具链自动生成 SVG 火焰图，并提供内置简化渲染器作为兜底。
6. 实现 Flask API 和 Web 页面，用于展示采集状态、历史窗口和火焰图。
7. 编写 Dockerfile、容器启动脚本和 `--privileged` 运行说明。
8. 设计并验证 Docker 内 `stress-ng` CPU 飙升测试场景。
9. 排查 Docker Desktop + WSL 环境中的时间差问题，并通过 `TZ=Asia/Shanghai` 和挂载 `/etc/localtime` 对齐容器时间。
10. 整理测试截图、SVG 火焰图和验证总结文档。

主要工程权衡：

- 使用文件存储而不是数据库，降低实现复杂度，也方便评审直接查看采样索引和生成结果。
- 默认使用 `cpu-clock` 事件，以提高在 WSL / Docker Desktop 等虚拟化环境中的兼容性。
- 使用系统级采样模式，便于模拟线上故障场景，但火焰图中也会包含 idle 栈，这是预期现象。

