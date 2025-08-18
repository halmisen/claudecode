#!/usr/bin/env python3
"""
Four Swords Debug Runner - 用于诊断ZeroDivisionError问题
"""
import argparse
import pandas as pd
import backtrader as bt
import sys
import os
from datetime import datetime

# 临时简化的WaveTrend指标
class SimpleWaveTrend(bt.Indicator):
    """简化版WaveTrend指标，移除复杂的除法运算"""
    lines = ('wt1', 'wt2', 'wt_signal')
    
    params = (
        ('n1', 10),
        ('n2', 21),
    )
    
    def __init__(self):
        # 使用更简单的计算方式
        self.ap = (self.data.high + self.data.low + self.data.close) / 3.0
        self.ema1 = bt.indicators.EMA(self.ap, period=self.params.n1)
        self.ema2 = bt.indicators.EMA(self.ema1, period=self.params.n1)
        
        # 简化的WT计算，避免复杂除法
        self.wt1 = (self.ap - self.ema2) * 100  # 乘以100而不是除法
        self.wt2 = bt.indicators.SMA(self.wt1, period=4)
        self.wt_signal = self.wt1 > self.wt2

    def next(self):
        self.lines.wt1[0] = self.wt1[0]
        self.lines.wt2[0] = self.wt2[0]
        self.lines.wt_signal[0] = float(self.wt_signal[0])


# 简化的Squeeze Momentum指标
class SimpleSqueezeMomentum(bt.Indicator):
    """简化版Squeeze Momentum指标"""
    lines = ('squeeze_on', 'squeeze_off', 'signal_bar', 'momentum')
    
    params = (
        ('bb_length', 20),
        ('bb_mult', 2.0),
        ('kc_length', 20),
        ('kc_mult', 1.5),
    )
    
    def __init__(self):
        # Bollinger Bands
        self.bb_basis = bt.indicators.SMA(self.data.close, period=self.params.bb_length)
        self.bb_dev = self.params.bb_mult * bt.indicators.StdDev(self.data.close, period=self.params.bb_length)
        self.bb_upper = self.bb_basis + self.bb_dev
        self.bb_lower = self.bb_basis - self.bb_dev
        
        # Keltner Channels  
        self.kc_ma = bt.indicators.SMA(self.data.close, period=self.params.kc_length)
        self.kc_range = bt.indicators.ATR(self.data, period=self.params.kc_length)
        self.kc_upper = self.kc_ma + self.kc_range * self.params.kc_mult
        self.kc_lower = self.kc_ma - self.kc_range * self.params.kc_mult
        
        # Squeeze conditions
        self.squeeze_on_cond = (self.bb_lower > self.kc_lower) & (self.bb_upper < self.kc_upper)
        
        # 简化的momentum计算
        self.momentum = bt.indicators.ROC(self.data.close, period=self.params.kc_length)

    def next(self):
        squeeze_on = bool(self.squeeze_on_cond[0])
        
        # 简化的signal bar逻辑
        prev_squeeze = False
        if len(self) > 1:
            prev_squeeze = bool(self.squeeze_on_cond[-1])
        
        signal_bar = prev_squeeze and not squeeze_on
        
        self.lines.squeeze_on[0] = float(squeeze_on)
        self.lines.squeeze_off[0] = float(not squeeze_on)
        self.lines.signal_bar[0] = float(signal_bar)
        self.lines.momentum[0] = self.momentum[0]


class DebugStrategy(bt.Strategy):
    """简化的调试策略"""
    
    params = (
        ('use_wt', True),
    )
    
    def __init__(self):
        print("初始化调试策略...")
        
        # 使用简化的指标
        self.sqzmom = SimpleSqueezeMomentum(self.data)
        
        if self.params.use_wt:
            print("初始化WaveTrend指标...")
            self.wavetrend = SimpleWaveTrend(self.data)
            print("WaveTrend指标初始化完成")
        
        print("策略初始化完成")
    
    def next(self):
        # 简单的逻辑检查
        if len(self) < 50:  # 跳过前50根K线
            return
            
        # 基本信号
        signal_bar = bool(self.sqzmom.lines.signal_bar[0])
        momentum = self.sqzmom.lines.momentum[0]
        
        if self.params.use_wt:
            wt_signal = bool(self.wavetrend.lines.wt_signal[0])
        else:
            wt_signal = True
        
        # 简单的入场逻辑
        if not self.position and signal_bar and momentum > 0 and wt_signal:
            self.buy(size=0.1)
        elif self.position and len(self) - getattr(self, 'entry_bar', 0) > 20:
            self.close()
            self.entry_bar = len(self)


