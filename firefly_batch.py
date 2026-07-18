#!/usr/bin/env python3
"""
Firefly OS — 批量参数扫描器
自动扫描指定参数网格，生成多个CSV数据文件。
"""

import itertools
import os
from firefly_sim import run_experiment, DEFAULT_PARAMS

def batch_scan():
    # 定义要扫描的参数网格
    L_values = [0.002, 0.005, 0.02, 0.1]   # 兰道尔系数
    BS_values = [0.01, 0.02, 0.04]         # 熵增速率
    
    # 创建数据目录
    os.makedirs('batch_data', exist_ok=True)
    
    print("=" * 70)
    print("Firefly OS 批量参数扫描")
    print(f"总配置数: {len(L_values) * len(BS_values)}")
    print("=" * 70)
    
    summary = []
    for L, BS in itertools.product(L_values, BS_values):
        params = DEFAULT_PARAMS.copy()
        params['LANDAUER_COST'] = L
        params['ENTROPY_RATE'] = BS
        
        filename = f"batch_data/L_{L}_BS_{BS}.csv"
        print(f"正在运行: L={L}, BS={BS} -> {filename}")
        
        data = run_experiment(params, n_runs=2000)  # 每组跑2000次
        
        with open(filename, 'w', newline='') as f:
            import csv
            writer = csv.writer(f)
            writer.writerow(['lifetime', 'final_M', 'cause'])
            writer.writerows(data)
        
        # 计算即时统计，用于屏幕显示
        lifetimes = [row[0] for row in data]
        summary.append((L, BS, np.mean(lifetimes), np.std(lifetimes)))
    
    # 打印汇总表
    print("\n" + "=" * 70)
    print("扫描完成。汇总如下：")
    print(f"{'L (兰道尔)':>12} | {'BS (熵速)':>10} | {'寿命均值':>10} | {'寿命标准差':>10}")
    print("-" * 70)
    for L, BS, mean, std in summary:
        print(f"{L:12.4f} | {BS:10.3f} | {mean:10.4f} | {std:10.4f}")
    print("=" * 70)
    print("所有数据文件已保存至 ./batch_data/")

if __name__ == "__main__":
    import numpy as np
    batch_scan()