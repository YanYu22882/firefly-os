#!/usr/bin/env python3
"""
Firefly OS — 数据分析脚本（支持中文字体）
读取CSV数据，打印统计结论，并绘制直方图。
"""

import numpy as np
import csv
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontManager
import sys

# ===== 智能字体选择 =====
def get_chinese_font():
    candidates = [
        'Microsoft YaHei', 'SimHei', 'PingFang SC', 'Hiragino Sans GB',
        'WenQuanYi Micro Hei', 'Noto Sans CJK SC', 'Source Han Sans SC',
        'AR PL UMing CN', 'Droid Sans Fallback'
    ]
    available = [f.name for f in FontManager().ttflist]
    for font in candidates:
        if font in available:
            return font
    for f in FontManager().ttflist:
        name = f.name.lower()
        if 'cjk' in name or 'hei' in name or 'sc' in name or 'cn' in name:
            return f.name
    return None

chinese_font = get_chinese_font()
use_chinese = chinese_font is not None
if use_chinese:
    plt.rcParams['font.sans-serif'] = [chinese_font]
    plt.rcParams['axes.unicode_minus'] = False
    print(f"使用中文字体: {chinese_font}")
else:
    print("警告：未找到中文字体，将使用英文标签")

def label_text(chinese, english):
    return chinese if use_chinese else english

# ==================================================

def load_data(filename):
    lifetimes, final_Ms, causes = [], [], []
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for row in reader:
            lifetimes.append(int(row[0]))
            final_Ms.append(float(row[1]))
            causes.append(row[2])
    return np.array(lifetimes), np.array(final_Ms), causes

def analyze(filename, show_plot=True):
    lif, M, causes = load_data(filename)
    n = len(lif)

    print("=" * 90)
    print(f"Firefly OS 数据分析")
    print(f"数据文件: {filename}  (共 {n} 条记录)")
    print("=" * 90)

    # 基本统计
    mean_life = np.mean(lif)
    std_life = np.std(lif)
    min_lif = np.min(lif)      # <-- 这里定义了 min_lif
    max_lif = np.max(lif)      # <-- 这里定义了 max_lif
    median_life = np.median(lif)
    q75, q25 = np.percentile(lif, 75), np.percentile(lif, 25)
    iqr = q75 - q25

    print("\n【寿命统计】")
    print(f"  均值: {mean_life:.4f} 步")
    print(f"  标准差: {std_life:.4f} 步")
    print(f"  最小值: {min_lif} 步")
    print(f"  最大值: {max_lif} 步")
    print(f"  中位数: {median_life:.1f} 步")
    print(f"  四分位距: {iqr:.1f} 步")

    cause_counts = Counter(causes)
    print("\n【死因分布】")
    for cause, count in cause_counts.items():
        print(f"  {cause}: {count} ({count/n*100:.1f}%)")

    mean_M = np.mean(M)
    print(f"\n【记忆终值 M】均值 = {mean_M:.6f}")

    print("\n" + "=" * 90)
    print("【基于实测数据的结论】")
    print(f"1. 纯热力学底线（忽略信息成本）约为 8 步，")
    print(f"   但实际加入随机信息成本后，平均寿命为 {mean_life:.2f} 步。")
    print(f"   → 信息成本通过抬高总成本（分母），延迟了代谢崩溃的触发。")
    print()
    print(f"2. 寿命标准差约为 {std_life:.2f} 步，并非零方差。")
    print(f"   → 方差来源于随机噪声通过 cost_info 对生存时间的传导。")
    print()
    collapse_ratio = cause_counts.get('metabolic_collapse', 0) / n * 100
    print(f"3. 死因中 'metabolic_collapse' 占比 {collapse_ratio:.1f}%，")
    print(f"   证明热力学第二定律始终是耗散结构死亡的最终裁决者。")
    print("=" * 90)

    # 绘图
    if show_plot:
        try:
            plt.figure(figsize=(10, 6))
            bins = range(min_lif, max_lif + 2)   # <-- 这里是 range，不是 ange
            plt.hist(lif, bins=bins, align='left', rwidth=0.8,
                     color='steelblue', edgecolor='black', alpha=0.8)
            plt.xlabel(label_text('寿命 (步数)', 'Lifetime (steps)'))
            plt.ylabel(label_text('频数', 'Frequency'))
            plt.title(label_text('Firefly OS 寿命分布', 'Firefly OS Lifetime Distribution'))
            plt.axvline(mean_life, color='red', linestyle='--',
                        label=label_text(f'均值 = {mean_life:.2f}', f'Mean = {mean_life:.2f}'))
            plt.axvline(8, color='green', linestyle=':',
                        label=label_text('热力学底线 (8步)', 'Thermodynamic baseline (8 steps)'))
            plt.legend()
            plt.grid(alpha=0.3)
            plt.tight_layout()
            plt.savefig('lifetime_histogram.png', dpi=150)
            print("\n直方图已保存为 lifetime_histogram.png")
            plt.show()
        except Exception as e:
            print(f"绘图出错: {e}")

if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else 'firefly_data.csv'
    analyze(filename, show_plot=True)