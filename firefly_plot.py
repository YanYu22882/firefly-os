#!/usr/bin/env python3
"""
Firefly OS — 可视化脚本（自动适配中英文）
"""

import csv
import numpy as np
import sys
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties, findfont, FontManager
import subprocess
import os

# ===== 智能字体选择 =====
def get_chinese_font():
    """
    返回一个可用的中文字体名称，如果找不到则返回 None。
    """
    # 候选字体列表（Windows / macOS / Linux 常见中文字体）
    candidates = [
        'Microsoft YaHei',
        'SimHei',
        'PingFang SC',
        'Hiragino Sans GB',
        'WenQuanYi Micro Hei',
        'Noto Sans CJK SC',
        'Source Han Sans SC',
        'AR PL UMing CN',
        'Droid Sans Fallback'
    ]
    
    # 获取系统所有可用字体
    import matplotlib.font_manager as fm
    available = [f.name for f in fm.fontManager.ttflist]
    
    for font in candidates:
        if font in available:
            return font
    
    # 若未找到，尝试用 findfont 查找任意包含 'CJK' 或 'Hei' 的字体
    for f in fm.fontManager.ttflist:
        name = f.name.lower()
        if 'cjk' in name or 'hei' in name or 'sc' in name or 'cn' in name:
            return f.name
    
    return None

# 尝试获取中文字体
chinese_font = get_chinese_font()
use_chinese = chinese_font is not None

if use_chinese:
    plt.rcParams['font.sans-serif'] = [chinese_font]
    plt.rcParams['axes.unicode_minus'] = False
    print(f"使用中文字体: {chinese_font}")
else:
    print("警告：未找到中文字体，将使用英文标签")
    # 回退到英文显示，我们直接使用英文文本（无需设置字体）

def label_text(chinese, english):
    """根据是否使用中文返回对应文本"""
    return chinese if use_chinese else english

# ==================================================

def load_data(filename):
    lifetimes, final_Ms, causes = [], [], []
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            lifetimes.append(int(row[0]))
            final_Ms.append(float(row[1]))
            causes.append(row[2])
    return np.array(lifetimes), np.array(final_Ms), causes

def plot_histogram(lifetimes, save_path='lifetime_hist.png'):
    plt.figure(figsize=(10, 6))
    bins = range(min(lifetimes), max(lifetimes) + 2)
    plt.hist(lifetimes, bins=bins, align='left', rwidth=0.8,
             color='steelblue', edgecolor='black', alpha=0.8)
    
    plt.xlabel(label_text('寿命 (步数)', 'Lifetime (steps)'))
    plt.ylabel(label_text('频数', 'Frequency'))
    plt.title(label_text('Firefly OS 寿命分布 (右偏拖尾)', 'Firefly OS Lifetime Distribution (Right-skewed)'))
    
    mean_val = np.mean(lifetimes)
    plt.axvline(mean_val, color='red', linestyle='--', 
                label=label_text(f'均值 = {mean_val:.2f}', f'Mean = {mean_val:.2f}'))
    plt.axvline(8, color='green', linestyle=':', 
                label=label_text('热力学底线 (8步)', 'Thermodynamic baseline (8 steps)'))
    
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    print(f"直方图已保存至 {save_path}")
    plt.show()

def plot_trace(trace_file='trace.csv'):
    try:
        with open(trace_file, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)
            data = list(reader)
        if not data:
            print("轨迹文件为空")
            return
        data = np.array(data, dtype=float)
        t = data[:, 0]
        E = data[:, 1]
        S = data[:, 2]
        M = data[:, 3]
        cm = data[:, 5]
        ci = data[:, 6]
        
        fig, axes = plt.subplots(2, 1, figsize=(10, 8))
        
        # 子图1
        axes[0].plot(t, E, label=label_text('E (能量)', 'E (Energy)'), color='blue', linewidth=2)
        axes[0].plot(t, S, label=label_text('S (熵/老化)', 'S (Entropy/Aging)'), color='red', linestyle='--', linewidth=2)
        axes[0].plot(t, M, label=label_text('M (记忆/信息)', 'M (Memory/Info)'), color='green', linestyle=':', linewidth=2)
        axes[0].set_xlabel(label_text('时间步', 'Time step'))
        axes[0].set_ylabel(label_text('状态值', 'State value'))
        axes[0].set_title(label_text('单次运行的状态演化', 'State evolution of a single run'))
        axes[0].legend()
        axes[0].grid(alpha=0.3)
        
        # 子图2
        axes[1].plot(t, cm, label=label_text('维持成本 (cost_maint)', 'Maintenance cost'), color='orange')
        axes[1].plot(t, ci, label=label_text('信息成本 (cost_info)', 'Info cost'), color='purple')
        axes[1].set_xlabel(label_text('时间步', 'Time step'))
        axes[1].set_ylabel(label_text('成本', 'Cost'))
        axes[1].set_title(label_text('成本构成演化', 'Cost components evolution'))
        axes[1].legend()
        axes[1].grid(alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('trace_curve.png', dpi=150)
        print("轨迹曲线已保存至 trace_curve.png")
        plt.show()
    except FileNotFoundError:
        print("未找到 trace.csv，请先运行 python firefly_sim.py --trace")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = 'firefly_data.csv'
    
    print(f"加载数据: {filename}")
    lif, _, _ = load_data(filename)
    plot_histogram(lif)
    plot_trace('trace.csv')