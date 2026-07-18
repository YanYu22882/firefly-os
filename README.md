# Firefly OS — 最小耗散结构模拟器

**Firefly OS** 是一个基于公理化热力学（能量守恒、熵增、兰道尔原理）构建的离散时间耗散结构模拟内核。它用极少的代码（约 200 行）揭示了有限能量系统在信息–热力学耦合下的生存极限，并为复杂系统研究提供了一套可复现、可扩展的数值实验平台。

---

## 目录

- [项目背景](#项目背景)
- [核心原理](#核心原理)
- [安装与依赖](#安装与依赖)
- [快速开始](#快速开始)
- [详细使用指南](#详细使用指南)
  - [1. 核心模拟器 (firefly_sim.py)](#1-核心模拟器-firefly_simpy)
  - [2. 数据分析与绘图 (firefly_analyze.py)](#2-数据分析与绘图-firefly_analyzespy)
  - [3. 独立可视化 (firefly_plot.py)](#3-独立可视化-firefly_plotpy)
  - [4. 批量参数扫描 (firefly_batch.py)](#4-批量参数扫描-firefly_batchpy)
- [参数说明与调优](#参数说明与调优)
- [输出文件解读](#输出文件解读)
- [常见问题](#常见问题)
- [贡献与许可](#贡献与许可)

---

## 项目背景

在物理、生物、经济乃至人工智能领域，存在一类通用问题：

> *“一个有限资源、会老化、且能处理信息的系统，它的最大生存时间由什么决定？随机干扰会如何影响它的寿命？”*

Firefly OS 以最精简的数学结构（三个状态变量 + 三条物理公理）给出了一种答案。它不模拟任何具体对象（细胞、经济体、AI模型），而是模拟所有这类系统的**共同底层约束**。通过数千次并行实验，它涌现出非平凡的统计规律，例如：

- **刚性最短寿命**：无论噪声如何，系统不会短于某个热力学底线（本例中约为 8 步）。
- **右偏长尾分布**：噪声可通过信息成本“缓冲”代谢崩溃，使部分个体存活更久（本例中最长可达 19 步）。
- **100% 代谢崩溃死因**：在所有参数配置下，死亡几乎全部由“维持成本侵占行动预算”引发，证明热力学第二定律是最终裁决者。

该项目适用于教学演示、算法基准测试、以及作为更复杂模型的底层内核。

---

## 核心原理

系统状态由三个标量描述：

- **E（能量储备）**：有限预算，每步因各类成本而减少。
- **S（熵/老化度）**：不可逆地线性增加，代表内部无序累积。
- **M（记忆/信息量）**：积累的环境信息，会反过来降低感知灵敏度（认知惯性）。

每一步严格按以下因果顺序执行：

1. **熵增**：`S ← S + BS` （热力学第二定律）
2. **感知**：`signal = base + noise`，其中噪声幅值受 `M` 抑制（`rigidity = 1/(1+M*K)`）
3. **代谢成本**：`cost_maint = β * (1 + ES * S²)` （老化加速维持成本）
4. **信息处理**：若 `|Δsignal| > threshold`，则支付 `cost_info = L * |Δsignal|`，并更新 `M += Δsignal * efficiency`
5. **能量扣除**：`E ← E - (cost_maint + cost_info + basal_loss)`
6. **死亡判定**（互斥）：
   - **代谢崩溃**：若 `cost_maint > 0.7 * total_cost`
   - **能量耗尽**：若 `E < 0.001`
   - **熵饱和**：若 `S >= 0.999`

---

## 安装与依赖

- Python 3.8 或更高版本
- 推荐使用虚拟环境（可选）

安装必要库：

```bash
pip install numpy matplotlib
```

本项目所有脚本均使用标准库及上述两个依赖，无需额外框架。

---

## 快速开始

1. **克隆或下载本仓库**。

2. **运行默认实验（5000 次）**：

```bash
python firefly_sim.py
```

这将在当前目录生成 `firefly_data.csv`。

3. **查看统计结果与直方图**：

```bash
python firefly_analyze.py firefly_data.csv
```

终端将打印完整统计报告，同时弹出寿命分布直方图（并保存为 `lifetime_histogram.png`）。

4. **（可选）绘制单次运行轨迹**：

```bash
python firefly_sim.py --trace
python firefly_plot.py firefly_data.csv
```

这会产生 `trace.csv` 并绘制状态演化曲线（E, S, M）和成本曲线，保存为 `trace_curve.png`。

---

## 详细使用指南

### 1. 核心模拟器 (`firefly_sim.py`)

**功能**：执行模拟，输出 CSV 原始数据。

**命令行参数**：

| 参数 | 说明 |
| :--- | :--- |
| `-n N` | 重复实验次数（默认 5000） |
| `-o FILENAME` | 输出 CSV 文件名（默认 `firefly_data.csv`） |
| `--trace` | 启用轨迹模式，仅运行 1 次，输出详细状态到 `trace.csv` |

**使用示例**：

```bash
# 默认配置
python firefly_sim.py

# 自定义次数和文件名
python firefly_sim.py -n 10000 -o my_experiment.csv

# 生成单次轨迹
python firefly_sim.py --trace
```

---

### 2. 数据分析与绘图 (`firefly_analyze.py`)

**功能**：读取 CSV，计算统计量，打印结论，并绘制寿命直方图。

**用法**：

```bash
python firefly_analyze.py [数据文件.csv]
```

若不指定文件，默认读取 `firefly_data.csv`。

**输出内容**：

- 终端：均值、标准差、最值、四分位距、死因分布、核心结论。
- 图像：`lifetime_histogram.png`（寿命分布直方图）。

**高级选项**：若不想弹出图形窗口（如在无 GUI 服务器上），可修改脚本中 `show_plot=False`。

---

### 3. 独立可视化 (`firefly_plot.py`)

**功能**：仅绘制直方图与轨迹曲线，不进行统计计算。适合已有数据时快速出图。

**用法**：

```bash
python firefly_plot.py [数据文件.csv]
```

如果存在 `trace.csv`，将额外绘制两条曲线：
- 状态演化：E, S, M 随时间的变化
- 成本演化：维持成本与信息成本

输出图像保存为 `lifetime_hist.png` 和 `trace_curve.png`。

---

### 4. 批量参数扫描 (`firefly_batch.py`)

**功能**：自动扫描 `LANDAUER_COST` 和 `ENTROPY_RATE` 的组合，生成多组数据，用于研究参数对寿命方差的影响。

**用法**：

```bash
python firefly_batch.py
```

**输出**：

- 所有 CSV 文件保存至 `batch_data/` 目录，文件名包含参数值。
- 终端打印汇总表格（每组均值与标准差）。

**自定义扫描网格**：直接修改脚本中的 `L_values` 和 `BS_values` 列表。

---

## 参数说明与调优

核心参数位于 `firefly_sim.py` 的 `DEFAULT_PARAMS` 字典中，所有数值均为无量纲单位。

| 参数 | 默认值 | 含义 | 调优建议 |
| :--- | :--- | :--- | :--- |
| `ENTROPY_RATE` | 0.02 | 每步熵增量（老化速度） | 增大则寿命缩短，减小则寿命延长 |
| `METABOLIC_BASE` | 0.02 | 基础代谢率 | 增大则能量消耗加快 |
| `DISORDER_SENS` | 2.5 | 熵敏感度（老化对维持成本的放大效应） | 增大则代谢崩溃更早发生 |
| `LANDAUER_COST` | 0.02 | 信息处理相对成本 | 增大则信息处理代价更高，方差增大 |
| `INFO_THRESHOLD` | 0.05 | 感知死区阈值 | 低于此幅度的信号不处理，可降低信息成本 |
| `INERTIA_COEFF` | 0.10 | 认知惯性系数 | 增大则记忆对感知的抑制更强 |
| `BINDING_FRACTION` | 0.30 | 必须保留的能量比例（对应 70% 崩溃线） | 建议保持在 0.25–0.40，否则死因分布会失衡 |
| `BASAL_LOSS` | 0.01 | 每步最小损耗 | 一般为小常数，避免无穷寿命 |

**推荐实验**：先运行默认参数获得基准，然后逐一调整 `ENTROPY_RATE` 或 `LANDAUER_COST`，观察统计量变化。

---

## 输出文件解读

### `firefly_data.csv`（标准输出）
- 三列：`lifetime`, `final_M`, `cause`
- 每行代表一次独立实验。
- 可用于任何数据分析工具（Excel, R, Pandas 等）。

### `trace.csv`（轨迹模式）
- 列：`t`, `E`, `S`, `M`, `signal`, `cost_maintenance`, `cost_info`, `dead`
- 单次运行的完整时间序列，用于可视化状态演化。

### 图像文件
- `lifetime_histogram.png` / `lifetime_hist.png`：寿命分布直方图，标注均值和热力学底线。
- `trace_curve.png`：状态演化及成本曲线。

---

## 常见问题

**Q1：为什么我的寿命标准差不是 0？**  
A：因为默认 `LANDAUER_COST` 足够大，使信息成本显著扰动总成本，引入随机性。若希望接近零方差，可将 `LANDAUER_COST` 设为 `0.001` 或更小。

**Q2：如何改变噪声幅值？**  
A：修改 `firefly_sim.py` 中 `step()` 函数内的 `0.08 * rigidity` 系数。

**Q3：图表中文显示乱码怎么办？**  
A：`firefly_plot.py` 和 `firefly_analyze.py` 已内置自动中文字体检测；若仍乱码，请安装系统字体（如微软雅黑），或脚本将自动回退为英文标签。

**Q4：运行时间太长，如何加速？**  
A：减少 `-n` 参数（例如 `-n 1000`），或降低并行度（修改 `workers` 参数）。在无绘图需求时，添加 `--no-show` 可避免阻塞。

**Q5：我可以把核心引擎嵌入自己的项目吗？**  
A：可以。`firefly_sim.py` 中的 `run_experiment()` 函数可直接导入调用，返回原始数据列表，便于二次开发。

---

## 贡献与许可

本项目采用 **MIT 许可证**，欢迎 Fork 和 Pull Request。

若你有新的应用场景、有趣的参数相变发现，或遇到任何问题，请提交 Issue 与我们分享。

---

**感谢使用 Firefly OS — 探索有限宇宙中的生存极限。** 🪚