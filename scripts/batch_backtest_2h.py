#!/usr/bin/env python3
"""
批量2h回测脚本 - 并行执行所有币种的回测
"""
import subprocess
import threading
import time
from datetime import datetime
import os

 
# 配置所有要回测的币种
SYMBOLS = [
    'BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'XRPUSDT', 
    'SUIUSDT', '1000PEPEUSDT', 'AAVEUSDT', 'WLDUSDT', 'DOGEUSDT'
]

# 基础配置
BASE_CONFIG = {
    'initial_cash': 500,
    'leverage': 4,
    'risk_pct': 0.20,
    'order_style': 'maker',
    'commission': 0.0002,
    'limit_offset': 0.0,
    'no_ema_filter': True,
    'no_volume_filter': True,
    'no_wt_filter': True,
    'write_meta': 1
}

def run_backtest(symbol):
    """运行单个币种的回测"""
    print(f"开始回测 {symbol}...")
    start_time = time.time()
    
    # 构建命令
    cmd = [
        "../backtester/venv/Scripts/python.exe",
        "run_four_swords_v1_7_4.py",
        "--data", f"data/{symbol}/2h/{symbol}-2h-merged.csv",
        "--initial_cash", str(BASE_CONFIG['initial_cash']),
        "--leverage", str(BASE_CONFIG['leverage']),
        "--risk_pct", str(BASE_CONFIG['risk_pct']),
        "--order_style", BASE_CONFIG['order_style'],
        "--commission", str(BASE_CONFIG['commission']),
        "--limit_offset", str(BASE_CONFIG['limit_offset']),
        "--html", f"../results/2h_comprehensive_backtest/{symbol}_2h_baseline.html",
        "--summary_csv", "../results/2h_comprehensive_backtest/test_summary_2h.csv",
        "--write_meta", str(BASE_CONFIG['write_meta'])
    ]
    
    # 添加过滤器开关
    if BASE_CONFIG['no_ema_filter']:
        cmd.append("--no_ema_filter")
    if BASE_CONFIG['no_volume_filter']:
        cmd.append("--no_volume_filter")
    if BASE_CONFIG['no_wt_filter']:
        cmd.append("--no_wt_filter")
    
    try:
        # 执行回测
        result = subprocess.run(cmd, cwd="backtester", capture_output=True, text=True, timeout=600)
        
        duration = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ {symbol} 回测完成 ({duration:.1f}s)")
        else:
            print(f"❌ {symbol} 回测失败: {result.stderr[:200]}")
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {symbol} 回测超时 (>10分钟)")
    except Exception as e:
        print(f"💥 {symbol} 回测异常: {str(e)}")

def main():
    print("=" * 70)
    print("2H 综合回测系统")
    print("=" * 70)
    print(f"回测币种: {', '.join(SYMBOLS)}")
    print(f"时间周期: 2h")
    print(f"配置: {BASE_CONFIG['initial_cash']} USDT, {BASE_CONFIG['leverage']}x杠杆, {BASE_CONFIG['order_style']}模式")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 创建结果目录
    os.makedirs("results/2h_comprehensive_backtest", exist_ok=True)
    
    # 并行执行回测
    threads = []
    for symbol in SYMBOLS:
        thread = threading.Thread(target=run_backtest, args=(symbol,))
        thread.start()
        threads.append(thread)
        time.sleep(2)  # 错开启动时间避免资源竞争
    
    # 等待所有回测完成
    for thread in threads:
        thread.join()
    
    print()
    print("=" * 70)
    print("所有回测完成!")
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("结果文件: results/2h_comprehensive_backtest/test_summary_2h.csv")
    print("=" * 70)

if __name__ == "__main__":
    main()
