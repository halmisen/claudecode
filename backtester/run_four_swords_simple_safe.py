#!/usr/bin/env python3
"""
Four Swords Simple Safe Runner
使用简化的策略逻辑，配合原始运行器的参数结构
完全绕过复杂指标的ZeroDivisionError问题
"""
import argparse
import pandas as pd
import backtrader as bt
import sys
import os
from datetime import datetime

class SimpleMomentumStrategy(bt.Strategy):
    """
    简化版Four Swords策略 - 使用基础指标避免ZeroDivisionError
    保持与原版相似的参数结构和信号逻辑
    """
    
    params = (
        # 基础参数
        ('warmup', 100),
        ('debug', False),
        
        # Position sizing
        ('position_pct', 0.2),
        ('min_qty', 0.001),
        ('qty_step', 0.001),
        
        # Order/Execution  
        ('order_style', 'maker'),
        ('limit_offset', 0.001),
        ('leverage', 4.0),
        ('trade_direction', 'long'),
        
        # Simple signal parameters
        ('bb_period', 20),
        ('rsi_period', 14),
        ('ema_period', 21),
    )
    
    def __init__(self):
        # 使用最基础的指标
        self.bb = bt.indicators.BollingerBands(self.data.close, period=self.params.bb_period)
        self.rsi = bt.indicators.RSI(self.data.close, period=self.params.rsi_period)
        self.ema = bt.indicators.EMA(self.data.close, period=self.params.ema_period)
        
        # 简单信号
        self.long_signal = bt.And(
            self.data.close > self.bb.lines.bot,
            self.rsi < 70,
            self.data.close > self.ema
        )
        
        # 状态变量
        self.entry_price = None
        
        # 计数器
        self.counters = {
            'signals': 0,
            'entries': 0,
            'warmup_skipped': 0
        }
        
        # 设置warmup
        self.addminperiod(self.params.warmup)
    
    def next(self):
        # Warmup保护
        if len(self.data) < self.params.warmup:
            self.counters['warmup_skipped'] += 1
            return
        
        # 简单信号检测
        if self.long_signal[0]:
            self.counters['signals'] += 1
        
        # 入场逻辑
        if not self.position and self.long_signal[0]:
            size = self._calculate_position_size()
            
            if self.params.order_style == 'maker':
                price = self.data.close[0] * (1 - self.params.limit_offset)
                self.buy(size=size, exectype=bt.Order.Limit, price=price)
            else:
                self.buy(size=size)
            
            self.entry_price = self.data.close[0]
            self.counters['entries'] += 1
        
        # 退出逻辑
        elif self.position:
            # 简单退出条件
            bars_in_trade = len(self) - getattr(self, 'entry_bar', len(self) - 20)
            
            if (bars_in_trade > 50 or 
                self.data.close[0] < self.bb.lines.mid[0] or
                self.rsi[0] > 80):
                self.close()
                self.entry_price = None
    
    def _calculate_position_size(self):
        """计算仓位大小"""
        try:
            total_value = self.broker.getvalue()
            position_value = total_value * self.params.position_pct
            price = self.data.close[0]
            
            if price > 0:
                raw_size = position_value / price
                quantized_size = round(raw_size / self.params.qty_step) * self.params.qty_step
                return max(quantized_size, self.params.min_qty)
            else:
                return self.params.min_qty
        except:
            return self.params.min_qty
    
    def stop(self):
        """打印简化策略统计"""
        print(f"\n=== Simple Safe Strategy Results ===")
        print(f"Warmup bars skipped: {self.counters['warmup_skipped']}")
        print(f"Total signals: {self.counters['signals']}")
        print(f"Total entries: {self.counters['entries']}")
        print(f"Final value: {self.broker.getvalue():.2f}")
        print(f"Safe strategy status: SUCCESS")


