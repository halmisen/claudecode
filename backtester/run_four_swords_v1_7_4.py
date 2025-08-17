#!/usr/bin/env python3
"""
Four Swords Swing Strategy v1.7.4 Runner
基于优化测试确立的生产级策略执行器

执行统一口径的严谨测试：
- 初始资金 500 USDT，4×逐仓杠杆，只做多，同一时刻仅1笔持仓
- 每笔使用账户权益的20%名义价值
- BTCUSDT 4H 全历史数据
- 支持 A0/A1/A2 消融测试 (无过滤 -> EMA过滤 -> EMA+Volume过滤)
- 新基线：limit_offset=0.0 实现最优Maker模式性能

Usage:
    # A0 新基线测试 (无过滤，最优配置)
    python run_four_swords_v1_7_4.py --data backtester/data/BTCUSDT/4h/BTCUSDT-4h-merged.csv --order_style maker --limit_offset 0.0 --no_ema_filter --no_volume_filter --no_wt_filter

    # A1 仅EMA过滤
    python run_four_swords_v1_7_4.py --data backtester/data/BTCUSDT/4h/BTCUSDT-4h-merged.csv --no_volume_filter --no_wt_filter

    # A2 EMA+Volume过滤
    python run_four_swords_v1_7_4.py --data backtester/data/BTCUSDT/4h/BTCUSDT-4h-merged.csv --no_wt_filter
"""

import sys
import os
import json
import argparse
from datetime import datetime
from pathlib import Path
from math import floor

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import backtrader as bt

# Import our strategy
from strategies.four_swords_swing_strategy_v1_7_4 import FourSwordsSwingStrategyV174

# Optional plotting with btplotting (modern alternative)
try:
    from btplotting import BacktraderPlotting as Bokeh
    HAS_BT_PLOTTING = True
except (ImportError, AttributeError):
    HAS_BT_PLOTTING = False


class LeverageSizer(bt.Sizer):
    """
    4×合约仓位管理器 - 正确实现
    
    核心逻辑:
    - 目标交易价值 = 账户权益 × 20% (想要的交易价值)
    - 实际买入金额 = 目标交易价值 ÷ 杠杆 (实际花费的USDT)
    - 仓位大小 = 实际买入金额 / 价格
    
    示例: 500 USDT账户 → 100 USDT交易价值 → 25 USDT买入 → 4倍杠杆 → 100 USDT实际交易价值
    """
    params = dict(
        risk_pct=0.20,   # 账户权益的20%作为保证金
        leverage=4.0,    # 4倍杠杆
        step=0.001,      # 数量步进
        min_qty=0.001    # 最小数量
    )
    
    def _getsizing(self, comminfo, cash, data, isbuy):
        if not isbuy:
            return 0
            
        price = float(data.close[0])
        account_value = self.broker.getvalue()  # 账户权益
        
        # 正确的4倍合约逻辑 (按照用户理解)
        target_trading_value = account_value * self.p.risk_pct  # 目标交易价值 (20%资金)
        actual_buy_amount = target_trading_value / self.p.leverage  # 实际买入金额 (除以杠杆)
        size = actual_buy_amount / price  # 仓位大小
        
        # 量化到交易所步进
        q = floor(size / self.p.step) * self.p.step
        final_size = max(q, self.p.min_qty)
        
        # 调试信息
        if final_size > 0:
            actual_trading_value = final_size * price * self.p.leverage
            print(f"[合约仓位] 账户权益: {account_value:.2f} USDT")
            print(f"[合约仓位] 目标交易价值: {target_trading_value:.2f} USDT ({self.p.risk_pct*100}%资金)")
            print(f"[合约仓位] 实际买入金额: {actual_buy_amount:.2f} USDT (÷{self.p.leverage}杠杆)")
            print(f"[合约仓位] 价格: {price:.2f}, 仓位: {final_size:.6f}")
            print(f"[合约仓位] 实际交易价值: {actual_trading_value:.2f} USDT")
        
        return final_size


