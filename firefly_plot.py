#!/usr/bin/env python3
"""
Firefly OS — 绘图脚本
"""
import csv
import numpy as np
import sys
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontManager

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

def plot_hist(lifetimes):
    plt.figure(figsize=(10,6))
    bins = range(min(lifetimes), max(lifetimes)+2)
    plt.hist(lifetimes, bins=bins, align='left', rwidth=0.8, color='steelblue', edgecolor='black')
    mean_val = np.mean(lifetimes)
    min_val = np.min(lifetimes)
    plt.xlabel(label_text('寿命 (步数)','Lifetime (steps)'))
    plt.ylabel(label_text('频数','Frequency'))
    plt.title(label_text('Firefly OS 寿命分布','Firefly OS Lifetime Distribution'))
    plt.axvline(mean_val, color='red', linestyle='--', label=label_text(f'均值 {mean_val:.2f}', f'Mean {mean_val:.2f}'))
    plt.axvline(min_val, color='green', linestyle=':', label=label_text(f'最小观测 {min_val}', f'Min observed {min_val}'))
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig('lifetime_hist.png', dpi=150)
    print("直方图已保存至 lifetime_hist.png")
    plt.show()

def plot_trace(trace_file='trace.csv'):
    try:
        with open(trace_file, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)
            rows = list(reader)
        if not rows:
            return
        # 跳过 dead 列
        numeric = [row[:7] for row in rows]
        data = np.array(numeric, dtype=float)
        t = data[:,0]; E = data[:,1]; S = data[:,2]; M = data[:,3]
        cm = data[:,5]; ci = data[:,6]
        fig, axes = plt.subplots(2,1,figsize=(10,8))
        axes[0].plot(t, E, label=label_text('E (能量)','E (Energy)'), color='blue')
        axes[0].plot(t, S, label=label_text('S (老化)','S (Aging)'), color='red', linestyle='--')
        axes[0].plot(t, M, label=label_text('M (记忆)','M (Memory)'), color='green', linestyle=':')
        axes[0].set_xlabel(label_text('时间步','Time step'))
        axes[0].set_ylabel(label_text('状态值','State value'))
        axes[0].set_title(label_text('状态演化','State evolution'))
        axes[0].legend(); axes[0].grid(alpha=0.3)
        axes[1].plot(t, cm, label=label_text('维持成本','Maintenance cost'), color='orange')
        axes[1].plot(t, ci, label=label_text('信息成本','Info cost'), color='purple')
        axes[1].set_xlabel(label_text('时间步','Time step'))
        axes[1].set_ylabel(label_text('成本','Cost'))
        axes[1].set_title(label_text('成本演化','Cost evolution'))
        axes[1].legend(); axes[1].grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig('trace_curve.png', dpi=150)
        print("轨迹曲线已保存至 trace_curve.png")
        plt.show()
    except FileNotFoundError:
        print("未找到 trace.csv，请先运行 python firefly_sim.py --trace")

if __name__ == "__main__":
    fname = sys.argv[1] if len(sys.argv)>1 else 'firefly_data.csv'
    lif, _, _ = load_data(fname)
    plot_hist(lif)
    plot_trace('trace.csv')