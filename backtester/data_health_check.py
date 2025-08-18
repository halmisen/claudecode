#!/usr/bin/env python3
"""
数据质量体检工具 - 检查零值、极小波动、重复时间戳等问题
根据用户分析建议实现
"""
import pandas as pd
import numpy as np
import argparse
import os

def check_data_health(file_path, symbol_name):
    """检查数据质量的核心问题"""
    print(f"\n=== 数据体检报告: {symbol_name} ===")
    print(f"文件: {file_path}")
    
    try:
        # 读取数据
        df = pd.read_csv(file_path)
        print(f"数据行数: {len(df)}")
        print(f"列名: {list(df.columns)}")
        
        # 时间处理
        if 'open_time' in df.columns:
            df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
            df = df.sort_values('open_time')
            print(f"时间范围: {df['open_time'].min()} -> {df['open_time'].max()}")
        
        # 1) 零/负/缺失值检查
        print(f"\n1. 零值和异常值检查:")
        print(f"   零成交量: {(df['volume'] == 0).sum()} 条 ({(df['volume'] == 0).mean()*100:.2f}%)")
        print(f"   负成交量: {(df['volume'] < 0).sum()} 条")
        print(f"   零价差(H=L): {((df['high']-df['low']).abs() == 0).sum()} 条 ({((df['high']-df['low']).abs() == 0).mean()*100:.2f}%)")
        print(f"   异常价格(H<L): {(df['high'] < df['low']).sum()} 条")
        print(f"   异常价格(C<0): {(df['close'] < 0).sum()} 条")
        print(f"   缺失值总数: {df.isnull().sum().sum()}")
        
        # 2) 极小波动占比
        eps = 1e-12
        price_range = (df['high'] - df['low']).abs()
        near_zero_range = (price_range < eps).sum()
        print(f"\n2. 极小波动检查:")
        print(f"   价差 < {eps}: {near_zero_range} 条 ({near_zero_range/len(df)*100:.2f}%)")
        
        # 更实用的极小波动检查（相对价差）
        relative_range = price_range / df['close']
        tiny_moves = (relative_range < 1e-6).sum()  # 0.0001% 以下的价格变动
        print(f"   相对价差 < 0.0001%: {tiny_moves} 条 ({tiny_moves/len(df)*100:.2f}%)")
        
        # 3) 重复和连续性检查
        print(f"\n3. 时间序列检查:")
        if 'open_time' in df.columns:
            dups = df['open_time'].duplicated().sum()
            print(f"   重复时间戳: {dups} 条")
            
            # 检查时间间隔
            time_diffs = df['open_time'].diff().dt.total_seconds() / 3600  # 小时
            expected_interval = 2.0  # 2小时
            irregular_intervals = ((time_diffs != expected_interval) & (time_diffs.notna())).sum()
            print(f"   非标准时间间隔: {irregular_intervals} 条")
            if irregular_intervals > 0:
                print(f"   时间间隔范围: {time_diffs.min():.2f}h - {time_diffs.max():.2f}h")
        
        # 4) 常数段检查（连续相同价格）
        print(f"\n4. 常数段检查:")
        constant_close = 0
        constant_high_low = 0
        
        if len(df) > 1:
            # 检查连续相同收盘价
            close_diff = df['close'].diff().abs()
            constant_close = (close_diff == 0).sum()
            
            # 检查H=L=C的情况
            hlc_equal = ((df['high'] == df['low']) & (df['low'] == df['close'])).sum()
            constant_high_low = hlc_equal
            
        print(f"   连续相同收盘价: {constant_close} 条 ({constant_close/len(df)*100:.2f}%)")
        print(f"   H=L=C (完全平盘): {constant_high_low} 条 ({constant_high_low/len(df)*100:.2f}%)")
        
        # 5) 统计摘要
        print(f"\n5. 数据统计摘要:")
        print(f"   平均成交量: {df['volume'].mean():.2f}")
        print(f"   平均价差: {(df['high']-df['low']).mean():.6f}")
        print(f"   平均相对价差: {((df['high']-df['low'])/df['close']).mean()*100:.4f}%")
        
        # 6) 风险评估
        print(f"\n6. ZeroDivisionError风险评估:")
        risk_score = 0
        risk_factors = []
        
        if (df['volume'] == 0).mean() > 0.01:  # 超过1%零成交量
            risk_score += 3
            risk_factors.append("高零成交量比例")
        
        if ((df['high']-df['low']).abs() == 0).mean() > 0.001:  # 超过0.1%零价差
            risk_score += 5
            risk_factors.append("存在零价差K线")
        
        if tiny_moves/len(df) > 0.05:  # 超过5%极小波动
            risk_score += 2
            risk_factors.append("高极小波动比例")
        
        if constant_high_low/len(df) > 0.001:  # 超过0.1%完全平盘
            risk_score += 4
            risk_factors.append("存在完全平盘K线")
        
        # 评估结果
        if risk_score == 0:
            risk_level = "低风险 ✅"
        elif risk_score <= 3:
            risk_level = "中等风险 ⚠️"
        else:
            risk_level = "高风险 ❌"
        
        print(f"   风险等级: {risk_level} (评分: {risk_score})")
        if risk_factors:
            print(f"   风险因素: {', '.join(risk_factors)}")
        
        return {
            'symbol': symbol_name,
            'total_rows': len(df),
            'zero_volume_pct': (df['volume'] == 0).mean() * 100,
            'zero_range_pct': ((df['high']-df['low']).abs() == 0).mean() * 100,
            'tiny_moves_pct': tiny_moves/len(df) * 100,
            'constant_hlc_pct': constant_high_low/len(df) * 100,
            'risk_score': risk_score,
            'risk_level': risk_level,
            'risk_factors': risk_factors
        }
        
    except Exception as e:
        print(f"数据检查错误: {e}")
        return None

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='数据质量体检工具')
    parser.add_argument('--symbol', help='单个币种检查')
    parser.add_argument('--all', action='store_true', help='检查所有问题币种')
    
    args = parser.parse_args()
    
    # 问题币种列表
    problem_symbols = ['SUIUSDT', 'XRPUSDT', 'DOGEUSDT']
    
    results = []
    
    if args.all:
        print("=== 批量数据体检 ===")
        for symbol in problem_symbols:
            data_file = f"data/{symbol}/2h/{symbol}-2h-merged.csv"
            if os.path.exists(data_file):
                result = check_data_health(data_file, symbol)
                if result:
                    results.append(result)
            else:
                print(f"\n文件不存在: {data_file}")
    
    elif args.symbol:
        symbol = args.symbol.upper()
        data_file = f"data/{symbol}/2h/{symbol}-2h-merged.csv"
        if os.path.exists(data_file):
            result = check_data_health(data_file, symbol)
            if result:
                results.append(result)
        else:
            print(f"文件不存在: {data_file}")
    
    else:
        print("请使用 --symbol SYMBOL 或 --all 参数")
        return
    
    # 生成汇总报告
    if results:
        print(f"\n" + "="*60)
        print("汇总报告")
        print("="*60)
        print(f"{'Symbol':<12} {'Risk':<12} {'ZeroVol%':<10} {'ZeroRange%':<12} {'TinyMove%':<12}")
        print("-"*60)
        
        for r in results:
            print(f"{r['symbol']:<12} {r['risk_level'][:6]:<12} {r['zero_volume_pct']:<10.2f} "
                  f"{r['zero_range_pct']:<12.4f} {r['tiny_moves_pct']:<12.2f}")
        
        # 推荐修复策略
        high_risk_symbols = [r['symbol'] for r in results if r['risk_score'] > 3]
        if high_risk_symbols:
            print(f"\n高风险币种需要数据预处理: {', '.join(high_risk_symbols)}")
            print("建议修复措施:")
            print("1. 在WaveTrend指标中添加eps保护")
            print("2. 在SqueezeMomentum中添加范围检查") 
            print("3. 增加warmup期数，避免初期计算不稳定")

if __name__ == '__main__':
    main()