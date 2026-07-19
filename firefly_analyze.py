#!/usr/bin/env python3
"""
Firefly OS — 数据分析脚本
"""
import numpy as np
import csv
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontManager
import sys

def get_chinese_font():
    candidates = ['Microsoft YaHei','SimHei','PingFang SC','Hiragino Sans GB',
                  'WenQuanYi Micro Hei','Noto Sans CJK SC','Source Han Sans SC']
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

def label_text(ch, en):
    return ch if use_chinese else en

def load_data(filename):
    lif, fm, causes = [], [], []
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            lif.append(int(row[0]))
            fm.append(float(row[1]))
            causes.append(row[2])
    return np.array(lif), np.array(fm), causes

def analyze(filename, show_plot=True):
    lif, M, causes = load_data(filename)
    n = len(lif)
    mean_life = np.mean(lif)
    std_life = np.std(lif)
    min_lif = np.min(lif)
    max_lif = np.max(lif)
    median_life = np.median(lif)
    q75, q25 = np.percentile(lif, 75), np.percentile(lif, 25)
    iqr = q75 - q25

    print("="*80)
    print(f"Firefly OS 数据分析  文件: {filename}  (n={n})")
    print("="*80)
    print(f"寿命均值: {mean_life:.4f}  标准差: {std_life:.4f}")
    print(f"最小值: {min_lif}  最大值: {max_lif}  中位数: {median_life:.1f}  IQR: {iqr:.1f}")
    cause_counts = Counter(causes)
    print("死因分布:")
    for c, cnt in cause_counts.items():
        print(f"  {c}: {cnt} ({cnt/n*100:.1f}%)")
    print(f"记忆终值均值: {np.mean(M):.6f}")

    print("\n结论:")
    print(f"- 最小观测寿命 = {min_lif} 步（由判定阈值与老化速率决定）")
    print(f"- 均值 {mean_life:.2f} 步, 标准差 {std_life:.2f} 步")
    print(f"- 主要死因: {cause_counts.most_common(1)[0][0]} ({cause_counts.most_common(1)[0][1]/n*100:.1f}%)")

    if show_plot:
        try:
            plt.figure(figsize=(10,6))
            bins = range(min_lif, max_lif+2)
            plt.hist(lif, bins=bins, align='left', rwidth=0.8, color='steelblue', edgecolor='black')
            plt.xlabel(label_text('寿命 (步数)','Lifetime (steps)'))
            plt.ylabel(label_text('频数','Frequency'))
            plt.title(label_text('Firefly OS 寿命分布','Firefly OS Lifetime Distribution'))
            plt.axvline(mean_life, color='red', linestyle='--', label=label_text(f'均值 {mean_life:.2f}', f'Mean {mean_life:.2f}'))
            plt.axvline(min_lif, color='green', linestyle=':', label=label_text(f'最小观测 {min_lif}', f'Min observed {min_lif}'))
            plt.legend()
            plt.grid(alpha=0.3)
            plt.tight_layout()
            plt.savefig('lifetime_histogram.png', dpi=150)
            print("直方图已保存为 lifetime_histogram.png")
            plt.show()
        except Exception as e:
            print(f"绘图失败: {e}")

if __name__ == "__main__":
    fname = sys.argv[1] if len(sys.argv)>1 else 'firefly_data.csv'
    analyze(fname, show_plot=True)