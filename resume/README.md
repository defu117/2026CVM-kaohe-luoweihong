# Resume

请在提交前将个人简历命名为 `resume.pdf` 并放入本目录。
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
