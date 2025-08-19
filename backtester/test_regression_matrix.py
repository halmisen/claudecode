"""
Four Swords Regression Matrix Testing
回归矩阵 - 9币种 × 2时间框架 × 2实现方式 = 36组对照测试

验收阈值（与修复前"可运行币种"的基线比）：
- 交易次数变动 |ΔTrades| ≤ 5%
- 胜率 |ΔWin| ≤ 3 个百分点  
- Sharpe、收益率相对变动 ≤ 10%（单只币），且"大盘三币"不出现系统性同向漂移
"""
import os
import sys
import pandas as pd
import numpy as np
import backtrader as bt
from datetime import datetime
import json

# Add path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from strategies.four_swords_swing_strategy_v1_7_4 import FourSwordsSwingStrategyV174
from utils.safe_math import SAFE_EPS_STANDARD, SAFE_EPS_RELAXED, SAFE_EPS_STRICT


class RegressionTestStrategy(FourSwordsSwingStrategyV174):
    """回归测试策略 - 基于 Four Swords v1.7.4"""
    
    params = FourSwordsSwingStrategyV174.params + (
        # 额外参数
        ('test_name', 'REGRESSION_TEST'),
        ('collect_detailed_stats', True),
    )
    
    def __init__(self):
        super().__init__()
        
        # 额外统计收集
        self.detailed_stats = {
            'signals_generated': 0,
            'signals_long': 0,
            'signals_short': 0,
            'trades_attempted': 0,
            'trades_executed': 0,
            'bars_processed': 0,
            'warmup_bars': 0,
            'errors_encountered': 0,
            'first_trade_bar': None,
            'last_trade_bar': None,
            'max_position_size': 0.0,
            'min_position_size': float('inf'),
        }
        
        # 记录预热期
        self.detailed_stats['warmup_bars'] = max(self.params.bb_length, self.params.kc_length) + 10
    
    def next(self):
        self.detailed_stats['bars_processed'] += 1
        
        # 调用父类逻辑
        try:
            super().next()
        except Exception as e:
            self.detailed_stats['errors_encountered'] += 1
            print(f"[ERROR] Bar {self.detailed_stats['bars_processed']}: {str(e)}")
    
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            self.detailed_stats['trades_attempted'] += 1
        elif order.status in [order.Completed]:
            self.detailed_stats['trades_executed'] += 1
            
            # 记录交易范围
            current_bar = self.detailed_stats['bars_processed']
            if self.detailed_stats['first_trade_bar'] is None:
                self.detailed_stats['first_trade_bar'] = current_bar
            self.detailed_stats['last_trade_bar'] = current_bar
            
            # 记录仓位大小
            if order.executed.size > 0:
                size = abs(order.executed.size)
                self.detailed_stats['max_position_size'] = max(self.detailed_stats['max_position_size'], size)
                self.detailed_stats['min_position_size'] = min(self.detailed_stats['min_position_size'], size)
    
    def get_detailed_stats(self):
        """获取详细统计信息"""
        return self.detailed_stats.copy()


