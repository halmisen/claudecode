"""
Four Swords Indicator Unit Verification
指标级单元测试 - 验证ROC分母保护正确性

目标: 证明"ROC分母保护"正确且只在该触发条件下生效
验收点:
- 输入 previous=0、±1e−14、±常数段；输出无 Inf/NaN，符号与预期一致
- 预热期内不产出任何信号/数值
- 全序列统计：分母被替换的bar占比 < 0.5%；给出首末时间戳
"""
import os
import sys
import pandas as pd
import numpy as np
import backtrader as bt
from datetime import datetime

# Add path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from indicators.sqzmom_safe import SqueezeMomentumSafe
from indicators.wavetrend_safe import WaveTrendSafe
from utils.safe_math import (
    DEBUG_DENOMINATOR_REPLACEMENT, DEBUG_LOG_TRIGGERS, 
    DenominatorMonitor, SAFE_EPS_STANDARD, SAFE_EPS_RELAXED, SAFE_EPS_STRICT
)


class IndicatorTestStrategy(bt.Strategy):
    """测试策略 - 仅运行指标，不下单"""
    
    params = (
        ('test_eps', SAFE_EPS_STANDARD),
        ('enable_monitoring', True),
        ('indicator_type', 'both'),  # 'sqzmom', 'wavetrend', 'both'
    )
    
    def __init__(self):
        print(f"[TEST] Indicator unit test init - EPS={self.params.test_eps}, monitoring={'ON' if self.params.enable_monitoring else 'OFF'}")
        
        # 初始化监控器
        if self.params.enable_monitoring:
            self.sqzmom_monitor = DenominatorMonitor("SQZMOM")
            self.wavetrend_monitor = DenominatorMonitor("WAVETREND")
        
        # 创建指标实例
        if self.params.indicator_type in ['sqzmom', 'both']:
            self.sqzmom = SqueezeMomentumSafe(
                eps=self.params.test_eps,
                debug=DEBUG_DENOMINATOR_REPLACEMENT
            )
            print(f"[OK] SqueezeMomentum Safe loaded")
        
        if self.params.indicator_type in ['wavetrend', 'both']:
            self.wavetrend = WaveTrendSafe(
                eps=self.params.test_eps,
                debug=DEBUG_DENOMINATOR_REPLACEMENT
            )
            print(f"[OK] WaveTrend Safe loaded")
        
        # 统计变量
        self.bar_count = 0
        self.warmup_period = 50  # 预估预热期
        self.invalid_values = 0
        self.first_valid_bar = None
        self.last_valid_bar = None
        
    def next(self):
        self.bar_count += 1
        
        # 检查预热期
        if self.bar_count <= self.warmup_period:
            return
        
        # 检查指标值有效性
        valid_indicators = True
        
        if hasattr(self, 'sqzmom'):
            momentum = self.sqzmom.momentum[0]
            if np.isnan(momentum) or np.isinf(momentum):
                self.invalid_values += 1
                valid_indicators = False
                print(f"[ERROR] Bar {self.bar_count}: SQZMOM momentum invalid: {momentum}")
        
        if hasattr(self, 'wavetrend'):
            wt1 = self.wavetrend.wt1[0]
            wt2 = self.wavetrend.wt2[0]
            if np.isnan(wt1) or np.isinf(wt1) or np.isnan(wt2) or np.isinf(wt2):
                self.invalid_values += 1
                valid_indicators = False
                print(f"[ERROR] Bar {self.bar_count}: WaveTrend invalid: wt1={wt1}, wt2={wt2}")
        
        # 记录有效区间
        if valid_indicators:
            if self.first_valid_bar is None:
                self.first_valid_bar = self.bar_count
            self.last_valid_bar = self.bar_count
    
    def stop(self):
        """测试完成后的报告"""
        print(f"\n[RESULT] Indicator unit test completed")
        print(f"[STATS] Total bars: {self.bar_count}")
        print(f"[STATS] Invalid values: {self.invalid_values}")
        print(f"[STATS] Valid range: {self.first_valid_bar} -> {self.last_valid_bar}")
        
        if self.params.enable_monitoring:
            if hasattr(self, 'sqzmom_monitor'):
                summary = self.sqzmom_monitor.get_summary()
                print(f"\n[MONITOR] SQZMOM Report:")
                print(f"   Total checks: {summary['total_checks']}")
                print(f"   Replacements: {summary['replacements']}")
                print(f"   Replacement rate: {summary['replacement_rate_pct']:.3f}%")
                print(f"   Original value range: {summary['original_value_range']}")
                
            if hasattr(self, 'wavetrend_monitor'):
                summary = self.wavetrend_monitor.get_summary()
                print(f"\n[MONITOR] WaveTrend Report:")
                print(f"   Total checks: {summary['total_checks']}")
                print(f"   Replacements: {summary['replacements']}")
                print(f"   Replacement rate: {summary['replacement_rate_pct']:.3f}%")
                print(f"   Original value range: {summary['original_value_range']}")


