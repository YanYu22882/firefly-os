# firefly_os_v3.py — Firefly OS v3.3 "Batch Runner"
# 用法：直接 python firefly_os_v3.py，改顶部常量即可调参
import random
import time
import csv

# ==================== 实验配置（改这里就行）====================
NUM_RUNS    = 50          # 每批跑多少次（10/50/100）
SHOW_ANIM   = False       # True=慢放逐帧，False=秒出结果
MAX_STEPS   = 2000        # 安全闸上限

# ==================== 物理常量（核心规则，别乱改）====================
LANDAUER   = 0.02    # 兰道尔系数（信息擦除代价）
BASE_METAB = 0.02    # 基础代谢 β
ENTROPY_S  = 1     # 熵敏感系数 ES
DF_TH      = 0.03    # 记忆触发阈值 ΔF
BS         = 0.02    # 熵增系数
K_STAB     = 10.0    # 稳定系数（影响F抖动衰减）

INIT_E = 100.0
INIT_S = 0.10
INIT_F = 0.50

param_str = f"E{INIT_E:.2f}_S{INIT_S:.2f}_L{LANDAUER:.3f}_ES{ENTROPY_S:.1f}_B{BASE_METAB:.3f}_F{INIT_F:.2f}"

# ==================== 单步演化（核心物理，未动）====================
def tick(st, prev_F, prev_M):
    sens = 1.0 / max(st["E"], 1e-6)
    stability = 1.0 / (1.0 + prev_M * K_STAB)
    action_cost = st["F_raw"] * LANDAUER * 100 * sens * stability
    info_cost   = LANDAUER * abs(st["F_raw"] - 0.5)
    maint_cost  = BASE_METAB * (1 + ENTROPY_S * st["S"] ** 2)
    total_cost  = action_cost + info_cost + maint_cost

    st["E"] -= total_cost
    st["S"] += BS + total_cost * 0.015
    st["F_raw"] += random.uniform(-0.05, 0.05) * stability

    dF = prev_F - st["F_raw"]
    mem_eff = LANDAUER * (1 - st["S"])
    gained = 0.0
    if dF > DF_TH and st["E"] > 0:
        gained = (dF * mem_eff) / (total_cost + 1e-9)
        st["M"] += max(0, gained)

    prev_F_out = st["F_raw"]
    prev_M_out = st["M"]
    return total_cost, maint_cost, prev_F_out, prev_M_out, gained

# ==================== 终端渲染（动画用）====================
def render(st, t, cost, mcost, gained):
    bar_w = 30
    e_bar = "█" * int(st["E"]/100*bar_w) + "░"*(bar_w-int(st["E"]/100*bar_w))
    s_bar = "█" * int(st["S"]*bar_w) + "░"*(bar_w-int(st["S"]*bar_w))
    flag = ""
    if mcost > cost * 0.7:
        flag = " ⚠ METABOLIC COLLAPSE"
    if gained > 0:
        flag += " ★"
    print(f"t{str(t).zfill(4)} |E[{e_bar}] {st['E']:6.2f} |S[{s_bar}] {st['S']:6.3f} "
          f"|F {st['F_raw']:+.3f} |M {st['M']:.6f}{flag}")

# ==================== 主循环 ====================
if __name__ == "__main__":
    print(f"=== Firefly OS v3.3 | ES={ENTROPY_S} ΔF={DF_TH} β={BASE_METAB} RUNS={NUM_RUNS} ===\n")

    for run_id in range(NUM_RUNS):
        state = {"E": INIT_E, "S": INIT_S, "F_raw": INIT_F, "M": 0.0}
        prev_F = INIT_F
        prev_M = 0.0

        csv_name = f"firefly_{param_str}_RUN{run_id}.csv"
        print(f"--- RUN {run_id+1}/{NUM_RUNS} -> {csv_name} ---")

        with open(csv_name, 'w', newline='', encoding='utf-8-sig') as f:
            w = csv.writer(f)
            w.writerow(['step','E','S','F_raw','M','total_cost','maint_cost','is_collapse','has_memory_gain'])

            for step in range(MAX_STEPS):
                cost, mcost, prev_F, prev_M, gained = tick(state, prev_F, prev_M)
                w.writerow([
                    step, round(state['E'],6), round(state['S'],6), round(state['F_raw'],6), round(state['M'],6),
                    round(cost,6), round(mcost,6),
                    1 if mcost > cost*0.7 else 0,
                    1 if gained > 0 else 0
                ])

                if SHOW_ANIM:
                    render(state, step, cost, mcost, gained)
                    time.sleep(0.03)

                if state["E"] <= 0.001 or state["S"] >= 0.999:
                    print(f"  💀 终止 t={step} | E={state['E']:.4f} S={state['S']:.4f} M={state['M']:.6f}")
                    break
            else:
                print(f"  ⏳ 达MAX_STEPS={MAX_STEPS} | E={state['E']:.4f} S={state['S']:.4f} M={state['M']:.6f}")

    print(f"\n=== 完成 {NUM_RUNS} 次实验 ===")