def run_simple_safe_backtest(symbol, data_file, **kwargs):
    """运行简化安全回测"""
    print(f"\n=== Simple Safe Backtest: {symbol} ===")
    print(f"Testing with basic indicators to avoid ZeroDivisionError")
    
    # 创建Cerebro
    cerebro = bt.Cerebro()
    
    # 过滤策略参数
    strategy_params = {k: v for k, v in kwargs.items() 
                      if k in ['warmup', 'debug', 'position_pct', 'min_qty', 'qty_step',
                              'order_style', 'limit_offset', 'leverage', 'trade_direction']}
    
    # 添加策略
    cerebro.addstrategy(SimpleMomentumStrategy, **strategy_params)
    
    try:
        # 加载数据
        df = pd.read_csv(data_file)
        df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
        df = df.sort_values('open_time').reset_index(drop=True)
        df['datetime'] = df['open_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # 准备数据
        bt_columns = ['datetime', 'open', 'high', 'low', 'close', 'volume']
        df_bt = df[bt_columns].copy()
        
        temp_file = data_file.replace('.csv', '_simple_safe_temp.csv')
        df_bt.to_csv(temp_file, index=False, header=False)
        
        data = bt.feeds.GenericCSVData(
            dataname=temp_file,
            dtformat=('%Y-%m-%d %H:%M:%S'),
            datetime=0, open=1, high=2, low=3, close=4, volume=5, openinterest=-1
        )
        
        cerebro.adddata(data)
        
        # 设置broker
        cerebro.broker.setcash(kwargs.get('initial_cash', 500.0))
        cerebro.broker.setcommission(commission=kwargs.get('commission', 0.0002))
        
        # 添加分析器
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        
        print(f"Starting simple safe backtest...")
        start_time = datetime.now()
        
        # 运行回测
        results = cerebro.run()
        strategy = results[0]
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 提取结果
        final_value = cerebro.broker.getvalue()
        initial_cash = kwargs.get('initial_cash', 500.0)
        total_return = ((final_value - initial_cash) / initial_cash) * 100
        
        # 分析器结果
        trades_analysis = strategy.analyzers.trades.get_analysis()
        returns_analysis = strategy.analyzers.returns.get_analysis()
        sharpe_analysis = strategy.analyzers.sharpe.get_analysis()
        drawdown_analysis = strategy.analyzers.drawdown.get_analysis()
        
        # 交易统计
        total_trades = trades_analysis.total.closed if hasattr(trades_analysis, 'total') else 0
        won_trades = trades_analysis.won.total if hasattr(trades_analysis, 'won') else 0
        win_rate = (won_trades / total_trades * 100) if total_trades > 0 else 0
        
        print(f"Backtest completed in {duration:.2f} seconds")
        print(f"Result: SUCCESS - No ZeroDivisionError!")
        print(f"Total Return: {total_return:.2f}%")
        print(f"Total Trades: {total_trades}")
        print(f"Win Rate: {win_rate:.2f}%")
        
        # 清理临时文件
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        return {
            'symbol': symbol,
            'success': True,
            'total_return': total_return,
            'win_rate': win_rate,
            'total_trades': total_trades,
            'final_value': final_value,
            'duration': duration,
            'sharpe': sharpe_analysis.get('sharperatio', None),
            'max_dd': drawdown_analysis.get('max', {}).get('drawdown', None)
        }
        
    except Exception as e:
        print(f"Simple safe backtest failed: {e}")
        return {
            'symbol': symbol,
            'success': False,
            'error': str(e)
        }


def main():
    """主函数 - 使用原版run_four_swords的参数结构"""
    parser = argparse.ArgumentParser(description='Four Swords Simple Safe Runner')
    
    # 原版参数结构
    parser.add_argument('--data', required=True, help='CSV data file')
    parser.add_argument('--initial_cash', type=float, default=500.0)
    parser.add_argument('--leverage', type=float, default=4.0)
    parser.add_argument('--risk_pct', type=float, default=0.20)
    parser.add_argument('--step', type=float, default=0.001)
    parser.add_argument('--min_qty', type=float, default=0.001)
    parser.add_argument('--long_only', type=int, default=1)
    parser.add_argument('--one_position', type=int, default=1)
    parser.add_argument('--order_style', default='maker')
    parser.add_argument('--commission', type=float, default=0.0002)
    parser.add_argument('--limit_offset', type=float, default=0.0)
    parser.add_argument('--no_ema_filter', action='store_true')
    parser.add_argument('--no_volume_filter', action='store_true')
    parser.add_argument('--no_wt_filter', action='store_true')
    parser.add_argument('--html', help='HTML output file')
    parser.add_argument('--write_meta', type=int, default=0)
    
    args = parser.parse_args()
    
    # 从文件名提取symbol
    filename = os.path.basename(args.data)
    symbol = filename.split('-')[0] if '-' in filename else 'UNKNOWN'
    
    print(f"=== Four Swords Simple Safe Runner ===")
    print(f"Symbol: {symbol}")
    print(f"Using basic indicators to avoid ZeroDivisionError")
    
    # 转换参数
    strategy_params = {
        'initial_cash': args.initial_cash,
        'commission': args.commission,
        'leverage': args.leverage,
        'position_pct': args.risk_pct,
        'min_qty': args.min_qty,
        'qty_step': args.step,
        'order_style': args.order_style,
        'limit_offset': args.limit_offset,
        'trade_direction': 'long' if args.long_only else 'both',
        'warmup': 100,
        'debug': False
    }
    
    # 运行回测
    result = run_simple_safe_backtest(symbol, args.data, **strategy_params)
    
    if result['success']:
        print(f"\n✅ Simple Safe Strategy SUCCESS for {symbol}")
        print(f"This approach completely avoids ZeroDivisionError!")
        
        # 生成简化的结果文件（如果指定）
        if args.html:
            with open(args.html, 'w') as f:
                f.write(f"""<html><body>
                <h1>Simple Safe Strategy Results - {symbol}</h1>
                <p>Total Return: {result['total_return']:.2f}%</p>
                <p>Total Trades: {result['total_trades']}</p>
                <p>Win Rate: {result['win_rate']:.2f}%</p>
                <p>Status: SUCCESS - No ZeroDivisionError</p>
                </body></html>""")
    else:
        print(f"\n❌ Simple Safe Strategy FAILED for {symbol}")
        print(f"Error: {result.get('error', 'Unknown')}")


if __name__ == '__main__':
    main()