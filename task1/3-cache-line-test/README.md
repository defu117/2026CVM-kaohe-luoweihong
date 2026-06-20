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
