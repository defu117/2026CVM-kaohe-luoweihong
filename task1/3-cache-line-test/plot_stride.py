import pandas as pd
import matplotlib.pyplot as plt

csv_path = "task1/3-cache-line-test/results/performance.csv"
df = pd.read_csv(csv_path)

plt.figure(figsize=(8, 5))
plt.plot(df["stride_bytes"], df["ns_per_access"], marker="o", linewidth=2)
plt.axvline(x=64, color="red", linestyle="--", label="64B cache line")
plt.xscale("log", base=2)
plt.xlabel("Stride (bytes)")
plt.ylabel("Average latency (ns/access)")
plt.title("Stride vs Memory Access Latency")
plt.grid(True, which="both", linestyle="--", alpha=0.5)
plt.legend()
plt.tight_layout()
plt.savefig("task1/3-cache-line-test/figures/stride_latency.png", dpi=200)

plt.figure(figsize=(8, 5))
plt.plot(df["stride_bytes"], df["throughput_MB_s"], marker="o", linewidth=2)
plt.axvline(x=64, color="red", linestyle="--", label="64B cache line")
plt.xscale("log", base=2)
plt.xlabel("Stride (bytes)")
plt.ylabel("Throughput (MB/s)")
plt.title("Stride vs Memory Access Throughput")
plt.grid(True, which="both", linestyle="--", alpha=0.5)
plt.legend()
plt.tight_layout()
plt.savefig("task1/3-cache-line-test/figures/stride_throughput.png", dpi=200)
