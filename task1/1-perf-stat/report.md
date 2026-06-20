# CPU 微架构性能指标采集报告

## 1. 测试环境

本实验运行在 Ubuntu 24.04 on WSL2 环境中，内核为 `6.18.33.1-microsoft-standard-WSL2`。perf 工具使用 `/usr/lib/linux-tools/6.8.0-124-generic/perf`。

环境信息原始文件：

- `results/lscpu.txt`
- `results/uname.txt`
- `results/numa.txt`
- `results/virt.txt`
- `results/cpupower.txt`

由于 WSL2 环境缺少与当前 WSL 内核完全匹配的 `cpupower` 工具，CPU 频率策略无法完整读取，原始报错已保存到 `cpupower.txt`。

## 2. 原始 perf stat 输出

- 整数计算：`results/int64.txt`
- 矩阵计算：`results/matrixprod.txt`
- 连续访存：`results/read64.txt`
- 随机访存：`results/rand-set.txt`
- 分支密集：`results/queens.txt`

## 3. 衍生指标对比

| 负载 | IPC | L1 DCache Miss Rate | LLC Miss Rate | 分支预测失败率 | TLB Miss Rate |
|---|---:|---:|---:|---:|---:|
| int64 | 3.05 | 16.07% | N/A | 0.23% | 0.97% |
| matrixprod | 1.00 | 38.53% | N/A | 0.05% | 0.001% |
| read64 | 2.43 | 0.062% | N/A | 0.067% | 1.33% |
| rand-set | 4.76 | 48.84% | N/A | 0.026% | 0.79% |
| queens | 2.31 | 19.25% | N/A | 11.39% | 0.64% |

说明：WSL2 环境下 `LLC-load-misses` 显示为 `<not supported>`，因此 LLC Miss Rate 无法直接计算，表中记为 N/A。

## 4. 差异分析

`int64` 属于整数计算负载，IPC 约为 3.05，分支失败率仅 0.23%，说明流水线执行效率较高，主要压力不在分支预测。

`matrixprod` 的 IPC 约为 1.00，L1 DCache Miss Rate 达到 38.53%，但整体 cache-misses 比例较低，说明矩阵计算存在大量数据访问和复用，压力主要来自计算单元与 L1 数据缓存访问。

`read64` 是连续访存负载，IPC 约为 2.43，L1 DCache Miss Rate 很低，说明连续访问能较好利用硬件预取器。但 TLB Miss Rate 达到 1.33%，说明大内存区域访问带来了页表和 TLB 压力。

`rand-set` 是随机访存负载，L1 DCache Miss Rate 达到 48.84%，明显高于 read64，说明随机访问破坏了空间局部性，硬件预取器难以发挥作用。

`queens` 是分支密集型负载，分支预测失败率达到 11.39%，远高于其他负载，说明 N 皇后搜索中大量条件判断和回溯路径对分支预测器形成压力。
