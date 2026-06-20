# 2026 CVM 竞品微架构性能测评 — 校企合作 Mini 项目考核题

---

## 考核题目 1：CPU 微架构性能指标采集、火焰图分析与瓶颈定位

请在你的个人 PC、虚拟机或云服务器（推荐 Linux x86_64 环境）上完成以下任务。

---

### 一、多场景微架构指标采集（必做）

使用 Linux `perf stat` 工具，针对以下 **五类典型负载** 分别采集微架构关键指标：

| 序号 | 负载类型 | 测试命令 | 说明 |
|------|----------|----------|------|
| ① | **纯计算（整数）** | `stress-ng --cpu 1 --cpu-method int64 -t 30s` | 64位整数运算，考察ALU流水线效率 |
| ② | **纯计算（浮点/矩阵）** | `stress-ng --cpu 1 --cpu-method matrixprod -t 30s` | 矩阵乘法，考察浮点单元与SIMD利用率 |
| ③ | **访存密集型** | `stress-ng --vm 1 --vm-bytes 1G --vm-method read64 --vm-keep -t 30s` | 大块内存连续读取，考察Cache层级与内存带宽 |
| ④ | **随机访存型** | `stress-ng --vm 1 --vm-bytes 512M --vm-method rand-set -t 30s` | 随机内存访问，考察TLB与Cache Miss表现 |
| ⑤ | **分支密集型** | `stress-ng --cpu 1 --cpu-method queens -t 30s` | N-皇后问题，大量条件分支，考察分支预测器能力 |

> **注**：若你的环境不支持某个 `--cpu-method` 或 `--vm-method`，可运行 `stress-ng --cpu-method list` / `stress-ng --vm-method list` 查看可用方法，选择功能最接近的替代，并在报告中说明。

**每种负载需采集的 perf 指标至少包括：**

```bash
perf stat -e cycles,instructions,cache-references,cache-misses,\
L1-dcache-load-misses,L1-icache-load-misses,LLC-load-misses,\
branch-instructions,branch-misses,dTLB-load-misses,\
context-switches,cpu-migrations \
-- <测试命令>
```

**你需要：**

- **a. 环境记录**：记录完整的测试环境信息，包括但不限于：
  - CPU 型号、微架构代号（如 Cascade Lake / Zen 4 / Neoverse V2 等）
  - 内核版本、虚拟化类型（物理机 / KVM / Xen / 容器等）
  - NUMA 拓扑（`numactl --hardware`）、CPU 频率策略（`cpupower frequency-info`）
  - 记录 `perf stat` 的**完整原始输出**

- **b. 五场景横向对比**：将五种负载的指标结果汇总为**对比表格**，至少包含以下衍生指标：

  | 衍生指标 | 计算方式 |
  |----------|----------|
  | IPC（每周期指令数） | instructions / cycles |
  | L1 DCache Miss Rate | L1-dcache-load-misses / cache-references |
  | LLC Miss Rate | LLC-load-misses / cache-references |
  | 分支预测失败率 | branch-misses / branch-instructions |
  | TLB Miss Rate | dTLB-load-misses / cache-references |

- **c. 差异分析**：结合 CPU 微架构流水线原理（前端取指/解码、后端执行单元、访存子系统）进行分析：

---

### 二、火焰图生成与热点分析（必做）

