# 2026CVM-kaohe-luoweihong

本仓库为 2026 CVM 竞品微架构性能测评 Mini 项目提交材料。

## 完成情况

| 模块 | 状态 | 说明 |
|---|---|---|
| 题目 1-1 多场景 perf stat | 已完成 | 已采集 int64、matrixprod、read64、rand-set、queens 五类负载 |
| 题目 1-2 火焰图分析 | 已完成 | 已生成 matrixprod 与 rand-set 火焰图 |
| 题目 1-3 Cache Line 微基准 | 已完成 | 已完成 C 程序、stride 性能数据、perf stat、火焰图和曲线图 |
| 题目 2 持续 CPU Profiling 工具 | 已完成 | 已实现 Docker 化持续采集、按时间段回查、Web 页面、CLI 和 stress-ng 验证 |

## 测试环境

- 系统环境：Ubuntu 24.04 on WSL2
- WSL2 内核：`6.18.33.1-microsoft-standard-WSL2`
- 编译器：GCC 13.3.0
- 压测工具：stress-ng 0.17.06
- perf 工具：`/usr/lib/linux-tools/6.8.0-124-generic/perf`

说明：由于实验环境为 WSL2，`LLC-load-misses` 事件显示为 `<not supported>`，因此报告中 LLC Miss Rate 记为 N/A。

## 仓库结构

```text
.
├── README.md
├── resume/
│   └── README.md
├── task1/
│   ├── 1-perf-stat/              # perf stat 数据、README、report.md/report.pdf
│   ├── 2-flamegraph/             # FlameGraph SVG、README、report.md/report.pdf
│   └── 3-cache-line-test/        # C 源码、结果、图表、火焰图、AI 记录、report.md/report.pdf
├── task2/
│   ├── README.md                 # 持续 CPU Profiling 工具说明
│   ├── src/                      # Dockerfile、后端、前端源码
│   ├── test/                     # 验证脚本、截图、最终 SVG 火焰图
│   └── ai-chat-log/              # AI 辅助记录
└── .gitignore
```

## 快速查看

- 题目 1-1 报告：`task1/1-perf-stat/report.md` / `task1/1-perf-stat/report.pdf`
- 题目 1-2 报告：`task1/2-flamegraph/report.md` / `task1/2-flamegraph/report.pdf`
- 题目 1-3 报告：`task1/3-cache-line-test/report.md` / `task1/3-cache-line-test/report.pdf`
- 题目 2 工具说明：`task2/README.md`
- 题目 2 验证总结：`task2/test/results/verification-summary.md`
- 题目 2 AI 记录：`task2/ai-chat-log/ai-chat-export-task2.md`

## 备注

`resume/resume.pdf` 需要提交前手动放入个人简历 PDF。

`task2/profiler.tar` 已在本地通过 `docker save` 导出，但大小约 158MB，超过 GitHub 普通文件 100MB 限制，因此不直接提交到 Git 仓库。如评审需要预构建镜像 tar 包，应上传到 GitHub Release 附件。
