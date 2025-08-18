#!/usr/bin/env python3
"""
SQZMOM 指标专项调试器
专门测试 SqueezeMomentum 指标在 SUI 2H 数据上的 ZeroDivisionError
"""
import sys
import os
import pandas as pd
import backtrader as bt

# 添加路径
sys.path.append(os.path.dirname(__file__))
from indicators.sqzmom_safe import SqueezeMomentumSafe


class DebugSQZMOMStrategy(bt.Strategy):
    """仅用于测试 SQZMOM 指标的简化策略"""
    
    def __init__(self):
        print(f"[DEBUG] Initializing SQZMOM indicator...")
        
        # 创建 SQZMOM 指标，启用调试
        self.sqzmom = SqueezeMomentumSafe(
            self.data,
            bb_length=20,
            bb_mult=2.0,
            kc_length=20,
            kc_mult=1.5,
            use_true_range=True,
            debug=True  # 启用调试日志
        )
        
        print(f"[DEBUG] SQZMOM indicator created successfully")
    
    def next(self):
        """每个bar都打印SQZMOM的状态"""
        try:
            bar_num = len(self)
            if bar_num % 1000 == 0:  # 每1000个bar打印一次
                print(f"[DEBUG] Bar {bar_num}: SQZMOM processing...")
            
            # 强制访问所有SQZMOM的值以触发计算
            squeeze_on = self.sqzmom.lines.squeeze_on[0]
            squeeze_off = self.sqzmom.lines.squeeze_off[0]
            signal_bar = self.sqzmom.lines.signal_bar[0] 
            momentum = self.sqzmom.lines.momentum[0]
            
            # 检查异常值
            if abs(momentum) > 1000:
                print(f"[WARNING] Bar {bar_num}: Large momentum {momentum}")
            
        except Exception as e:
            print(f"[ERROR] Bar {len(self)}: {e}")
            print(f"[ERROR] Exception type: {type(e)}")
            import traceback
            traceback.print_exc()
            raise


def main():
    print("=" * 60)
    print("SQZMOM 指标专项调试 - SUI 2H 数据")
    print("=" * 60)
    
    # 数据文件路径
    data_file = "data/SUIUSDT/2h/SUIUSDT-2h-merged.csv"
    
    if not os.path.exists(data_file):
        print(f"错误: 数据文件不存在 {data_file}")
        return
    
    print(f"加载数据: {data_file}")
    
    # 读取数据
    df = pd.read_csv(data_file)
    print(f"数据行数: {len(df)}")
    print(f"列名: {df.columns.tolist()}")
    
    # 转换时间格式
    df['datetime'] = pd.to_datetime(df['open_time'], unit='ms')
    df.set_index('datetime', inplace=True)
    
    # 创建 Backtrader 数据源
    data = bt.feeds.PandasData(
        dataname=df,
        datetime=None,  # 使用索引
        open='open',
        high='high', 
        low='low',
        close='close',
        volume='volume',
        openinterest=None
    )
    
    # 创建 Cerebro
    cerebro = bt.Cerebro()
    cerebro.adddata(data)
    cerebro.addstrategy(DebugSQZMOMStrategy)
    
    print("开始运行 SQZMOM 调试测试...")
    
    try:
        results = cerebro.run()
        print("✅ SQZMOM 指标测试成功完成!")
        
    except Exception as e:
        print(f"❌ SQZMOM 指标测试失败: {e}")
        print(f"错误类型: {type(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()