def test_data_loading(data_file):
    """测试数据加载"""
    print(f"测试数据文件: {data_file}")
    
    try:
        df = pd.read_csv(data_file)
        print(f"数据行数: {len(df)}")
        print(f"列名: {list(df.columns)}")
        
        # 检查时间列
        if 'open_time' in df.columns:
            df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
            print(f"时间范围: {df['open_time'].min()} -> {df['open_time'].max()}")
        
        return True
    except Exception as e:
        print(f"数据加载错误: {e}")
        return False


def run_debug_test(data_file, use_wt=True):
    """运行调试测试"""
    print(f"\n=== 调试测试开始 ===")
    print(f"数据文件: {data_file}")
    print(f"使用WaveTrend: {use_wt}")
    
    # 测试数据加载
    if not test_data_loading(data_file):
        return False
    
    # 创建Cerebro实例
    cerebro = bt.Cerebro()
    
    # 添加策略
    cerebro.addstrategy(DebugStrategy, use_wt=use_wt)
    
    # 加载数据
    try:
        data = bt.feeds.GenericCSVData(
            dataname=data_file,
            dtformat=('%Y-%m-%d %H:%M:%S'),
            datetime=1,  # open_time列转换后的位置
            time=-1,
            open=2,
            high=3,
            low=4,
            close=5,
            volume=6,
            openinterest=-1,
        )
        
        # 先转换时间格式
        df = pd.read_csv(data_file)
        df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
        df['datetime'] = df['open_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # 重新排列列顺序
        df_bt = df[['datetime', 'datetime', 'open', 'high', 'low', 'close', 'volume']].copy()
        
        # 保存临时文件
        temp_file = data_file.replace('.csv', '_temp.csv')
        df_bt.to_csv(temp_file, index=False, header=False)
        
        data = bt.feeds.GenericCSVData(
            dataname=temp_file,
            dtformat=('%Y-%m-%d %H:%M:%S'),
            datetime=0,
            time=-1,
            open=2,
            high=3,
            low=4,
            close=5,
            volume=6,
            openinterest=-1,
        )
        
        cerebro.adddata(data)
        print("数据加载成功")
        
    except Exception as e:
        print(f"数据加载错误: {e}")
        return False
    
    # 设置初始资金
    cerebro.broker.setcash(500.0)
    
    try:
        print("开始运行回测...")
        results = cerebro.run()
        print("回测完成!")
        return True
        
    except Exception as e:
        print(f"回测运行错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 清理临时文件
        temp_file = data_file.replace('.csv', '_temp.csv')
        if os.path.exists(temp_file):
            os.remove(temp_file)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Four Swords Debug Runner')
    parser.add_argument('--data', required=True, help='CSV data file path')
    parser.add_argument('--no-wt', action='store_true', help='Disable WaveTrend indicator')
    
    args = parser.parse_args()
    
    print("=== Four Swords Debug Runner ===")
    
    # 首先测试不使用WaveTrend
    print("\n第一步: 测试不使用WaveTrend指标")
    success1 = run_debug_test(args.data, use_wt=False)
    
    if success1:
        print("✅ 不使用WaveTrend的测试成功")
        
        if not args.no_wt:
            print("\n第二步: 测试使用WaveTrend指标")
            success2 = run_debug_test(args.data, use_wt=True)
            
            if success2:
                print("✅ 使用WaveTrend的测试也成功")
                print("✅ 所有测试通过，问题可能在原始指标的复杂计算中")
            else:
                print("❌ WaveTrend指标导致问题")
        else:
            print("跳过WaveTrend测试")
    else:
        print("❌ 基础测试失败，问题在数据或基本设置中")


if __name__ == '__main__':
    main()