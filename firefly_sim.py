#!/usr/bin/env python3
"""
Firefly OS v1.1 — 核心模拟器
=========================================
量纲声明（所有数值均为无量纲归一化单位）：
  - E: 抽象能量单位，与焦耳/ATP/货币呈线性正比
  - S: 无量纲熵指数，范围 [0, 1)，对应"有序度退化百分比"
  - 时间步: 抽象周期，映射到具体系统时需通过 BS 校准

物理参数对应关系：
  - ENTROPY_RATE (BS): 系统老化速度（如单位时间内的氧化损伤累积率）
  - BINDING_FRACTION (0.30): 参考生物体基础代谢占总能耗约70%的经验事实
  - LANDAUER_COST: 信息处理的"相对成本"，默认设为 β/10 以贴近真实物理量级
"""

import numpy as np
from concurrent.futures import ProcessPoolExecutor, as_completed
import csv
import os
import argparse

# ============================================================================
# 一、公理参数（默认）
# ============================================================================
DEFAULT_PARAMS = {
    'INIT_FREE_ENERGY': 100.0,
    'INIT_DISORDER': 0.10,
    'ENTROPY_RATE': 0.02,
    'METABOLIC_BASE': 0.02,
    'DISORDER_SENS': 2.5,
    'LANDAUER_COST': 0.02,
    'INFO_THRESHOLD': 0.05,
    'INERTIA_COEFF': 0.10,
    'BINDING_FRACTION': 0.30,
    'BASAL_LOSS': 0.01,
    'MAX_STEPS': 500,
    'ENERGY_EPSILON': 1e-3,
    'ENTROPY_SATUR': 0.999,
}

# ============================================================================
# 二、核心演化引擎
# ============================================================================
def step(t, E, S, M, signal_prev, params, rng):
    S_next = S + params['ENTROPY_RATE']
    rigidity = 1.0 / (1.0 + M * params['INERTIA_COEFF'])
    noise = rng.normal(0.0, 0.08 * rigidity)
    signal = 0.5 + noise
    cost_maintenance = params['METABOLIC_BASE'] * (
        1.0 + params['DISORDER_SENS'] * S_next ** 2
    )
    delta_signal = abs(signal - signal_prev) if t > 0 else 0.0
    if delta_signal > params['INFO_THRESHOLD']:
        cost_info = params['LANDAUER_COST'] * delta_signal
        write_efficiency = max(
            params['LANDAUER_COST'] * (1.0 - S_next), 0.0
        ) * rigidity
        dM = delta_signal * write_efficiency
    else:
        cost_info = 0.0
        dM = 0.0
    total_cost = cost_maintenance + cost_info + params['BASAL_LOSS']
    E_next = E - total_cost
    M_next = M + dM

    if cost_maintenance > (1.0 - params['BINDING_FRACTION']) * total_cost:
        dead, cause = True, 'metabolic_collapse'
    elif E_next < params['ENERGY_EPSILON']:
        dead, cause = True, 'energy_exhaust'
    elif S_next >= params['ENTROPY_SATUR']:
        dead, cause = True, 'entropy_saturation'
    else:
        dead, cause = False, None
    return E_next, S_next, M_next, signal, dead, cause, cost_maintenance, cost_info


def run_single(params, seed):
    rng = np.random.default_rng(seed)
    E, S, M = params['INIT_FREE_ENERGY'], params['INIT_DISORDER'], 0.0
    signal_prev = 0.5
    t = 0
    # 用于轨迹记录
    trace = []
    while t < params.get('MAX_STEPS', 500):
        E, S, M, signal, dead, cause, cm, ci = step(
            t, E, S, M, signal_prev, params, rng
        )
        trace.append((t, E, S, M, signal, cm, ci, dead))
        t += 1
        if dead:
            break
        signal_prev = signal
    if not dead:
        cause = 'energy_exhaust'
    # 返回：最终寿命，最终M，死因，完整轨迹
    return t, M, cause, trace


def run_experiment(params, n_runs, workers=None, seed_base=42):
    """并行执行实验，返回原始数据列表"""
    if workers is None:
        workers = min(os.cpu_count(), 8)
    rng = np.random.default_rng(seed_base)
    seeds = rng.integers(0, 2**31, size=n_runs)
    results = []
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(run_single, params, seed) for seed in seeds]
        for future in as_completed(futures):
            lifetime, final_M, cause, _ = future.result()
            results.append((lifetime, final_M, cause))
    return results


def run_trace(params, seed=42):
    """单次运行，返回完整轨迹"""
    _, _, _, trace = run_single(params, seed)
    return trace


# ============================================================================
# 三、主程序
# ============================================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Firefly OS 核心模拟器')
    parser.add_argument('-n', '--runs', type=int, default=5000,
                        help='重复实验次数（默认5000）')
    parser.add_argument('-o', '--output', type=str, default='firefly_data.csv',
                        help='输出CSV文件名（默认firefly_data.csv）')
    parser.add_argument('--trace', action='store_true',
                        help='启用轨迹输出模式（仅运行1次，输出详细轨迹到 trace.csv）')
    args = parser.parse_args()

    if args.trace:
        # 轨迹模式
        print("启用轨迹模式，运行1次模拟...")
        trace = run_trace(DEFAULT_PARAMS)
        with open('trace.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['t', 'E', 'S', 'M', 'signal', 'cost_maintenance', 'cost_info', 'dead'])
            writer.writerows(trace)
        print("轨迹已保存至 trace.csv")
    else:
        # 标准批量模式
        print(f"运行 {args.runs} 次模拟，输出至 {args.output} ...")
        data = run_experiment(DEFAULT_PARAMS, n_runs=args.runs)
        with open(args.output, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['lifetime', 'final_M', 'cause'])
            writer.writerows(data)
        print("完成。")