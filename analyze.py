import pandas as pd
import glob
import re

print("🔍 自动扫描所有实验文件，按参数分组统计...\n")

# 1. 扫描所有CSV文件，提取文件名中的参数信息
all_files = glob.glob("firefly_*.csv")
if not all_files:
    print("❌ 没找到任何CSV实验文件！")
    exit()

# 2. 解析每个文件的参数和RUN编号（核心：自动提取ES/L/B等所有参数）
file_metadata = []
for f in all_files:
    # 正则匹配文件名中的参数：E..._S..._L..._ES..._B..._F..._RUN...
    match = re.match(
        r'firefly_E([\d\.]+)_S([\d\.]+)_L([\d\.]+)_ES([\d\.]+)_B([\d\.]+)_F([\d\.]+)_RUN(\d+)\.csv',
        f
    )
    if match:
        metadata = {
            'path': f,
            'E': float(match.group(1)),
            'S': float(match.group(2)),
            'L': float(match.group(3)),
            'ES': float(match.group(4)),  # 熵系数，自动提取
            'B': float(match.group(5)),
            'F': float(match.group(6)),
            'run_id': int(match.group(7))
        }
        file_metadata.append(metadata)
    else:
        print(f"⚠️ 跳过格式不符的文件：{f}")

if not file_metadata:
    print("❌ 没有找到符合命名规则的文件！请确保文件名是firefly_参数_RUNx.csv格式")
    exit()

# 3. 按完整参数组合分组（只要有一个参数不同，就算不同组）
df_meta = pd.DataFrame(file_metadata)
# 把参数组合转成字符串作为分组键（比如"ES=2.5,L=0.02,B=0.02"）
df_meta['param_group'] = df_meta.apply(
    lambda x: f"ES={x['ES']}, L={x['L']}, B={x['B']}", axis=1
)
unique_groups = df_meta['param_group'].unique()

print(f"✅ 检测到 {len(unique_groups)} 组不同参数的实验：")
for i, group in enumerate(unique_groups):
    count = len(df_meta[df_meta['param_group']==group])
    print(f"  组{i+1}: {group}（共{count}次实验）")
print("\n" + "="*80 + "\n")

# 4. 遍历每组参数，分别统计
for group_name in unique_groups:
    group_files = df_meta[df_meta['param_group'] == group_name]
    all_group_data = []
    
    for _, meta in group_files.iterrows():
        df = pd.read_csv(meta['path'])
        df['run_id'] = meta['run_id']
        all_group_data.append(df)
    
    combined_df = pd.concat(all_group_data, ignore_index=True)
    final_states = combined_df.groupby('run_id').last().reset_index()
    
    # 统计代谢崩溃首次出现步数
    collapse_events = combined_df[combined_df['is_collapse'] == 1]
    first_collapse_steps = collapse_events.groupby('run_id')['step'].min()
    
    # 输出该组的统计结果
    print(f"📊 统计结果：{group_name}")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"【核心寿命指标】")
    print(f"  实验次数：{len(final_states)}次")
    print(f"  平均死亡步数：{final_states['step'].mean():.1f} ± {final_states['step'].std():.1f}")
    print(f"  平均死亡时S值：{final_states['S'].mean():.3f}")
    print(f"\n【认知积累指标】")
    print(f"  M平均终值：{final_states['M'].mean():.6f} ± {final_states['M'].std():.6f}")
    print(f"  M终值范围：{final_states['M'].min():.6f} ~ {final_states['M'].max():.6f}")
    print(f"\n【代谢压力指标】")
    if not first_collapse_steps.empty:
        print(f"  代谢崩溃首次出现步数：{first_collapse_steps.mean():.1f} ± {first_collapse_steps.std():.1f}")
        print(f"  代谢崩溃最早出现步数：{first_collapse_steps.min():.0f}")
    else:
        print(f"  代谢崩溃首次出现步数：无")
    print(f"  最后一步代谢崩溃比例：{len(final_states[final_states['is_collapse']==1])/len(final_states)*100:.1f}%")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")


# 5. 可选：输出所有实验的参数汇总表（方便核对）
print("="*80)
print("📋 所有实验参数汇总表：")
param_summary = df_meta[['run_id', 'ES', 'L', 'B', 'path']].sort_values(by=['ES', 'run_id'])
print(param_summary.to_string(index=False))