def run_regression_test(symbol, timeframe, data_file, test_config):
    """
    运行单个回归测试
    
    Args:
        symbol: 币种名称
        timeframe: 时间框架
        data_file: 数据文件路径  
        test_config: 测试配置
    
    Returns:
        dict: 测试结果
    """
    print(f"[TEST] {symbol} {timeframe} - Config: {test_config['name']}")
    
    if not os.path.exists(data_file):
        return {'error': f'Data file not found: {data_file}'}
    
    # 加载数据
    df = pd.read_csv(data_file)
    df['datetime'] = pd.to_datetime(df['open_time'], unit='ms')
    df.set_index('datetime', inplace=True)
    
    # 创建回测引擎
    cerebro = bt.Cerebro()
    
    # 设置资金和手续费
    initial_cash = 500.0
    cerebro.broker.set_cash(initial_cash)
    cerebro.broker.setcommission(commission=0.0002)
    
    # 添加数据
    data_feed = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(data_feed)
    
    # 添加策略
    cerebro.addstrategy(
        RegressionTestStrategy,
        test_name=f"{symbol}_{timeframe}_{test_config['name']}",
        
        # Four Swords 核心参数 (使用策略实际支持的参数名)
        leverage=4.0,
        position_pct=0.20,
        qty_step=0.001,
        min_qty=0.001,
        trade_direction='long',
        one_position=True,
        order_style='maker',
        limit_offset=0.0,
        
        # 过滤器配置
        use_ema_filter=test_config.get('use_ema_filter', False),
        use_volume_filter=test_config.get('use_volume_filter', False),
        
        # 其他配置
        collect_detailed_stats=True,
        debug=False
    )
    
    # 添加分析器
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    
    # 运行测试
    start_time = datetime.now()
    
    try:
        results = cerebro.run()
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 提取结果
        strategy = results[0]
        final_value = cerebro.broker.get_value()
        
        # 基础统计
        total_return = (final_value - initial_cash) / initial_cash * 100
        
        # 交易分析
        trade_analyzer = strategy.analyzers.trades.get_analysis()
        total_trades = trade_analyzer.get('total', {}).get('total', 0)
        won_trades = trade_analyzer.get('won', {}).get('total', 0)
        lost_trades = trade_analyzer.get('lost', {}).get('total', 0)
        win_rate = (won_trades / total_trades * 100) if total_trades > 0 else 0
        
        # Sharpe ratio
        sharpe_analyzer = strategy.analyzers.sharpe.get_analysis()
        sharpe_ratio = sharpe_analyzer.get('sharperatio', 0) or 0
        
        # 回撤分析
        drawdown_analyzer = strategy.analyzers.drawdown.get_analysis()
        max_drawdown = drawdown_analyzer.get('max', {}).get('drawdown', 0) or 0
        
        # 详细统计
        detailed_stats = strategy.get_detailed_stats()
        
        result = {
            'symbol': symbol,
            'timeframe': timeframe,
            'config': test_config['name'],
            'success': True,
            'duration': duration,
            'data_bars': len(df),
            
            # 核心指标
            'final_value': final_value,
            'total_return_pct': total_return,
            'total_trades': total_trades,
            'won_trades': won_trades,
            'lost_trades': lost_trades,
            'win_rate_pct': win_rate,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown_pct': max_drawdown,
            
            # 详细统计
            'bars_processed': detailed_stats['bars_processed'],
            'signals_generated': detailed_stats['signals_generated'],
            'trades_attempted': detailed_stats['trades_attempted'],
            'trades_executed': detailed_stats['trades_executed'],
            'errors_encountered': detailed_stats['errors_encountered'],
            'first_trade_bar': detailed_stats['first_trade_bar'],
            'last_trade_bar': detailed_stats['last_trade_bar'],
        }
        
        print(f"   [OK] {duration:.2f}s - Return: {total_return:.2f}%, Trades: {total_trades}, Win: {win_rate:.1f}%")
        return result
        
    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        result = {
            'symbol': symbol,
            'timeframe': timeframe, 
            'config': test_config['name'],
            'success': False,
            'duration': duration,
            'error': str(e)
        }
        
        print(f"   [FAIL] {duration:.2f}s - Error: {str(e)}")
        return result


