#!/usr/bin/env bash
set -euo pipefail

mkdir -p resume
mkdir -p task1/1-perf-stat/results
mkdir -p task1/2-flamegraph/flamegraphs
mkdir -p task1/3-cache-line-test/src
mkdir -p task1/3-cache-line-test/results
mkdir -p task1/3-cache-line-test/flamegraphs
mkdir -p task1/3-cache-line-test/figures
mkdir -p task1/3-cache-line-test/ai-chat-log
mkdir -p task2/src task2/test/screenshots task2/ai-chat-log

cat > .gitignore <<'EOF'
*.o
*.tmp
.DS_Store
__pycache__/
EOF

cat > README.md <<'EOF'
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
EOF

cat > resume/README.md <<'EOF'
# Resume

请在提交前将个人简历命名为 `resume.pdf` 并放入本目录。
EOF

cat > task1/1-perf-stat/README.md <<'EOF'
# 1-perf-stat 多场景微架构指标采集

## 环境准备

```bash
export PERF_BIN=/usr/lib/linux-tools/6.8.0-124-generic/perf
sudo sysctl -w kernel.perf_event_paranoid=1
sudo sysctl -w kernel.kptr_restrict=0
```

## 环境信息采集

```bash
lscpu > results/lscpu.txt
uname -a > results/uname.txt
numactl --hardware > results/numa.txt
systemd-detect-virt > results/virt.txt
cpupower frequency-info > results/cpupower.txt 2>&1
```

## 五类负载

```bash
sudo $PERF_BIN stat -e cycles,instructions,cache-references,cache-misses,L1-dcache-load-misses,L1-icache-load-misses,LLC-load-misses,branch-instructions,branch-misses,dTLB-load-misses,context-switches,cpu-migrations -o results/int64.txt -- stress-ng --cpu 1 --cpu-method int64 -t 30s
sudo $PERF_BIN stat -e cycles,instructions,cache-references,cache-misses,L1-dcache-load-misses,L1-icache-load-misses,LLC-load-misses,branch-instructions,branch-misses,dTLB-load-misses,context-switches,cpu-migrations -o results/matrixprod.txt -- stress-ng --cpu 1 --cpu-method matrixprod -t 30s
sudo $PERF_BIN stat -e cycles,instructions,cache-references,cache-misses,L1-dcache-load-misses,L1-icache-load-misses,LLC-load-misses,branch-instructions,branch-misses,dTLB-load-misses,context-switches,cpu-migrations -o results/read64.txt -- stress-ng --vm 1 --vm-bytes 1G --vm-method read64 --vm-keep -t 30s
sudo $PERF_BIN stat -e cycles,instructions,cache-references,cache-misses,L1-dcache-load-misses,L1-icache-load-misses,LLC-load-misses,branch-instructions,branch-misses,dTLB-load-misses,context-switches,cpu-migrations -o results/rand-set.txt -- stress-ng --vm 1 --vm-bytes 512M --vm-method rand-set --vm-keep -t 30s
sudo $PERF_BIN stat -e cycles,instructions,cache-references,cache-misses,L1-dcache-load-misses,L1-icache-load-misses,LLC-load-misses,branch-instructions,branch-misses,dTLB-load-misses,context-switches,cpu-migrations -o results/queens.txt -- stress-ng --cpu 1 --cpu-method queens -t 30s
```

原始输出保存在 `results/` 目录。
EOF

cat > task1/1-perf-stat/report.md <<'EOF'
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
EOF

cat > task1/2-flamegraph/README.md <<'EOF'
# 2-flamegraph 火焰图生成

## 依赖

```bash
git clone https://github.com/brendangregg/FlameGraph.git ~/FlameGraph
export PERF_BIN=/usr/lib/linux-tools/6.8.0-124-generic/perf
```

## matrixprod 火焰图

```bash
sudo $PERF_BIN record -F 99 -g -o matrixprod.perf.data -- stress-ng --cpu 1 --cpu-method matrixprod -t 30s
sudo $PERF_BIN script -i matrixprod.perf.data > matrixprod.perf
~/FlameGraph/stackcollapse-perf.pl matrixprod.perf | ~/FlameGraph/flamegraph.pl > flamegraphs/matrixprod_flame.svg
```

## rand-set 火焰图

