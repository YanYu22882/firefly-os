"""
扫描结果统计分析脚本（批量读取CSV，输出鲁棒性结论）
"""
import pandas as pd
import glob
import os

def analyze_scan_results(scan_file):
    """分析单个扫描结果文件"""
    df = pd.read_csv(scan_file)
    print(f"\n📊 分析结果：{os.path.basename(scan_file)}")
    print(f"扫描参数：{df['param_value'].iloc[0]} ~ {df['param_value'].iloc[-1]}")
    print(f"平均寿命范围：{df['avg_lifetime'].min():.1f} ~ {df['avg_lifetime'].max():.1f}步")
    print(f"寿命波动率：{df['std_lifetime'].mean():.2f}步（越小越鲁棒）")
    print(f"平均M范围：{df['avg_M'].min():.4f} ~ {df['avg_M'].max():.4f}")
    
    
    # 判断鲁棒性
    lifetime_volatility = df['std_lifetime'].mean() / df['avg_lifetime'].mean() * 100
    if lifetime_volatility < 5:
        print(f"✅ 鲁棒性：强（寿命波动率{lifetime_volatility:.1f}% <5%）")
    elif lifetime_volatility < 20:
        print(f"⚠️ 鲁棒性：中（寿命波动率{lifetime_volatility:.1f}% 5%~20%）")
    else:
        print(f"❌ 鲁棒性：弱（寿命波动率{lifetime_volatility:.1f}% >20%）")

def analyze_all_scans():
    """批量分析所有扫描结果"""
    scan_files = glob.glob('firefly_scan_*.csv')
    if not scan_files:
        print("❌ 未找到扫描结果文件，请先运行scan_firefly.py")
        return
    for file in scan_files:
        analyze_scan_results(file)

if __name__ == '__main__':
    analyze_all_scans()