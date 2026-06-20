# 2026CVM-kaohe-luoweihong

本仓库为 2026 CVM 竞品微架构性能测评 Mini 项目提交材料。

## 完成情况

| 模块 | 状态 | 说明 |
|---|---|---|
| 题目 1-1 多场景 perf stat | 已完成 | 已采集 int64、matrixprod、read64、rand-set、queens 五类负载 |
| 题目 1-2 火焰图分析 | 已完成 | 已生成 matrixprod 与 rand-set 火焰图 |
| 题目 1-3 Cache Line 微基准 | 已完成 | 已完成 C 程序、stride 性能数据、perf stat、火焰图和曲线图 |
| 题目 2 持续 CPU Profiling 工具 | 未完成 | 选做加分项，本次提交未实现 |

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
├── task1/
│   ├── 1-perf-stat/
│   ├── 2-flamegraph/
│   └── 3-cache-line-test/
└── task2/
```

## 快速查看

- 题目 1-1 报告：`task1/1-perf-stat/report.md`
- 题目 1-2 报告：`task1/2-flamegraph/report.md`
- 题目 1-3 报告：`task1/3-cache-line-test/report.md`

## 备注

`resume/resume.pdf` 需要提交前手动放入个人简历 PDF。