```bash
sudo $PERF_BIN record -F 99 -g -o rand-set.perf.data -- stress-ng --vm 1 --vm-bytes 512M --vm-method rand-set --vm-keep -t 30s
sudo $PERF_BIN script -i rand-set.perf.data > rand-set.perf
~/FlameGraph/stackcollapse-perf.pl rand-set.perf | ~/FlameGraph/flamegraph.pl > flamegraphs/rand_set_flame.svg
```

火焰图文件位于 `flamegraphs/`。
EOF

cat > task1/2-flamegraph/report.md <<'EOF'
# 火焰图热点分析报告

## 1. 生成结果

matrixprod 火焰图：

![matrixprod flamegraph](flamegraphs/matrixprod_flame.svg)

rand-set 火焰图：

![rand-set flamegraph](flamegraphs/rand_set_flame.svg)

## 2. matrixprod 负载分析

`matrixprod` 是矩阵乘法类计算负载，CPU 时间主要集中在 stress-ng 的矩阵计算路径中。火焰图整体更接近热点集中的形态，说明程序大部分时间在重复执行稳定的计算循环。

该负载的分支预测失败率较低，说明分支不是主要瓶颈。结合 perf stat 中 IPC 约为 1.00、L1 DCache Miss Rate 较高的现象，可以判断其压力主要来自计算循环中的数据访问和执行单元利用。

## 3. rand-set 负载分析

`rand-set` 是随机访存型负载，访问地址更分散，空间局部性弱。火焰图相比 matrixprod 更容易出现分散的栈形态，说明 CPU 时间不仅消耗在用户态访问循环中，也可能受缺页、页表访问和内存管理路径影响。

结合 perf stat 结果，rand-set 的 L1 DCache Miss Rate 达到 48.84%，明显高于 read64，说明随机访问破坏了缓存局部性，硬件预取器难以提前加载后续数据。

## 4. 对比结论

计算密集型负载的热点更集中，访存随机性强的负载热点更分散。若火焰图中出现 `__do_page_fault`、`copy_page` 等内核态函数，通常说明访问过程中触发了缺页、页表处理或内存页初始化，这些路径会增加访存延迟并降低整体吞吐。

本实验运行在 WSL2 虚拟化环境中，内核态栈和部分硬件事件可能受虚拟化层影响，因此分析时同时参考 perf stat 和火焰图趋势。
EOF

cat > task1/3-cache-line-test/README.md <<'EOF'
# 3-cache-line-test Cache Line 微基准测试

## 编译

```bash
gcc -Wall -Wextra -O2 -march=native -o cache_line_test src/cache_line_test.c
```

## 运行性能测试

```bash
./cache_line_test > results/performance.csv
```

## 采集各 stride 的 perf stat

```bash
export PERF_BIN=/usr/lib/linux-tools/6.8.0-124-generic/perf
for s in 1 2 4 8 16 32 64 128 256; do
  sudo $PERF_BIN stat -e L1-dcache-load-misses,cache-misses,dTLB-load-misses \
  -o results/stride_${s}_perf.txt \
  -- ./cache_line_test $s
done
```

## 生成曲线图

```bash
python3 plot_stride.py
```

生成图片：

- `figures/stride_latency.png`
- `figures/stride_throughput.png`

## 生成 stride 火焰图

```bash
sudo $PERF_BIN record -F 99 -g -o stride1.perf.data -- ./cache_line_test 1
sudo $PERF_BIN script -i stride1.perf.data > stride1.perf
~/FlameGraph/stackcollapse-perf.pl stride1.perf | ~/FlameGraph/flamegraph.pl > flamegraphs/stride1.svg

sudo $PERF_BIN record -F 99 -g -o stride64.perf.data -- ./cache_line_test 64
sudo $PERF_BIN script -i stride64.perf.data > stride64.perf
~/FlameGraph/stackcollapse-perf.pl stride64.perf | ~/FlameGraph/flamegraph.pl > flamegraphs/stride64.svg
```
EOF

cat > task1/3-cache-line-test/report.md <<'EOF'
# Cache Line 微基准测试报告

## 1. 程序设计

本实验编写 C 程序 `src/cache_line_test.c`，申请 256MB 数组，并以不同步长遍历数组。测试步长为 1、2、4、8、16、32、64、128、256 字节。程序记录每种步长下的总访问次数、运行时间、平均访问延迟和吞吐量。