def load_csv_as_feed(csv_path: str) -> bt.feeds.PandasData:
    """
    加载CSV数据并进行基础验证
    确保时间框架为4H且数据完整性
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"数据文件不存在: {csv_path}")
    
    print(f"正在加载数据: {csv_path}")
    
    # 读取并预处理CSV
    df = pd.read_csv(csv_path)
    print(f"原始数据形状: {df.shape}")
    print(f"列名: {list(df.columns)}")
    
    # 适配常见列名格式
    cols_mapping = {c.lower(): c for c in df.columns}
    
    # 查找时间列
    datetime_col = None
    for potential_col in ['datetime', 'date', 'time', 'timestamp', 'open_time']:
        if potential_col in cols_mapping:
            datetime_col = cols_mapping[potential_col]
            break
    
    if not datetime_col:
        raise ValueError(f"CSV缺少时间列。可用列: {list(df.columns)}")
    
    # 时间索引处理
    # 如果是时间戳格式，需要转换
    if df[datetime_col].dtype in ['int64', 'float64']:
        # 假设是毫秒时间戳，转换为秒
        df[datetime_col] = pd.to_datetime(df[datetime_col], unit='ms')
    else:
        df[datetime_col] = pd.to_datetime(df[datetime_col])
    
    df = df.set_index(datetime_col).sort_index()
    
    # 数据完整性检查
    print("执行数据完整性检查...")
    assert df.index.is_monotonic_increasing, "时间索引必须单调递增"
    assert df.index.is_unique, "时间索引不能有重复"
    
    required_cols = ['open', 'high', 'low', 'close', 'volume']
    for col in required_cols:
        mapped_col = cols_mapping.get(col, col)
        if mapped_col not in df.columns:
            raise ValueError(f"缺少必要列: {col}")
        if df[mapped_col].isna().any():
            raise ValueError(f"列 {col} 存在空值")
    
    # 打印数据概要
    print(f"数据时间范围: {df.index.min()} -> {df.index.max()}")
    print(f"总K线数量: {len(df)} 根")
    print(f"时间间隔检查: {df.index.to_series().diff().mode().iloc[0]}")
    
    # 创建Backtrader数据源
    feed = bt.feeds.PandasData(
        dataname=df,
        timeframe=bt.TimeFrame.Minutes,
        compression=240,  # 4小时K线 (240分钟)
        open=cols_mapping.get('open', 'open'),
        high=cols_mapping.get('high', 'high'),
        low=cols_mapping.get('low', 'low'),
        close=cols_mapping.get('close', 'close'),
        volume=cols_mapping.get('volume', 'volume'),
    )
    
    return feed, (str(df.index.min()), str(df.index.max()), len(df))


def add_analyzers(cerebro: bt.Cerebro):
    """添加回测分析器"""
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', riskfreerate=0.0)
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')


def write_summary_csv(csv_path: str, row_data: dict):
    """写入回测结果汇总CSV"""
    import csv
    
    # 确保目录存在
    os.makedirs(os.path.dirname(csv_path) if os.path.dirname(csv_path) else '.', exist_ok=True)
    
    header = list(row_data.keys())
    file_exists = os.path.exists(csv_path)
    
    with open(csv_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=header)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row_data)


def write_meta_json(html_path: str, meta_data: dict):
    """写入元数据JSON文件"""
    base_name, _ = os.path.splitext(html_path)
    meta_path = base_name + '.meta.json'
    
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(meta_data, f, ensure_ascii=False, indent=2, default=str)


def plot_bokeh_chart(cerebro: bt.Cerebro, output_path: str):
    """生成Bokeh交互式图表使用btplotting"""
    if not HAS_BT_PLOTTING:
        print("警告: btplotting未安装，跳过图表生成")
        print("安装命令: pip install git+https://github.com/happydasch/btplotting.git")
        return
    
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        print(f"开始生成Bokeh图表: {output_path}")
        plotter = Bokeh(filename=output_path)
        
        print("调用cerebro.plot()...")
        cerebro.plot(plotter)
        print(f"图表已保存: {output_path}")
        
        # 检查文件是否真的生成了
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"HTML文件生成成功: {file_size} bytes")
        else:
            print("错误: HTML文件未生成")
        
    except Exception as e:
        import traceback
        print(f"图表生成失败: {e}")
        print("详细错误信息:")
        traceback.print_exc()


def main():
    parser = argparse.ArgumentParser(
        description='Four Swords v1.7.4 测试运行器 - 支持A0/A1/A2消融测试',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
消融测试示例:
  # A0 基线 (无过滤)
  python run_four_swords_v1_7_4_test.py --data data.csv --no_ema_filter --no_volume_filter --no_wt_filter
  
  # A1 仅EMA过滤
  python run_four_swords_v1_7_4_test.py --data data.csv --no_volume_filter --no_wt_filter
  
  # A2 EMA+Volume过滤
  python run_four_swords_v1_7_4_test.py --data data.csv --no_wt_filter
  
  # A3 全过滤 (默认)
  python run_four_swords_v1_7_4_test.py --data data.csv
        """
    )
    
    # 必需参数
    parser.add_argument('--data', required=True, help='OHLCV CSV数据文件路径')
    
    # 回测基础设置
    parser.add_argument('--initial_cash', type=float, default=500.0, help='初始资金 USDT (默认: 500)')
    parser.add_argument('--leverage', type=float, default=4.0, help='杠杆倍数 (默认: 4)')
    parser.add_argument('--commission', type=float, default=0.0002, help='手续费率 (默认: 0.0002 = 0.02% maker)')
    
    # 仓位管理
    parser.add_argument('--risk_pct', type=float, default=0.20, help='单笔仓位占权益比例 (默认: 0.20 = 20%)')
    parser.add_argument('--step', type=float, default=0.001, help='数量步进 (默认: 0.001)')
    parser.add_argument('--min_qty', type=float, default=0.001, help='最小交易数量 (默认: 0.001)')
    
    # 交易设置
    parser.add_argument('--order_style', choices=['maker', 'taker'], default='maker', 
                       help='下单方式 (默认: maker)')
    parser.add_argument('--limit_offset', type=float, default=0.001,
                       help='maker模式限价偏移比例 (默认: 0.001 = 0.1%)')
    parser.add_argument('--long_only', type=int, default=1, help='只做多 (1) 或双向 (0)')
    parser.add_argument('--one_position', type=int, default=1, help='同一时刻仅1笔持仓 (1) 或多笔 (0)')
    
    # 策略参数
    parser.add_argument('--bb_length', type=int, default=20, help='布林带周期')
    parser.add_argument('--bb_mult', type=float, default=2.0, help='布林带倍数')
    parser.add_argument('--kc_length', type=int, default=20, help='肯特纳通道周期')
    parser.add_argument('--kc_mult', type=float, default=1.5, help='肯特纳通道倍数')
    parser.add_argument('--wt_n1', type=int, default=10, help='WaveTrend n1参数')
    parser.add_argument('--wt_n2', type=int, default=21, help='WaveTrend n2参数')
    parser.add_argument('--ema_fast', type=int, default=10, help='快速EMA周期')
    parser.add_argument('--ema_slow', type=int, default=20, help='慢速EMA周期')
    parser.add_argument('--volume_mult', type=float, default=1.05, help='成交量倍数阈值')
    
    # 过滤器开关 (消融测试核心)
    parser.add_argument('--no_ema_filter', action='store_true', help='禁用EMA趋势过滤')
    parser.add_argument('--no_volume_filter', action='store_true', help='禁用成交量过滤')
    parser.add_argument('--no_wt_filter', action='store_true', help='禁用WaveTrend方向过滤')
    
    # 输出设置
    parser.add_argument('--html', help='HTML图表输出路径')
    parser.add_argument('--summary_csv', default='results/test_summary.csv', help='结果汇总CSV路径')
    parser.add_argument('--write_meta', type=int, default=1, help='是否写入元数据 (1/0)')
    
    args = parser.parse_args()
    
    # 创建输出目录
    if args.html:
        os.makedirs(os.path.dirname(args.html), exist_ok=True)
    os.makedirs(os.path.dirname(args.summary_csv), exist_ok=True)
    
    print("="*70)
    print("FOUR SWORDS v1.7.4 测试运行器")
    print("="*70)
    print(f"数据文件: {args.data}")
    print(f"初始资金: ${args.initial_cash} USDT")
    print(f"杠杆倍数: {args.leverage}×")
    print(f"仓位比例: {args.risk_pct*100}%")
    print(f"下单方式: {args.order_style}")
    print(f"过滤器状态:")
    print(f"  - EMA过滤: {'禁用' if args.no_ema_filter else '启用'}")
    print(f"  - Volume过滤: {'禁用' if args.no_volume_filter else '启用'}")
    print(f"  - WaveTrend过滤: {'禁用' if args.no_wt_filter else '启用'}")
    
    # 初始化Cerebro
    cerebro = bt.Cerebro()
    
    # 设置Broker - 4倍杠杆期货模式
    cerebro.broker.setcash(args.initial_cash)
    cerebro.broker.setcommission(
        commission=args.commission,      # 手续费率 (0.02% Maker)
        margin=1.0 / args.leverage,      # 保证金比例 (25% = 4倍杠杆)
        stocklike=False,                 # 期货模式，非股票模式
        leverage=args.leverage           # 杠杆倍数
    )
    
    print(f"Broker配置: 初始资金 {args.initial_cash} USDT, {args.leverage}×杠杆, 保证金比例 {1.0/args.leverage*100:.1f}%")
    
    # 加载数据
    try:
        data_feed, (first_dt, last_dt, total_bars) = load_csv_as_feed(args.data)
        # 给数据源添加名称，解决backtrader-plotting标签解析问题
        cerebro.adddata(data_feed, name='BTCUSDT')
    except Exception as e:
        print(f"数据加载失败: {e}")
        sys.exit(1)
    
    # 添加4倍杠杆仓位管理器
    cerebro.addsizer(LeverageSizer, 
                    risk_pct=args.risk_pct,    # 20%资金作保证金
                    leverage=args.leverage,    # 4倍杠杆
                    step=args.step, 
                    min_qty=args.min_qty)
    
    # 添加分析器
    add_analyzers(cerebro)
    
    # 策略参数配置
    strategy_params = {
        # SQZMOM核心参数
        'bb_length': args.bb_length,
        'bb_mult': args.bb_mult,
        'kc_length': args.kc_length,
        'kc_mult': args.kc_mult,
        'use_true_range': True,
        
        # WaveTrend参数
        'wt_n1': args.wt_n1,
        'wt_n2': args.wt_n2,
        
        # 过滤器设置 (消融测试核心)
        'use_ema_filter': not args.no_ema_filter,
        'ema_fast': args.ema_fast,
        'ema_slow': args.ema_slow,
        'use_volume_filter': not args.no_volume_filter,
        'volume_multiplier': args.volume_mult,
        'use_simplified_signals': args.no_wt_filter,  # no_wt_filter = simplified mode
        
        # 交易设置
        'trade_direction': 'long',  # 固定只做多
        'order_style': args.order_style,
        'limit_offset': args.limit_offset,
        'use_sizer': True,
        'one_position': True,  # 同一时刻仅1笔持仓
        'leverage': args.leverage,  # 传递杠杆参数
        
        # 仓位管理
        'position_pct': args.risk_pct,
        'min_qty': args.min_qty,
        'qty_step': args.step,
    }
    
    # 添加策略
    cerebro.addstrategy(FourSwordsSwingStrategyV174, **strategy_params)
    
    print("\n开始回测...")
    
    # 执行回测
    start_time = datetime.now()
    results = cerebro.run()
    end_time = datetime.now()
    strategy = results[0]
    
    # 计算运行时间
    run_duration = (end_time - start_time).total_seconds()
    
    print(f"回测完成，耗时: {run_duration:.2f}秒")
    
    # 提取分析结果
    trades_analysis = strategy.analyzers.trades.get_analysis()
    drawdown_analysis = strategy.analyzers.drawdown.get_analysis()
    returns_analysis = strategy.analyzers.returns.get_analysis()
    sharpe_analysis = strategy.analyzers.sharpe.get_analysis()
    sqn_analysis = strategy.analyzers.sqn.get_analysis()
    
    # 处理交易统计
    total_trades = trades_analysis.get('total', {}).get('closed', 0) or 0
    won_trades = trades_analysis.get('won', {}).get('total', 0) or 0
    lost_trades = trades_analysis.get('lost', {}).get('total', 0) or 0
    win_rate = (won_trades / max(1, won_trades + lost_trades)) * 100.0
    
    # 构建结果行
    result_row = {
        # 基础信息
        'run_id': datetime.now().strftime('%Y%m%d_%H%M%S'),
        'config_name': os.path.basename(args.html) if args.html else 'test_run',
        'data_file': os.path.basename(args.data),
        'run_duration_sec': round(run_duration, 2),
        
        # 回测设置
        'initial_cash': args.initial_cash,
        'leverage': args.leverage,
        'commission': args.commission,
        'risk_pct': args.risk_pct,
        'order_style': args.order_style,
        
        # 过滤器状态
        'use_ema_filter': int(not args.no_ema_filter),
        'use_volume_filter': int(not args.no_volume_filter), 
        'use_wt_filter': int(not args.no_wt_filter),
        'ema_fast': args.ema_fast,
        'ema_slow': args.ema_slow,
        'volume_mult': args.volume_mult,
        
        # 数据信息
        'total_bars': total_bars,
        'first_date': first_dt,
        'last_date': last_dt,
        
        # 交易统计
        'total_trades': total_trades,
        'won_trades': won_trades,
        'lost_trades': lost_trades,
        'win_rate_pct': round(win_rate, 2),
        
        # 性能指标
        'final_value': round(cerebro.broker.getvalue(), 2),
        'total_return_pct': round(returns_analysis.get('rtot', 0.0) * 100, 2),
        'max_drawdown_pct': round(drawdown_analysis.get('max', {}).get('drawdown', 0.0), 2),
        'max_dd_duration': drawdown_analysis.get('max', {}).get('len', 0),
        'sharpe_ratio': round(sharpe_analysis.get('sharperatio', 0.0), 3),
        'sqn': round(sqn_analysis.get('sqn', 0.0), 2),
    }
    
    # 保存结果
    write_summary_csv(args.summary_csv, result_row)
    
    # 保存元数据
    if args.write_meta and args.html:
        meta_data = {
            'args': vars(args),
            'strategy_params': strategy_params,
            'data_info': {
                'first_date': first_dt,
                'last_date': last_dt,
                'total_bars': total_bars,
                'timeframe': '4H'
            },
            'run_info': {
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': run_duration
            }
        }
        write_meta_json(args.html, meta_data)
    
    # 生成图表
    if args.html:
        plot_bokeh_chart(cerebro, args.html)
    
    # 打印结果摘要
    print("\n" + "="*70)
    print("回测结果摘要")
    print("="*70)
    print(f"总交易次数: {total_trades}")
    print(f"胜率: {win_rate:.1f}%")
    print(f"最终权益: ${result_row['final_value']}")
    print(f"总收益率: {result_row['total_return_pct']:.2f}%")
    print(f"最大回撤: {result_row['max_drawdown_pct']:.2f}%")
    print(f"夏普比率: {result_row['sharpe_ratio']:.3f}")
    print(f"SQN: {result_row['sqn']:.2f}")
    
    print(f"\n结果已保存到: {args.summary_csv}")
    
    return cerebro, strategy


if __name__ == '__main__':
    main()