使用 `perf record` + [FlameGraph](https://github.com/brendangregg/FlameGraph) 工具链，对上述 **五类负载中任选至少 2 种**，生成 CPU 火焰图并进行分析。

**操作步骤参考（仅供参考）：**

```bash
# 1. 采集性能数据（以矩阵乘法为例）
perf record -F 99 -g -- stress-ng --cpu 1 --cpu-method matrixprod -t 30s

# 2. 导出采样数据
perf script > perf_matrixprod.data

# 3. 生成火焰图（需提前 clone FlameGraph 仓库）
git clone https://github.com/brendangregg/FlameGraph.git
./FlameGraph/stackcollapse-perf.pl perf_matrixprod.data | \
./FlameGraph/flamegraph.pl > matrixprod_flame.svg
```

**你需要：**

- **a.** 在报告中嵌入生成的火焰图（SVG 或截图），并标注**热点函数**（占比最大的函数栈）。
- **b.** 对比两种不同负载的火焰图，分析：
  - 火焰图的"宽度"分布有何差异？哪些函数/系统调用占据了主要 CPU 时间？
  - 计算密集型负载的火焰图是否呈现"尖塔"形态（热点集中）？访存/分支密集型是否更"扁平"（热点分散）？为什么？
- **c.** 如果火焰图中出现了**内核态函数**（如 `__do_page_fault`、`copy_page` 等），请解释它们出现的原因及其对性能的影响。

---

### 三、AI 辅助编写自定义微基准测试（必做）

借助 AI 辅助编程工具（如 CodeBuddy / ChatGPT / Copilot），编写一段 C 语言程序，验证 **CPU Cache Line 大小对数组遍历性能的影响**。

**具体要求：**

1. 程序以不同步长（stride = 1, 2, 4, 8, 16, 32, 64, 128, 256 字节）遍历一个大数组（≥16MB），记录每种步长下的平均访问延迟或吞吐量。
2. 使用 `perf stat` 采集各步长下的 `L1-dcache-load-misses` 和 `LLC-load-misses` 指标。
3. 使用 `perf record -g` 对其中**至少 2 个步长**（如 stride=1 和 stride=64）生成火焰图，对比二者在 Cache Miss 处理路径上的差异。
4. 绘制 **"步长 vs 性能"曲线图**，标注 Cache Line 边界拐点，并解释拐点产生的微架构原因。
5. 在文档中说明你如何使用 AI 工具辅助完成代码编写与问题排查（附截图或对话记录）。

---



---

## 考核题目 2（选做加分题）：AI 编程挑战 — 构建 Linux 持续 CPU Profiling 工具

> **本题为加分项**，完成后可获得额外加分。本题重点考察 AI 辅助编程能力、Docker 工程化能力和系统性能工具链的综合运用。

---

### 背景故事

你所在团队负责一个高并发在线服务。最近连续发生了几次凌晨 CPU 飙升的故障，值班同学赶到时进程已恢复正常，`perf top` 看到的全是平时的调用栈，完全没有故障现场。

复盘会上大家只能靠猜——"可能是大量删表"、"可能是 GC"、"可能是锁竞争"……

团队决定：开发一个 **7×24 持续 CPU Profiling 的采集工具**，让 perf 像"黑匣子"一样常驻后台运行，出问题时只需指定时间点，就能调出当时的 CPU 采样数据，生成火焰图定位根因。

---

### 你的任务

借助 AI 编程工具（CodeBuddy / ChatGPT / Copilot 等），在个人电脑上搭建 Linux 虚拟机环境，开发一个**容器化的持续 CPU Profiling 工具**，满足以下功能需求：

#### 一、核心功能（必须实现）

| 功能 | 说明 |
|------|------|
| **后台持续采集** | 使用 `perf record` 在后台持续采集 CPU 调用栈数据，按固定时间窗口（如每 1 分钟）自动轮转保存采样文件 |
| **历史数据保留** | 采样数据按时间戳命名并保留最近 N 小时（默认 24h），自动清理过期数据，避免磁盘爆满 |
| **按时间回查** | 提供命令行接口或 API，输入时间段（如 `2026-06-11 03:00 ~ 03:05`），自动定位对应的采样文件 |
| **一键生成火焰图** | 对指定时间段的采样数据，自动调用 FlameGraph 工具链生成 SVG 火焰图 |

#### 二、工程化要求（必须满足）

| 要求 | 说明 |
|------|------|
| **Docker 容器化** | 整个工具封装为 Docker 镜像，导出为 `.tar` 包上传到 GitHub 仓库，评审方 `git clone` 后执行 `docker load` + `docker run` 即可一键启动 |
| **特权模式运行** | 容器需以 `--privileged` 模式运行（perf 需要访问宿主机内核的 PMU），在 README 中明确说明 |
| **GitHub 仓库** | 代码托管在 GitHub 公开仓库，包含完整的 git 提交历史（体现开发过程） |
| **README 文档** | 包含：项目简介、架构设计说明、快速启动命令、使用示例、设计权衡说明 |

#### 三、前端界面（有前端加更多分）

推荐但不强制实现一个 **Web 前端界面**，功能建议：

- 时间线视图：展示过去 N 小时的采集时间线，可点击选择时间段
- 火焰图展示：在浏览器中直接渲染 SVG 火焰图，支持交互式缩放/搜索
- 系统概览：展示当前 CPU 使用率、采集状态、磁盘占用等基本信息

> **技术选型建议**：前端可用 React / Vue / 纯 HTML+JS 均可；后端可用 Python Flask / Go Gin / Node.js 等；火焰图渲染可直接嵌入 SVG 或使用 [d3-flame-graph](https://github.com/nickolay/d3-flame-graph) 库。

#### 四、测试验证（必须包含）

你需要在虚拟机中**构造一个可复现的 CPU 飙升场景**来验证工具的有效性：

```bash
# 示例：用 stress-ng 模拟凌晨3点的CPU飙升
# 先启动 profiling 工具容器，然后在宿主机/另一个容器中：
stress-ng --cpu 2 --cpu-method matrixprod -t 60s   # 模拟60秒CPU飙升
# 等待飙升结束后，使用工具回查该时间段，生成火焰图
# 验证火焰图中能看到 stress-ng 的 matrixprod 热点函数
```

**测试验证必须包含：**
- 构造 CPU 飙升的命令和时间记录
- 使用工具回查该时间段的操作截图/录屏
- 生成的火焰图截图，标注热点函数是否与预期一致

---


### 评判标准

| 维度 | 权重 | 说明 |
|------|------|------|
| **功能完整性** | 30% | 核心四项功能是否完整可用 |
| **工程质量** | 25% | Docker 镜像能否一键启动、代码结构是否清晰、README 是否完善 |
| **AI 工具使用** | 20% | AI 对话记录体现的需求拆解、迭代过程、问题排查能力 |
| **测试验证** | 15% | 是否构建了具象的测试场景、验证结果是否可信 |
| **前端界面** | 10% | 有可用前端界面额外加分，界面美观度和交互体验 |

---

### 提交方式

1. **GitHub 仓库地址**：提交公开仓库链接，仓库中应包含：
   - 完整项目代码（含 Dockerfile）
   - 导出的 Docker 镜像 `.tar` 文件（若超过 GitHub 100MB 限制，可放在 GitHub Release 附件中）
   - README.md（使用说明 + 设计说明）
   - `test/` 目录（测试脚本 + 测试结果截图）
   - `ai-chat-log/` 目录（AI 完整对话记录导出）

2. **一键启动验证命令**（评审方执行）：
```bash
# 方式一：从 tar 包加载
git clone https://github.com/<你的用户名>/<项目名>.git
cd <项目名>
docker load -i profiler.tar
docker run --privileged -d -p 8080:8080 --name cpu-profiler <镜像名>
# 浏览器访问 http://localhost:8080（如有前端）

# 方式二：直接构建
git clone https://github.com/<你的用户名>/<项目名>.git
cd <项目名>
docker build -t cpu-profiler .
docker run --privileged -d -p 8080:8080 --name cpu-profiler cpu-profiler
```


---

### 提交要求

所有题目统一使用 **一个 GitHub 公开仓库** 提交，仓库命名格式：

```
2026CVM-kaohe-<你的名字拼音>
```

> 示例：张三 → `2026CVM-kaohe-zhangsan`

#### 仓库目录结构

```
2026CVM-kaohe-<你的名字拼音>/
│
├── README.md                          # 仓库总说明：个人信息、题目完成情况概览
├── resume/
│   └── resume.pdf                     # 个人简历
│
├── task1/                             # ========== 题目 1 ==========
│   │
│   ├── 1-perf-stat/                   # 第一小题：多场景微架构指标采集
│   │   ├── README.md                  # 运行说明：环境准备、perf stat 采集命令、如何复现
│   │   ├── results/                   # perf stat 原始输出文件
│   │   │   ├── int64.txt
│   │   │   ├── matrixprod.txt
│   │   │   ├── read64.txt
│   │   │   ├── rand-set.txt
│   │   │   └── queens.txt
│   │   └── report.pdf                 # 五场景对比表格 + 差异分析报告
│   │
│   ├── 2-flamegraph/                  # 第二小题：火焰图生成与热点分析
│   │   ├── README.md                  # 运行说明：perf record + FlameGraph 生成步骤
│   │   ├── flamegraphs/               # 生成的火焰图文件
│   │   │   ├── matrixprod_flame.svg
│   │   │   ├── rand_mem_flame.svg
│   │   │   └── ...
│   │   └── report.pdf                 # 火焰图对比分析报告
│   │
│   └── 3-cache-line-test/             # 第三小题：AI 辅助编写 Cache Line 微基准
│       ├── README.md                  # 运行说明：编译命令、运行方式、perf 采集命令
│       ├── src/
│       │   └── cache_line_test.c      # 微基准测试源代码
│       ├── results/                   # 各步长的 perf 输出 + 性能数据
│       ├── flamegraphs/               # stride=1 vs stride=64 的火焰图
│       ├── report.pdf                 # 曲线图 + 拐点分析 + AI 使用记录
│       └── ai-chat-log/               # AI 工具对话记录（截图或导出文件）
│
├── task2/                             # ========== 题目 2（选做加分）==========
│   ├── README.md                      # 【核心文件】包含以下内容：
│   │                                  #   1. 项目简介与架构设计说明
│   │                                  #   2. 快速启动命令（docker load + docker run）
│   │                                  #   3. 使用示例（如何回查时间段、生成火焰图）
│   │                                  #   4. 前端访问地址（如有）
│   │                                  #   5. 设计权衡说明
│   ├── src/                           # 完整项目源代码
│   │   ├── Dockerfile
│   │   ├── ...                        # 后端/前端/采集脚本等
│   │   └── ...
│   ├── profiler.tar                   # Docker 镜像导出文件（docker save 生成）
│   │                                  # 若超过 100MB，放到 GitHub Release 附件中
│   │                                  # 并在 README 中注明下载链接
│   ├── test/                          # 测试验证
│   │   ├── test_scenario.sh           # 构造 CPU 飙升的测试脚本
│   │   └── screenshots/              # 测试过程截图（回查操作 + 火焰图结果）
│   └── ai-chat-log/                   # AI 编程完整对话记录
│
└── .gitignore
```

#### 评审方验证流程

```bash
# 1. 克隆仓库
git clone https://github.com/<你的用户名>/2026CVM-考核-<你的名字>.git
cd 2026CVM-考核-<你的名字>

# 2. 查看题目 1 —— 进入各小题目录，按 README.md 复现
cd task1/1-perf-stat && cat README.md
cd ../2-flamegraph && cat README.md
cd ../3-cache-line-test && cat README.md

# 3. 查看题目 2 —— 一键启动容器
cd ../../task2
docker load -i profiler.tar                              # 加载镜像
docker run --privileged -d -p 8080:8080 --name cpu-profiler <镜像名>  # 启动
# 浏览器访问 http://localhost:8080（如有前端）
```

#### 提交检查清单

| 检查项 | 是否完成 |
|--------|---------|
| GitHub 仓库为公开（Public）仓库 | ☐ |
| 仓库根目录有 `README.md` 总说明 | ☐ |
| `resume/` 下有简历 PDF | ☐ |
| `task1/1-perf-stat/` 有 README + perf 输出 + 分析报告 | ☐ |
| `task1/2-flamegraph/` 有 README + SVG 火焰图 + 分析报告 | ☐ |
| `task1/3-cache-line-test/` 有 README + 源代码 + 报告 + AI 记录 | ☐ |
| `task2/README.md` 包含 docker load/run 的启动命令 | ☐（选做） |
| `task2/profiler.tar` 可直接 docker load 加载 | ☐（选做） |
| `task2/test/` 有测试脚本和验证截图 | ☐（选做） |
| 仓库有多次 git commit 记录（体现开发过程） | ☐ |

---


