#!/usr/bin/env python3
"""
数据预处理器 - 解决ZeroDivisionError的根本途径
在数据层面处理可能导致零值除法的问题
"""
import pandas as pd
import numpy as np
import argparse
import os

def preprocess_ohlcv_data(input_file, output_file=None, min_price_change=1e-8, min_volume=1.0):
    """
    预处理OHLCV数据，防止技术指标计算中的零值除法
    
    Parameters:
    - input_file: 输入CSV文件路径
    - output_file: 输出CSV文件路径（如果为None，则覆盖原文件）
    - min_price_change: 最小价格变动（避免完全平盘）
    - min_volume: 最小成交量
    """
    print(f"预处理数据文件: {input_file}")
    
    # 读取数据
    df = pd.read_csv(input_file)
    original_len = len(df)
    print(f"原始数据行数: {original_len}")
    
    # 1. 处理价格数据
    print("处理价格数据...")
    
    # 检查并修复OHLC关系异常
    invalid_ohlc = (df['high'] < df['low']) | (df['close'] < df['low']) | (df['close'] > df['high'])
    if invalid_ohlc.sum() > 0:
        print(f"修复 {invalid_ohlc.sum()} 条OHLC关系异常的记录")
        # 使用收盘价作为所有价格的基准
        df.loc[invalid_ohlc, 'high'] = df.loc[invalid_ohlc, 'close']
        df.loc[invalid_ohlc, 'low'] = df.loc[invalid_ohlc, 'close']
        df.loc[invalid_ohlc, 'open'] = df.loc[invalid_ohlc, 'close']
    
    # 2. 处理零价差问题（H=L的情况）
    zero_range = (df['high'] == df['low'])
    if zero_range.sum() > 0:
        print(f"处理 {zero_range.sum()} 条零价差记录")
        # 为零价差的K线添加微小波动
        base_price = df.loc[zero_range, 'close']
        price_adjustment = base_price * min_price_change
        
        df.loc[zero_range, 'high'] = base_price + price_adjustment
        df.loc[zero_range, 'low'] = base_price - price_adjustment
    
    # 3. 处理极小价格变动
    price_range = df['high'] - df['low']
    relative_range = price_range / df['close']
    tiny_range = relative_range < min_price_change
    
    if tiny_range.sum() > 0:
        print(f"增强 {tiny_range.sum()} 条极小变动记录")
        base_price = df.loc[tiny_range, 'close']
        min_adjustment = base_price * min_price_change
        
        df.loc[tiny_range, 'high'] = base_price + min_adjustment
        df.loc[tiny_range, 'low'] = base_price - min_adjustment
    
    # 4. 处理零成交量问题
    zero_volume = (df['volume'] <= 0)
    if zero_volume.sum() > 0:
        print(f"处理 {zero_volume.sum()} 条零成交量记录")
        df.loc[zero_volume, 'volume'] = min_volume
    
    # 5. 处理极小成交量
    tiny_volume = (df['volume'] < min_volume) & (df['volume'] > 0)
    if tiny_volume.sum() > 0:
        print(f"调整 {tiny_volume.sum()} 条极小成交量记录")
        df.loc[tiny_volume, 'volume'] = min_volume
    
    # 6. 平滑连续相同价格的问题
    close_diff = df['close'].diff().abs()
    constant_price_runs = (close_diff == 0).rolling(window=10).sum() >= 8  # 连续8个或以上相同价格
    
    if constant_price_runs.sum() > 0:
        print(f"平滑 {constant_price_runs.sum()} 处长时间平盘区域")
        # 为连续平盘添加微小随机波动
        np.random.seed(42)  # 确保可重复性
        random_factor = np.random.normal(0, min_price_change/2, constant_price_runs.sum())
        
        base_prices = df.loc[constant_price_runs, 'close']
        price_noise = base_prices * random_factor
        
        df.loc[constant_price_runs, 'close'] += price_noise
        df.loc[constant_price_runs, 'high'] = np.maximum(
            df.loc[constant_price_runs, 'high'], 
            df.loc[constant_price_runs, 'close']
        )
        df.loc[constant_price_runs, 'low'] = np.minimum(
            df.loc[constant_price_runs, 'low'], 
            df.loc[constant_price_runs, 'close']
        )
    
    # 7. 最终验证
    print("最终验证...")
    final_zero_range = ((df['high'] - df['low']).abs() < min_price_change/10).sum()
    final_zero_volume = (df['volume'] <= 0).sum()
    final_invalid_ohlc = (df['high'] < df['low']).sum()
    
    print(f"剩余零价差记录: {final_zero_range}")
    print(f"剩余零成交量记录: {final_zero_volume}")
    print(f"剩余OHLC异常记录: {final_invalid_ohlc}")
    
    # 8. 保存结果
    if output_file is None:
        output_file = input_file
    
    df.to_csv(output_file, index=False)
    print(f"预处理完成，保存到: {output_file}")
    
    # 9. 生成报告
    print(f"\n预处理报告:")
    print(f"原始记录数: {original_len}")
    print(f"处理后记录数: {len(df)}")
    print(f"数据完整性: {'OK' if final_zero_range == 0 and final_zero_volume == 0 else 'ISSUE'}")
    
    return output_file