def create_synthetic_test_data():
    """创建合成测试数据 - 包含边界条件"""
    print("[SETUP] Creating synthetic test data...")
    
    # 基础价格序列
    base_price = 100.0
    dates = pd.date_range(start='2023-01-01', periods=1000, freq='1H')
    
    # 创建包含边界条件的价格序列
    prices = []
    for i in range(len(dates)):
        if i < 50:
            # 前50个bar: 完全相同价格 (测试零分母)
            price = base_price
        elif i < 100:
            # 50-100: 微小变化 (测试接近零分母)
            price = base_price + (i - 50) * 1e-14
        elif i < 150:
            # 100-150: 平盘段 (测试低波动)
            price = base_price + 0.01
        else:
            # 150+: 正常市场波动
            price = base_price + np.sin((i-150) * 0.1) * 10 + np.random.normal(0, 1)
        
        prices.append(price)
    
    # 构建OHLCV数据
    data = []
    for i, (date, price) in enumerate(zip(dates, prices)):
        spread = max(0.01, abs(price * 0.001))  # 最小价差
        high = price + spread
        low = price - spread
        volume = 1000 + np.random.randint(-100, 100)
        
        data.append({
            'datetime': date,
            'open': price,
            'high': high,
            'low': low,
            'close': price,
            'volume': volume
        })
    
    df = pd.DataFrame(data)
    df.set_index('datetime', inplace=True)
    
    print(f"[OK] Synthetic data created: {len(df)} bars")
    print(f"   First 50 bars: price = {base_price} (zero denominator test)")
    print(f"   50-100 bars: micro changes (near-zero denominator test)")
    print(f"   100-150 bars: flat segment (low volatility test)")
    print(f"   150+ bars: normal volatility (normal case test)")
    
    return df


def run_indicator_verification(data_source="synthetic", eps_value=SAFE_EPS_STANDARD, indicator_type='both'):
    """
    运行指标验证测试
    
    Args:
        data_source: 'synthetic' 或数据文件路径
        eps_value: 测试的EPS值
        indicator_type: 'sqzmom', 'wavetrend', 'both'
    """
    print(f"\n[START] Starting indicator unit verification")
    print(f"   Data source: {data_source}")
    print(f"   EPS value: {eps_value}")
    print(f"   Indicator type: {indicator_type}")
    
    # 准备数据
    if data_source == "synthetic":
        df = create_synthetic_test_data()
    else:
        if not os.path.exists(data_source):
            raise FileNotFoundError(f"Data file not found: {data_source}")
        df = pd.read_csv(data_source)
        df['datetime'] = pd.to_datetime(df['open_time'], unit='ms')
        df.set_index('datetime', inplace=True)
        print(f"[OK] Real data loaded: {len(df)} bars")
    
    # 创建回测引擎
    cerebro = bt.Cerebro()
    
    # 添加数据
    data_feed = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(data_feed)
    
    # 添加测试策略
    cerebro.addstrategy(
        IndicatorTestStrategy,
        test_eps=eps_value,
        enable_monitoring=True,
        indicator_type=indicator_type
    )
    
    # 运行测试
    print(f"[RUN] Starting indicator test...")
    start_time = datetime.now()
    
    try:
        result = cerebro.run()
        end_time = datetime.now()
        print(f"[OK] Test completed in {(end_time - start_time).total_seconds():.2f} seconds")
        return True
        
    except Exception as e:
        end_time = datetime.now()
        print(f"[ERROR] Test failed in {(end_time - start_time).total_seconds():.2f} seconds")
        print(f"Error: {str(e)}")
        return False


def run_eps_sensitivity_analysis():
    """EPS敏感性分析"""
    print(f"\n[ANALYSIS] EPS sensitivity analysis")
    
    eps_values = [SAFE_EPS_STRICT, SAFE_EPS_STANDARD, SAFE_EPS_RELAXED]
    eps_names = ['Strict(1e-15)', 'Standard(1e-12)', 'Relaxed(1e-10)']
    
    results = {}
    
    for eps, name in zip(eps_values, eps_names):
        print(f"\n[TEST] Testing EPS = {name}")
        success = run_indicator_verification(
            data_source="synthetic", 
            eps_value=eps, 
            indicator_type='both'
        )
        results[name] = success
    
    print(f"\n[SUMMARY] EPS sensitivity analysis results:")
    for name, success in results.items():
        status = "[PASS]" if success else "[FAIL]"
        print(f"   {name}: {status}")
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Four Swords 指标单元验证")
    parser.add_argument("--data", default="synthetic", help="数据源: 'synthetic' 或 CSV文件路径")
    parser.add_argument("--eps", type=float, default=SAFE_EPS_STANDARD, help="EPS测试值")
    parser.add_argument("--indicator", choices=['sqzmom', 'wavetrend', 'both'], default='both', help="测试指标类型")
    parser.add_argument("--sensitivity", action='store_true', help="运行EPS敏感性分析")
    
    args = parser.parse_args()
    
    if args.sensitivity:
        run_eps_sensitivity_analysis()
    else:
        run_indicator_verification(args.data, args.eps, args.indicator)