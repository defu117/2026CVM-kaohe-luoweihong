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
