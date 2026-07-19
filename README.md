Firefly OS

离散状态反馈基准模型

Firefly OS 是一个单代理、三变量、离散时间状态机模型，用于研究状态反馈（经验对代谢率的负调节）对能耗敏感型系统寿命分布的影响。

本模型不模拟任何具体物理实体，也不作为预测工具。其设计目的是在可复现的数值条件下，验证反馈机制是否能够显著改变系统的寿命分布。

系统定义

代理数：1
空间维度：0
时间结构：离散步长
状态变量：3个（E, S, M）
随机性：仅存在于环境信号中（高斯噪声）

变量定义
E：能量预算，单调递减，不可再生
S：内部老化程度，单调递增，不可逆
M：累积信息量，仅增不减，受老化和惯性衰减

核心演化规则

每步按以下因果顺序执行：

1. 老化：S增加固定增量
2. 感知：signal = 0.5 + 高斯噪声（噪声幅值受M衰减）
3. 代谢成本：cost_maint = beta * (1 + ES * S^2) * adaptive_factor
4. 信息处理：若信号变化超过阈值，则产生信息成本并更新M
5. 能量扣除：E -= cost_maint + cost_info + 基础损耗
6. 死亡判定（互斥）：代谢崩溃 / 能量耗尽 / 熵饱和

自适应因子公式
adaptive_factor = 1 - alpha * M / (1 + M)

其中alpha为反馈强度系数，alpha=0时退化为无反馈基线。

使用说明

1. 安装依赖
   pip install numpy matplotlib

2. 运行默认实验（5000次）
   python firefly_sim.py

   输出文件：firefly_data.csv（三列：lifetime, final_M, cause）

3. 查看统计结果与直方图
   python firefly_analyze.py firefly_data.csv

   输出：终端统计报告 + lifetime_histogram.png

4. 查看单次运行轨迹
   python firefly_sim.py --trace
   python firefly_plot.py firefly_data.csv

   输出：trace.csv + trace_curve.png

5. 批量参数扫描
   python firefly_batch.py

   输出：batch_data/ 目录下的多组CSV文件 + 终端汇总表格

实验验证结果

以下为5000次独立实验的统计结果。

条件一：弱反馈（默认参数）
INFO_THRESHOLD = 0.05，LANDAUER_COST = 0.02，FRUGALITY_COEFF = 0.10

平均寿命：9.91 步
标准差：2.10 步
最小观测寿命：8 步
最大观测寿命：21 步
死因分布：100% 代谢崩溃

条件二：强反馈（增强参数）
INFO_THRESHOLD = 0.005，LANDAUER_COST = 0.20，FRUGALITY_COEFF = 1.00

平均寿命：25.49 步
标准差：6.78 步
最小观测寿命：10 步
最大观测寿命：45 步
死因分布：99.9% 代谢崩溃，0.1% 熵饱和

对比结论
将反馈强度从弱调至强后，平均寿命延长约157%，标准差放大3.2倍，首次出现熵饱和死亡路径，最小观测寿命从8步提升至10步。表明在本模型框架内，状态反馈对系统寿命分布具有显著影响。

工具链说明

firefly_sim.py：核心模拟器，支持批量实验与轨迹输出
firefly_analyze.py：数据统计与直方图生成
firefly_plot.py：状态轨迹与成本曲线绘制
firefly_batch.py：参数网格批量扫描

命令行参数

python firefly_sim.py -n 5000 -o output.csv
  -n：实验次数，默认5000
  -o：输出文件名，默认firefly_data.csv
  --trace：轨迹模式，仅运行一次

适用边界

本模型适用于以下条件同时成立的系统：
- 系统为单代理或代理间无显著交互
- 系统行为由资源约束和单调老化主导
- 系统的经验可量化，且积累速度远低于老化速度

本模型不适用于：
- 多代理交互系统
- 空间扩散或场效应
- 连续时间系统
- 对真实物理系统的定量预测

项目状态

已完成v2.0迭代，验证了状态反馈对寿命分布的调节作用。代码完整可运行，统计结果可复现，设计边界已明确。

项目地址：https://github.com/YanYu22882/firefly-os

许可：MIT License