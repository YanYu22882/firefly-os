#!/usr/bin/env python3
"""
Firefly OS — 强反馈演示版 (v2.0-strong)
状态变量：E（能量）, S（老化）, M（记忆）
参数已调至强反馈范围，用于演示经验（M）对代谢率的显著抑制效应。
"""

import numpy as np
from concurrent.futures import ProcessPoolExecutor, as_completed
import csv
import os
import argparse

# ============================================================================
# 一、参数配置（已调至强反馈）
# ============================================================================
DEFAULT_PARAMS = {
    'INIT_FREE_ENERGY': 100.0,
    'INIT_DISORDER': 0.10,
    'ENTROPY_RATE': 0.02,
    'METABOLIC_BASE': 0.02,
    'DISORDER_SENS': 2.5,
    'LANDAUER_COST': 0.20,            # 原 0.02，提高信息增益
    'INFO_THRESHOLD': 0.005,           # 原 0.05，降低感知死区
    'INERTIA_COEFF': 0.10,
    'BINDING_FRACTION': 0.30,
    'BASAL_LOSS': 0.01,
    'FRUGALITY_COEFF': 1.0,            # 最大节俭反馈
    'MAX_STEPS': 500,
    'ENERGY_EPSILON': 1e-3,
    'ENTROPY_SATUR': 0.999,
}


# ============================================================================
# 二、核心演化引擎
# ============================================================================
def step(t, E, S, M, signal_prev, params, rng, debug=False):
    # 1. 熵增
    S_next = S + params['ENTROPY_RATE']

    # 2. 认知惯性
    rigidity = 1.0 / (1.0 + M * params['INERTIA_COEFF'])

    # 3. 感知
    noise = rng.normal(0.0, 0.08 * rigidity)
    signal = 0.5 + noise

    # 4. 节俭反馈（M 越大，代谢越低）
    alpha = params['FRUGALITY_COEFF']
    adaptive_factor = 1.0 - alpha * (M / (1.0 + M))

    if debug:
        print(f"[DEBUG] t={t}, alpha={alpha:.3f}, M={M:.6f}, adaptive_factor={adaptive_factor:.6f}")

    # 5. 代谢成本（乘以 adaptive_factor）
    cost_maintenance = (
        params['METABOLIC_BASE']
        * (1.0 + params['DISORDER_SENS'] * S_next ** 2)
        * adaptive_factor
    )

    # 6. 信号处理与记忆更新
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

    # 7. 能量扣除与状态更新
    total_cost = cost_maintenance + cost_info + params['BASAL_LOSS']
    E_next = E - total_cost
    M_next = M + dM

    # 8. 死亡判定
    if cost_maintenance > (1.0 - params['BINDING_FRACTION']) * total_cost:
        dead, cause = True, 'metabolic_collapse'
    elif E_next < params['ENERGY_EPSILON']:
        dead, cause = True, 'energy_exhaust'
    elif S_next >= params['ENTROPY_SATUR']:
        dead, cause = True, 'entropy_saturation'
    else:
        dead, cause = False, None

    return E_next, S_next, M_next, signal, dead, cause, cost_maintenance, cost_info


# ============================================================================
# 三、单次运行
# ============================================================================
def run_single(params, seed, debug=False):
    rng = np.random.default_rng(seed)
    E, S, M = params['INIT_FREE_ENERGY'], params['INIT_DISORDER'], 0.0
    signal_prev = 0.5
    t = 0
    trace = []
    while t < params.get('MAX_STEPS', 500):
        E, S, M, signal, dead, cause, cm, ci = step(
            t, E, S, M, signal_prev, params, rng, debug=debug
        )
        trace.append((t, E, S, M, signal, cm, ci, dead))
        t += 1
        if dead:
            break
        signal_prev = signal
    if not dead:
        cause = 'energy_exhaust'
    return t, M, cause, trace


# ============================================================================
# 四、并行实验
# ============================================================================
def run_experiment(params, n_runs, workers=None, seed_base=42):
    if workers is None:
        workers = min(os.cpu_count(), 8)
    rng = np.random.default_rng(seed_base)
    seeds = rng.integers(0, 2**31, size=n_runs)
    results = []
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(run_single, params, seed, False) for seed in seeds]
        for future in as_completed(futures):
            lifetime, final_M, cause, _ = future.result()
            results.append((lifetime, final_M, cause))
    return results


# ============================================================================
# 五、轨迹模式（带调试）
# ============================================================================
def run_trace(params, seed=42):
    _, _, _, trace = run_single(params, seed, debug=True)
    return trace


# ============================================================================
# 六、命令行入口
# ============================================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Firefly OS 强反馈版')
    parser.add_argument('-n', '--runs', type=int, default=5000,
                        help='重复实验次数 (默认 5000)')
    parser.add_argument('-o', '--output', type=str, default='firefly_data.csv',
                        help='输出 CSV 文件名 (默认 firefly_data.csv)')
    parser.add_argument('--trace', action='store_true',
                        help='启用轨迹模式 (仅运行一次，输出 trace.csv 并打印调试信息)')
    args = parser.parse_args()

    if args.trace:
        print("启用轨迹模式（强反馈参数）...")
        trace = run_trace(DEFAULT_PARAMS)
        with open('trace.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['t', 'E', 'S', 'M', 'signal', 'cost_maintenance', 'cost_info', 'dead'])
            writer.writerows(trace)
        print("轨迹已保存至 trace.csv")
    else:
        print(f"运行 {args.runs} 次模拟（强反馈参数），输出至 {args.output} ...")
        data = run_experiment(DEFAULT_PARAMS, n_runs=args.runs)
        with open(args.output, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['lifetime', 'final_M', 'cause'])
            writer.writerows(data)
        print("完成。")