数组使用 64B 对齐分配，减少非对齐访问对结果的影响。循环中使用 `volatile` 累加变量，避免编译器将访存循环优化掉。

## 2. 性能数据

| stride(bytes) | accesses | time(s) | ns/access | throughput(MB/s) |
|---:|---:|---:|---:|---:|
| 1 | 2147483648 | 0.651570 | 0.303 | 3143.18 |
| 2 | 1073741824 | 0.340348 | 0.317 | 3008.69 |
| 4 | 536870912 | 0.223969 | 0.417 | 2286.03 |
| 8 | 268435456 | 0.102810 | 0.383 | 2490.04 |
| 16 | 134217728 | 0.065472 | 0.488 | 1955.02 |
| 32 | 67108864 | 0.055839 | 0.832 | 1146.15 |
| 64 | 33554432 | 0.052232 | 1.557 | 612.66 |
| 128 | 16777216 | 0.073566 | 4.385 | 217.49 |
| 256 | 8388608 | 0.041878 | 4.992 | 191.03 |

原始数据保存在 `results/performance.csv`。

## 3. 曲线图

延迟曲线：

![stride latency](figures/stride_latency.png)

吞吐量曲线：

![stride throughput](figures/stride_throughput.png)

## 4. Cache Line 拐点分析

实验结果显示，在 stride=1B 到 32B 之间，平均访问延迟从 0.303 ns/access 上升到 0.832 ns/access，增长较缓；当 stride 达到 64B 时，延迟上升到 1.557 ns/access；当 stride 增加到 128B 和 256B 时，延迟进一步升高到 4.385 和 4.992 ns/access。

吞吐量也呈现对应下降趋势：stride=1B 时约 3143 MB/s，stride=64B 时下降到约 613 MB/s，stride=128B 后下降到约 200 MB/s。该趋势说明，当访问步长接近或超过典型 x86 CPU 的 64B cache line 大小时，每次访问更可能触发新的 cache line 加载，空间局部性下降，访存层级开销显著增加。

由于实验运行在 WSL2 虚拟化环境中，个别点存在小幅波动，但整体趋势清晰，不影响 64B cache line 拐点结论。

## 5. perf stat 与火焰图

各 stride 的 perf stat 原始输出保存在 `results/stride_*_perf.txt`。

火焰图文件：

- `flamegraphs/stride1.svg`
- `flamegraphs/stride64.svg`

`stride=1` 时，连续访问具有较好的空间局部性，一次 cache line 加载可以服务多个后续访问。`stride=64` 时，每次访问更容易落到新的 cache line，cache line 利用率下降，因此平均访问延迟上升、吞吐量下降。

## 6. AI 辅助说明

本实验使用 AI 工具辅助完成需求拆解、WSL2 perf 问题排查、C 程序编写、编译 warning 修复、性能曲线生成和报告分析。相关记录保存在 `ai-chat-log/`。
EOF

cat > task1/3-cache-line-test/ai-chat-log/chat-summary.md <<'EOF'
# AI 辅助记录摘要

本实验使用 ChatGPT/Codex 辅助完成以下工作：

1. 拆解 CVM 考题要求，确定仓库目录结构和完成顺序。
2. 排查 WSL2 中 `perf` 与内核版本不匹配问题，最终使用 `/usr/lib/linux-tools/6.8.0-124-generic/perf` 完成采集。
3. 编写 `cache_line_test.c`，用于测试不同 stride 对数组遍历性能的影响。
4. 修复 `CLOCK_MONOTONIC` 与 `posix_memalign` 相关编译问题。
5. 生成 stride 性能曲线图和 stride=1、stride=64 火焰图。
6. 辅助整理 perf stat、火焰图和 Cache Line 拐点分析。

完整对话截图可在提交前继续补充到本目录。
EOF

cat > task2/README.md <<'EOF'
# 题目 2：持续 CPU Profiling 工具

本题为选做加分项。本次提交主要完成题目 1 的必做内容，题目 2 暂未实现。

若后续继续扩展，计划采用以下方案：

- 后端：Python Flask
- 采集：后台调用 `perf record`
- 轮转：按固定时间窗口保存 perf.data
- 火焰图：调用 FlameGraph 工具链生成 SVG
- 容器化：Dockerfile + `--privileged` 模式运行
- 前端：HTML/JS 展示采集状态、时间线和火焰图
EOF

echo "Repository content files generated."