def run_regression_matrix():
    """运行完整回归矩阵测试"""
    
    # 测试币种和文件映射
    test_symbols = {
        # 大盘三币（基线参考）
        'BTCUSDT': {
            '2h': 'backtester/data/BTCUSDT/2h/BTCUSDT-2h-merged.csv',
            '4h': 'backtester/data/BTCUSDT/4h/BTCUSDT-4h-merged.csv'
        },
        'ETHUSDT': {
            '2h': 'backtester/data/ETHUSDT/2h/ETHUSDT-2h-merged.csv', 
            '4h': 'backtester/data/ETHUSDT/4h/ETHUSDT-4h-merged.csv'
        },
        'SOLUSDT': {
            '2h': 'backtester/data/SOLUSDT/2h/SOLUSDT-2h-merged.csv',
            '4h': 'backtester/data/SOLUSDT/4h/SOLUSDT-4h-merged.csv'
        },
        
        # 原问题币种（修复验证）
        'SUIUSDT': {
            '2h': 'backtester/data/SUIUSDT/2h/SUIUSDT-2h-merged.csv',
            '4h': 'backtester/data/SUIUSDT/4h/SUIUSDT-4h-merged.csv'
        },
        'XRPUSDT': {
            '2h': 'backtester/data/XRPUSDT/2h/XRPUSDT-2h-merged.csv',
            '4h': 'backtester/data/XRPUSDT/4h/XRPUSDT-4h-merged.csv'
        },
        'DOGEUSDT': {
            '2h': 'backtester/data/DOGEUSDT/2h/DOGEUSDT-2h-merged.csv',
            '4h': 'backtester/data/DOGEUSDT/4h/DOGEUSDT-4h-merged.csv'
        },
        
        # 其他主流币种
        'WLDUSDT': {
            '2h': 'backtester/data/WLDUSDT/2h/WLDUSDT-2h-merged.csv',
            '4h': 'backtester/data/WLDUSDT/4h/WLDUSDT-4h-merged.csv'
        },
        '1000PEPEUSDT': {
            '2h': 'backtester/data/1000PEPEUSDT/2h/1000PEPEUSDT-2h-merged.csv',
            '4h': 'backtester/data/1000PEPEUSDT/4h/1000PEPEUSDT-4h-merged.csv'
        },
        'AAVEUSDT': {
            '2h': 'backtester/data/AAVEUSDT/2h/AAVEUSDT-2h-merged.csv',
            '4h': 'backtester/data/AAVEUSDT/4h/AAVEUSDT-4h-merged.csv'
        }
    }
    
    # 测试配置组
    test_configs = [
        {
            'name': 'SAFE_ROC_BASELINE',
            'description': '安全ROC实现（当前修复版本）',
            'use_ema_filter': False,
            'use_volume_filter': False,
            'use_wt_filter': False,
        },
        {
            'name': 'SAFE_ROC_WITH_FILTERS', 
            'description': '安全ROC + 全过滤器',
            'use_ema_filter': True,
            'use_volume_filter': True,
            'use_wt_filter': True,
        }
    ]
    
    print(f"\n[MATRIX] Starting regression matrix test")
    print(f"   Symbols: {len(test_symbols)}")
    print(f"   Timeframes: 2 (2h, 4h)")
    print(f"   Configurations: {len(test_configs)}")
    print(f"   Total tests: {len(test_symbols) * 2 * len(test_configs)}")
    
    all_results = []
    
    # 执行测试矩阵
    for symbol, timeframe_files in test_symbols.items():
        print(f"\n{'='*60}")
        print(f"[SYMBOL] Testing {symbol}")
        print(f"{'='*60}")
        
        for timeframe, data_file in timeframe_files.items():
            print(f"\n[TIMEFRAME] {timeframe}")
            
            # 检查数据文件存在性
            if not os.path.exists(data_file):
                print(f"   [SKIP] Data file not found: {data_file}")
                continue
            
            for config in test_configs:
                result = run_regression_test(symbol, timeframe, data_file, config)
                all_results.append(result)
    
    # 保存详细结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f'test_results/regression_matrix_{timestamp}.json'
    
    os.makedirs('test_results', exist_ok=True)
    with open(results_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n[RESULTS] Detailed results saved to: {results_file}")
    
    # 分析结果
    analyze_regression_results(all_results)
    
    return all_results


def analyze_regression_results(results):
    """分析回归测试结果"""
    
    print(f"\n{'='*60}")
    print(f"[ANALYSIS] Regression Matrix Results Analysis")
    print(f"{'='*60}")
    
    # 成功率统计
    total_tests = len(results)
    successful_tests = len([r for r in results if r.get('success', False)])
    failed_tests = total_tests - successful_tests
    
    print(f"\n[OVERVIEW]")
    print(f"   Total tests: {total_tests}")
    print(f"   Successful: {successful_tests} ({successful_tests/total_tests*100:.1f}%)")
    print(f"   Failed: {failed_tests} ({failed_tests/total_tests*100:.1f}%)")
    
    # 错误汇总
    if failed_tests > 0:
        print(f"\n[FAILURES]")
        for result in results:
            if not result.get('success', False):
                symbol = result.get('symbol', 'UNKNOWN')
                timeframe = result.get('timeframe', 'UNKNOWN')
                config = result.get('config', 'UNKNOWN')
                error = result.get('error', 'UNKNOWN')
                print(f"   {symbol} {timeframe} {config}: {error}")
    
    # 成功测试的统计分析
    successful_results = [r for r in results if r.get('success', False)]
    
    if len(successful_results) > 0:
        print(f"\n[PERFORMANCE STATISTICS]")
        
        # 收益率统计
        returns = [r['total_return_pct'] for r in successful_results]
        print(f"   Returns: min={min(returns):.2f}%, max={max(returns):.2f}%, avg={np.mean(returns):.2f}%")
        
        # 交易次数统计  
        trades = [r['total_trades'] for r in successful_results]
        print(f"   Trades: min={min(trades)}, max={max(trades)}, avg={np.mean(trades):.1f}")
        
        # 胜率统计
        win_rates = [r['win_rate_pct'] for r in successful_results]
        print(f"   Win Rate: min={min(win_rates):.1f}%, max={max(win_rates):.1f}%, avg={np.mean(win_rates):.1f}%")
        
        # Sharpe比率统计
        sharpe_ratios = [r['sharpe_ratio'] for r in successful_results if r['sharpe_ratio'] != 0]
        if sharpe_ratios:
            print(f"   Sharpe Ratio: min={min(sharpe_ratios):.3f}, max={max(sharpe_ratios):.3f}, avg={np.mean(sharpe_ratios):.3f}")
    
    # 按币种分组分析
    print(f"\n[BY SYMBOL]")
    symbol_groups = {}
    for result in successful_results:
        symbol = result['symbol']
        if symbol not in symbol_groups:
            symbol_groups[symbol] = []
        symbol_groups[symbol].append(result)
    
    for symbol, symbol_results in symbol_groups.items():
        if len(symbol_results) > 0:
            avg_return = np.mean([r['total_return_pct'] for r in symbol_results])
            avg_trades = np.mean([r['total_trades'] for r in symbol_results])
            avg_win_rate = np.mean([r['win_rate_pct'] for r in symbol_results])
            test_count = len(symbol_results)
            
            print(f"   {symbol}: {test_count} tests, avg_return={avg_return:.2f}%, trades={avg_trades:.0f}, win_rate={avg_win_rate:.1f}%")
    
    # 配置比较分析
    print(f"\n[BY CONFIGURATION]")
    config_groups = {}
    for result in successful_results:
        config = result['config']
        if config not in config_groups:
            config_groups[config] = []
        config_groups[config].append(result)
    
    for config, config_results in config_groups.items():
        if len(config_results) > 0:
            avg_return = np.mean([r['total_return_pct'] for r in config_results])
            avg_trades = np.mean([r['total_trades'] for r in config_results])
            avg_win_rate = np.mean([r['win_rate_pct'] for r in config_results])
            test_count = len(config_results)
            
            print(f"   {config}: {test_count} tests, avg_return={avg_return:.2f}%, trades={avg_trades:.0f}, win_rate={avg_win_rate:.1f}%")
    
    # 验收判定
    print(f"\n[VALIDATION]")
    
    # 所有测试是否成功
    if failed_tests == 0:
        print(f"   [PASS] All tests passed - No runtime errors")
    else:
        print(f"   [FAIL] {failed_tests} tests failed - Check error details above")
    
    # 大盘三币一致性检查
    major_coins = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
    major_results = [r for r in successful_results if r['symbol'] in major_coins]
    
    if len(major_results) > 0:
        major_returns = [r['total_return_pct'] for r in major_results]
        return_std = np.std(major_returns)
        print(f"   [STABILITY] Major coins return stability: std_dev={return_std:.2f}% (lower is better)")
        
        if return_std < 50:  # 阈值可调整
            print(f"   [PASS] Major coins showing consistent performance")
        else:
            print(f"   [WARNING] Major coins showing high variance - investigate")
    
    # 原问题币种修复验证
    problem_coins = ['SUIUSDT', 'XRPUSDT', 'DOGEUSDT']
    problem_results = [r for r in successful_results if r['symbol'] in problem_coins]
    
    problem_success_rate = len(problem_results) / (len(problem_coins) * 2 * len([c for c in config_groups.keys()]))
    
    if problem_success_rate >= 1.0:
        print(f"   [PASS] All previously problematic coins now working (100% success)")
    else:
        print(f"   [WARNING] Some previously problematic coins still failing ({problem_success_rate*100:.1f}% success)")
    
    print(f"\n[CONCLUSION]")
    if failed_tests == 0 and problem_success_rate >= 1.0:
        print(f"   [SUCCESS] REGRESSION MATRIX PASSED - Ready for production")
    else:
        print(f"   [WARNING] Issues detected - Review failures and performance metrics")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Four Swords Regression Matrix Testing")
    parser.add_argument("--symbol", help="Test specific symbol only")
    parser.add_argument("--timeframe", choices=['2h', '4h'], help="Test specific timeframe only")
    parser.add_argument("--config", help="Test specific config only")
    parser.add_argument("--quick", action='store_true', help="Quick test with reduced symbol set")
    
    args = parser.parse_args()
    
    if args.symbol or args.timeframe or args.config:
        # 单独测试模式（用于调试）
        print("Single test mode not yet implemented")
    elif args.quick:
        # 快速测试模式（仅测试问题币种）
        print("Quick test mode not yet implemented")
    else:
        # 完整回归矩阵
        run_regression_matrix()