import numpy as np
import pandas as pd
import os

# ==================== 核心物理内核（和原文件100%对齐，不动）====================
def seeded_random(seed):
    def rng():
        nonlocal seed
        seed |= 0
        seed = seed * 16807 % 2147483647
        return (seed & 0x7fffffff) / 0x7fffffff
    return rng

def run_single(params, run_id, rng):
    E, S, F = 100.0, 0.1, 0.5
    M = 0.0
    prev_F = F
    for step in range(2000):
        sens = 1.0 / max(E, 1e-6)
        stability = 1.0 / (1.0 + M * params.get('k_stab', 10.0))
        action_cost = F * params['l'] * 100 * sens * stability
        maint_cost = params['base_metab'] * (1.0 + params['es'] * S ** 2)
        total_cost = action_cost + maint_cost
        E -= total_cost
        S += params['bs'] + total_cost * params.get('k_entropy', 0.015)
        F += (rng() * 0.1 - 0.05) * stability
        dF = abs(prev_F - F)
        if dF > params['df_th'] and E > 0:
            mem_eff = params['l'] * (1.0 - S)
            M += max(0.0, (dF * mem_eff) / (total_cost + 1e-9))
        if E <= 0.001 or S >= 0.999:
            return {'steps': step, 'final_M': M, 'is_elegant': maint_cost <= total_cost * 0.7}
        prev_F = F
    return {'steps': 2000, 'final_M': M, 'is_elegant': False}

# ==================== 剩余3个参数扫描配置（不用改）====================
SCAN_CONFIGS = [
    ('k_entropy', np.linspace(0.01, 0.03, 9)),   # 熵产系数：0.01~0.03
    ('base_metab', np.linspace(0.015, 0.025, 9)), # 基础代谢：0.015~0.025
    ('k_stab', np.linspace(1, 20, 10))            # 稳定系数：1~20
]

SEED = 42
RUNS_PER_POINT = 50
BASE_PARAMS = {
    'es': 2.5, 'bs': 0.02, 'l': 0.02, 'df_th': 0.03,
    'k_stab': 10.0, 'base_metab': 0.02
}

def sensitivity_scan(param_name, param_range):
    results = []
    rng = seeded_random(SEED)
    print(f"\n===== 扫描：{param_name} =====")
    for param_val in param_range:
        params = BASE_PARAMS.copy()
        params[param_name] = param_val
        # 基础代谢扫描时联动调兰道尔系数，保持43步锚点
        if param_name == 'base_metab':
            params['l'] = 0.0004 / param_val
        batch = [run_single(params, i, rng) for i in range(RUNS_PER_POINT)]
        steps = [r['steps'] for r in batch]
        Ms = [r['final_M'] for r in batch]
        results.append({
            'param_value': param_val,
            'avg_lifetime': np.mean(steps),
            'std_lifetime': np.std(steps),
            'avg_M': np.mean(Ms),
            'std_M': np.std(Ms)
        })
        print(f"✅ 参数={param_val:.4f} | 寿命={np.mean(steps):.1f}±{np.std(steps):.1f}步 | 平均M={np.mean(Ms):.4f}")
    pd.DataFrame(results).to_csv(f'firefly_scan_{param_name}.csv', index=False)
    print(f"✅ 结果保存至：firefly_scan_{param_name}.csv")
    return pd.DataFrame(results)

if __name__ == '__main__':
    os.makedirs('scan_raw_data', exist_ok=True)
    for param_name, param_range in SCAN_CONFIGS:
        sensitivity_scan(param_name, param_range)
    print("\n🎉 所有剩余参数扫描完成！运行 python analyze_scan.py 查看完整鲁棒性结论")