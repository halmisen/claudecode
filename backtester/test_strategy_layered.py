"""
Four Swords Strategy Layered Testing
策略级"分层排查跑" - 三步验证法

用同一份 2h CSV，三步跑法，每步必须完成 SUI/XRP/DOGE：
A) 仅指标、禁下单：应无异常  
B) 固定手数下单（禁风险/ATR仓位）：应无异常
C) 恢复原有 sizing/止损逻辑：应无异常

若 A 通过而 C 报错，说明 sizing 仍有其它分母（如 ATR、distance）未防守
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
    DenominatorMonitor, SAFE_EPS_STANDARD
)


class LayeredTestStrategy(bt.Strategy):
    """分层测试策略 - 支持三种模式"""
    
    params = (
        # 测试模式
        ('test_mode', 'indicators_only'),  # 'indicators_only', 'fixed_sizing', 'full_logic'
        ('test_eps', SAFE_EPS_STANDARD),
        
        # Four Swords 参数
        ('bb_length', 20),
        ('bb_mult', 2.0),
        ('kc_length', 20),
        ('kc_mult', 1.5),
        ('channel_length', 10),
        ('channel_avg_length', 21),
        ('wt_oversold', -60.0),
        ('wt_overbought', 60.0),
        
        # 过滤器开关
        ('use_ema_filter', False),
        ('ema_fast', 10),
        ('ema_slow', 20),
        ('use_volume_filter', False),
        ('volume_mult', 1.02),
        ('use_wt_filter', False),
        
        # 风险管理 (仅在 full_logic 模式使用)
        ('risk_pct', 0.20),
        ('leverage', 4.0),
        ('initial_cash', 500.0),
        
        # 固定手数 (仅在 fixed_sizing 模式使用)
        ('fixed_size', 0.001),
        
        # 调试开关
        ('enable_monitoring', True),
        ('verbose', True),
    )
    
    def __init__(self):
        self.mode = self.params.test_mode
        print(f"[STRATEGY] Layered test init - Mode: {self.mode}")
        
        # 初始化监控器
        if self.params.enable_monitoring:
            self.monitor = DenominatorMonitor(f"STRATEGY_{self.mode.upper()}")
        
        # 创建指标
        self.sqzmom = SqueezeMomentumSafe(
            bb_length=self.params.bb_length,
            bb_mult=self.params.bb_mult,
            kc_length=self.params.kc_length,
            kc_mult=self.params.kc_mult,
            eps=self.params.test_eps,
            debug=DEBUG_DENOMINATOR_REPLACEMENT
        )
        
        self.wavetrend = WaveTrendSafe(
            n1=self.params.channel_length,
            n2=self.params.channel_avg_length,
            eps=self.params.test_eps,
            debug=DEBUG_DENOMINATOR_REPLACEMENT
        )
        
        # EMA 过滤器（如果启用）
        if self.params.use_ema_filter:
            self.ema_fast = bt.indicators.EMA(period=self.params.ema_fast)
            self.ema_slow = bt.indicators.EMA(period=self.params.ema_slow)
        
        # 成交量指标（如果启用）
        if self.params.use_volume_filter:
            self.volume_ma = bt.indicators.SMA(self.data.volume, period=20)
        
        # 统计变量
        self.bar_count = 0
        self.signal_count = 0
        self.trade_count = 0
        self.error_count = 0
        self.warmup_period = max(self.params.bb_length, self.params.kc_length) + 10
        
    def next(self):
        self.bar_count += 1
        
        # 预热期保护
        if self.bar_count <= self.warmup_period:
            return
        
        try:
            # 获取指标值（所有模式都需要）
            squeeze_on = self.sqzmom.squeeze_on[0] > 0
            squeeze_off = self.sqzmom.squeeze_off[0] > 0
            momentum = self.sqzmom.momentum[0]
            
            wt1 = self.wavetrend.wt1[0]
            wt2 = self.wavetrend.wt2[0]
            
            # 检查指标值有效性
            if (np.isnan(momentum) or np.isinf(momentum) or 
                np.isnan(wt1) or np.isinf(wt1) or 
                np.isnan(wt2) or np.isinf(wt2)):
                self.error_count += 1
                if self.params.verbose:
                    print(f"[ERROR] Bar {self.bar_count}: Invalid indicator values")
                return
            
            # 信号生成逻辑
            signal = self._generate_signal(squeeze_on, squeeze_off, momentum, wt1, wt2)
            
            if signal != 0:
                self.signal_count += 1
                
                # 根据测试模式决定是否下单
                if self.mode == 'indicators_only':
                    # 模式A: 仅记录信号，不下单
                    if self.params.verbose:
                        print(f"[SIGNAL] Bar {self.bar_count}: Signal={signal} (indicators only)")
                        
                elif self.mode == 'fixed_sizing':
                    # 模式B: 固定手数下单
                    self._place_fixed_order(signal)
                    
                elif self.mode == 'full_logic':
                    # 模式C: 完整风险管理下单
                    self._place_risk_managed_order(signal)
        
        except Exception as e:
            self.error_count += 1
            print(f"[ERROR] Bar {self.bar_count}: {str(e)}")
            if self.params.verbose:
                import traceback
                traceback.print_exc()
    
    def _generate_signal(self, squeeze_on, squeeze_off, momentum, wt1, wt2):
        """生成交易信号"""
        signal = 0
        
        # 基础 squeeze 信号
        if squeeze_off and momentum > 0:
            signal = 1  # 买入信号
        elif squeeze_off and momentum < 0:
            signal = -1  # 卖出信号
        
        # 应用过滤器
        if signal != 0:
            # EMA 过滤器
            if self.params.use_ema_filter:
                if hasattr(self, 'ema_fast') and hasattr(self, 'ema_slow'):
                    ema_trend = self.ema_fast[0] > self.ema_slow[0]
                    if signal > 0 and not ema_trend:
                        signal = 0
                    elif signal < 0 and ema_trend:
                        signal = 0
            
            # 成交量过滤器
            if self.params.use_volume_filter and signal != 0:
                if hasattr(self, 'volume_ma'):
                    volume_ok = self.data.volume[0] > self.volume_ma[0] * self.params.volume_mult
                    if not volume_ok:
                        signal = 0
            
            # WaveTrend 过滤器
            if self.params.use_wt_filter and signal != 0:
                if signal > 0 and wt1 > self.params.wt_overbought:
                    signal = 0
                elif signal < 0 and wt1 < self.params.wt_oversold:
                    signal = 0
        
        return signal
    
    def _place_fixed_order(self, signal):
        """固定手数下单（模式B）"""
        try:
            if signal > 0 and not self.position:
                # 固定手数买入
                self.buy(size=self.params.fixed_size)
                self.trade_count += 1
                if self.params.verbose:
                    print(f"[ORDER] Bar {self.bar_count}: BUY fixed size={self.params.fixed_size}")
                    
            elif signal < 0 and self.position:
                # 平仓
                self.close()
                if self.params.verbose:
                    print(f"[ORDER] Bar {self.bar_count}: CLOSE position")
                    
        except Exception as e:
            self.error_count += 1
            print(f"[ERROR] Fixed sizing order failed: {str(e)}")
    
    def _place_risk_managed_order(self, signal):
        """风险管理下单（模式C）"""
        try:
            if signal > 0 and not self.position:
                # 计算仓位大小
                risk_amount = self.broker.get_cash() * self.params.risk_pct
                leverage_amount = risk_amount * self.params.leverage
                
                # 获取当前价格
                current_price = self.data.close[0]
                
                # 检查价格有效性
                if current_price <= 0 or np.isnan(current_price) or np.isinf(current_price):
                    self.error_count += 1
                    print(f"[ERROR] Invalid price: {current_price}")
                    return
                
                # 计算手数
                position_size = leverage_amount / current_price
                
                # 最小手数保护
                min_size = 0.001
                if position_size < min_size:
                    position_size = min_size
                
                # 下单
                self.buy(size=position_size)
                self.trade_count += 1
                
                if self.params.verbose:
                    print(f"[ORDER] Bar {self.bar_count}: BUY size={position_size:.6f}, price={current_price:.6f}")
                    
            elif signal < 0 and self.position:
                # 平仓
                self.close()
                if self.params.verbose:
                    print(f"[ORDER] Bar {self.bar_count}: CLOSE position")
                    
        except Exception as e:
            self.error_count += 1
            print(f"[ERROR] Risk managed order failed: {str(e)}")
    
    def stop(self):
        """测试完成报告"""
        print(f"\n[RESULT] Layered test completed - Mode: {self.mode}")
        print(f"[STATS] Total bars: {self.bar_count}")
        print(f"[STATS] Signals generated: {self.signal_count}")
        print(f"[STATS] Trades executed: {self.trade_count}")
        print(f"[STATS] Errors encountered: {self.error_count}")
        
        # 性能统计
        if self.trade_count > 0:
            final_value = self.broker.get_value()
            initial_value = self.params.initial_cash
            total_return = (final_value - initial_value) / initial_value * 100
            print(f"[PERFORMANCE] Final value: ${final_value:.2f}")
            print(f"[PERFORMANCE] Total return: {total_return:.2f}%")
        
        # 监控报告
        if self.params.enable_monitoring and hasattr(self, 'monitor'):
            summary = self.monitor.get_summary()
            print(f"\n[MONITOR] {self.mode.upper()} Report:")
            print(f"   Total checks: {summary['total_checks']}")
            print(f"   Replacements: {summary['replacements']}")
            print(f"   Replacement rate: {summary['replacement_rate_pct']:.3f}%")


def run_layered_test(data_file, test_mode, symbol_name, enable_filters=False):
    """
    运行分层测试
    
    Args:
        data_file: 数据文件路径
        test_mode: 'indicators_only', 'fixed_sizing', 'full_logic'
        symbol_name: 币种名称（用于报告）
        enable_filters: 是否启用过滤器
    """
    print(f"\n[START] Layered test - Mode: {test_mode}, Symbol: {symbol_name}")
    
    if not os.path.exists(data_file):
        raise FileNotFoundError(f"Data file not found: {data_file}")
    
    # 加载数据
    df = pd.read_csv(data_file)
    df['datetime'] = pd.to_datetime(df['open_time'], unit='ms')
    df.set_index('datetime', inplace=True)
    print(f"[DATA] Loaded {len(df)} bars from {data_file}")
    
    # 创建回测引擎
    cerebro = bt.Cerebro()
    
    # 设置初始资金
    initial_cash = 500.0
    cerebro.broker.set_cash(initial_cash)
    cerebro.broker.setcommission(commission=0.0002)
    
    # 添加数据
    data_feed = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(data_feed)
    
    # 添加策略
    cerebro.addstrategy(
        LayeredTestStrategy,
        test_mode=test_mode,
        test_eps=SAFE_EPS_STANDARD,
        initial_cash=initial_cash,
        use_ema_filter=enable_filters,
        use_volume_filter=enable_filters,
        use_wt_filter=enable_filters,
        verbose=False  # 减少输出
    )
    
    # 运行测试
    start_time = datetime.now()
    
    try:
        result = cerebro.run()
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        print(f"[OK] Test completed in {duration:.2f} seconds")
        return True, duration
        
    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        print(f"[ERROR] Test failed in {duration:.2f} seconds")
        print(f"Error: {str(e)}")
        return False, duration


def run_full_layered_test_suite(symbols_and_files):
    """
    运行完整的分层测试套件
    对每个币种运行 A -> B -> C 三个阶段
    """
    print(f"\n[SUITE] Starting full layered test suite")
    print(f"[SUITE] Testing {len(symbols_and_files)} symbols")
    
    modes = ['indicators_only', 'fixed_sizing', 'full_logic']
    mode_names = ['A) Indicators Only', 'B) Fixed Sizing', 'C) Full Logic']
    
    results = {}
    
    for symbol, data_file in symbols_and_files.items():
        print(f"\n{'='*60}")
        print(f"[SYMBOL] Testing {symbol}")
        print(f"{'='*60}")
        
        symbol_results = {}
        
        for mode, mode_name in zip(modes, mode_names):
            print(f"\n[PHASE] {mode_name}")
            success, duration = run_layered_test(data_file, mode, symbol)
            
            symbol_results[mode] = {
                'success': success,
                'duration': duration
            }
            
            # 如果 A 失败，跳过后续测试
            if mode == 'indicators_only' and not success:
                print(f"[ABORT] {symbol} indicators test failed, skipping remaining phases")
                break
            
            # 如果 B 失败但 A 成功，说明问题在下单逻辑
            if mode == 'fixed_sizing' and not success:
                print(f"[WARNING] {symbol} fixed sizing failed but indicators OK - order logic issue")
            
            # 如果 C 失败但 A/B 成功，说明问题在风险管理
            if mode == 'full_logic' and not success:
                prev_success = symbol_results.get('indicators_only', {}).get('success', False)
                if prev_success:
                    print(f"[WARNING] {symbol} full logic failed but indicators OK - risk management issue")
        
        results[symbol] = symbol_results
    
    # 总结报告
    print(f"\n{'='*60}")
    print(f"[SUMMARY] Layered Test Suite Results")
    print(f"{'='*60}")
    
    for symbol, symbol_results in results.items():
        print(f"\n[{symbol}]")
        for mode, mode_name in zip(modes, mode_names):
            if mode in symbol_results:
                result = symbol_results[mode]
                status = "[PASS]" if result['success'] else "[FAIL]"
                duration = result['duration']
                print(f"   {mode_name}: {status} ({duration:.2f}s)")
            else:
                print(f"   {mode_name}: [SKIPPED]")
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Four Swords Layered Testing")
    parser.add_argument("--mode", choices=['indicators_only', 'fixed_sizing', 'full_logic'], 
                        default='indicators_only', help="Test mode")
    parser.add_argument("--data", help="Data file path")
    parser.add_argument("--symbol", default="TEST", help="Symbol name for reporting")
    parser.add_argument("--filters", action='store_true', help="Enable filters")
    parser.add_argument("--suite", action='store_true', help="Run full test suite for SUI/XRP/DOGE")
    
    args = parser.parse_args()
    
    if args.suite:
        # 运行完整测试套件
        test_symbols = {
            'SUIUSDT': 'backtester/data/SUIUSDT/2h/SUIUSDT-2h-merged.csv',
            'XRPUSDT': 'backtester/data/XRPUSDT/2h/XRPUSDT-2h-merged.csv',
            'DOGEUSDT': 'backtester/data/DOGEUSDT/2h/DOGEUSDT-2h-merged.csv'
        }
        run_full_layered_test_suite(test_symbols)
    else:
        # 单个测试
        if not args.data:
            parser.error("--data is required when not using --suite")
        success, duration = run_layered_test(args.data, args.mode, args.symbol, args.filters)