def batch_preprocess(symbol_list, data_dir="data", interval="2h"):
    """批量预处理多个币种的数据"""
    print(f"=== 批量预处理 {len(symbol_list)} 个币种 ===")
    
    results = []
    for symbol in symbol_list:
        input_file = f"{data_dir}/{symbol}/{interval}/{symbol}-{interval}-merged.csv"
        
        if os.path.exists(input_file):
            try:
                output_file = preprocess_ohlcv_data(input_file)
                results.append({'symbol': symbol, 'status': 'success', 'file': output_file})
                print(f"SUCCESS {symbol} 预处理完成")
            except Exception as e:
                print(f"ERROR {symbol} 预处理失败: {e}")
                results.append({'symbol': symbol, 'status': 'error', 'error': str(e)})
        else:
            print(f"MISSING {symbol} 数据文件不存在: {input_file}")
            results.append({'symbol': symbol, 'status': 'missing', 'file': input_file})
        
        print("-" * 50)
    
    # 汇总报告
    print(f"\n=== 批量预处理汇总 ===")
    success_count = sum(1 for r in results if r['status'] == 'success')
    error_count = sum(1 for r in results if r['status'] == 'error')
    missing_count = sum(1 for r in results if r['status'] == 'missing')
    
    print(f"成功: {success_count}, 错误: {error_count}, 缺失: {missing_count}")
    
    return results

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='OHLCV数据预处理器')
    parser.add_argument('--file', help='单个文件预处理')
    parser.add_argument('--symbol', help='单个币种预处理')
    parser.add_argument('--batch', action='store_true', help='批量预处理问题币种')
    parser.add_argument('--output', help='输出文件路径')
    parser.add_argument('--min_price_change', type=float, default=1e-8, help='最小价格变动比例')
    parser.add_argument('--min_volume', type=float, default=1.0, help='最小成交量')
    
    args = parser.parse_args()
    
    if args.file:
        # 单文件处理
        preprocess_ohlcv_data(
            args.file, 
            args.output, 
            args.min_price_change, 
            args.min_volume
        )
    
    elif args.symbol:
        # 单币种处理
        input_file = f"data/{args.symbol}/2h/{args.symbol}-2h-merged.csv"
        if os.path.exists(input_file):
            preprocess_ohlcv_data(
                input_file, 
                args.output, 
                args.min_price_change, 
                args.min_volume
            )
        else:
            print(f"文件不存在: {input_file}")
    
    elif args.batch:
        # 批量处理问题币种
        problem_symbols = ['SUIUSDT', 'XRPUSDT', 'DOGEUSDT']
        batch_preprocess(problem_symbols)
    
    else:
        print("请使用 --file, --symbol, 或 --batch 参数")
        print("示例:")
        print("  python data_preprocessor.py --symbol SUIUSDT")
        print("  python data_preprocessor.py --batch")
        print("  python data_preprocessor.py --file data.csv --output clean_data.csv")

if __name__ == '__main__':
    main()