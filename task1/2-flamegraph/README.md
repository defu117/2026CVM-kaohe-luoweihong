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
