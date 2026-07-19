#!/usr/bin/env python3
"""
Firefly OS — 批量参数扫描器 (v2.0)
支持扫描 LANDAUER_COST, ENTROPY_RATE, FRUGALITY_COEFF
"""
import numpy as np
import itertools
import os
import csv
from firefly_sim import run_experiment, DEFAULT_PARAMS

def batch_scan():
    # 定义扫描网格（可自由增删）
    L_values = [0.002, 0.005, 0.02, 0.1]           # 兰道尔系数
    BS_values = [0.01, 0.02, 0.04]                 # 熵增速率
    ALPHA_values = [0.0, 0.05, 0.10]               # 节俭系数（新增）

    os.makedirs('batch_data', exist_ok=True)
    print("=" * 80)
    print("Firefly OS 批量扫描 (v2.0)")
    print(f"总配置数: {len(L_values) * len(BS_values) * len(ALPHA_values)}")
    print("=" * 80)

    summary = []
    for L, BS, ALPHA in itertools.product(L_values, BS_values, ALPHA_values):
        params = DEFAULT_PARAMS.copy()
        params['LANDAUER_COST'] = L
        params['ENTROPY_RATE'] = BS
        params['FRUGALITY_COEFF'] = ALPHA

        filename = f"batch_data/L_{L}_BS_{BS}_alpha_{ALPHA}.csv"
        print(f"运行: L={L}, BS={BS}, α={ALPHA} -> {filename}")

        data = run_experiment(params, n_runs=2000)   # 每组2000次

        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['lifetime', 'final_M', 'cause'])
            writer.writerows(data)

        lifetimes = [row[0] for row in data]
        mean_life = np.mean(lifetimes)
        std_life = np.std(lifetimes)
        summary.append((L, BS, ALPHA, mean_life, std_life))

    # 打印汇总表
    print("\n" + "=" * 80)
    print("扫描完成，汇总如下：")
    print(f"{'L':>8} | {'BS':>8} | {'α':>8} | {'寿命均值':>10} | {'寿命标准差':>10}")
    print("-" * 80)
    for L, BS, ALPHA, mean, std in summary:
        print(f"{L:8.4f} | {BS:8.3f} | {ALPHA:8.3f} | {mean:10.4f} | {std:10.4f}")
    print("=" * 80)
    print("所有数据文件已保存至 ./batch_data/")

if __name__ == "__main__":
    batch_scan()