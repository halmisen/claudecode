import backtrader as bt
import pandas as pd
import datetime

class TestStrategy(bt.Strategy):
    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=20)

    def next(self):
        if not self.position:
            if self.datas[0].close[0] > self.sma[0]:
                self.buy()
        else:
            if self.datas[0].close[0] < self.sma[0]:
                self.sell()

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    
    # 使用pandas读取CSV文件
    df = pd.read_csv('data/BTCUSDT/BTCUSDT_4h_merged.csv', header=None, 
                     names=['timestamp', 'open', 'high', 'low', 'close', 'volume', 
                            'close_time', 'quote_volume', 'trades', 'taker_buy_volume', 
                            'taker_buy_quote_volume', 'ignored'])
    
    # 确保timestamp是整数类型
    df['timestamp'] = pd.to_numeric(df['timestamp'], errors='coerce')
    
    # 修复过大的timestamp（有些有额外的零）
    max_valid_ms = pd.Timestamp.max.timestamp() * 1000
    df.loc[df['timestamp'] > max_valid_ms, 'timestamp'] = df.loc[df['timestamp'] > max_valid_ms, 'timestamp'] / 1000
    
    # 过滤掉无效的时间戳
    df = df[df['timestamp'].notna()]
    
    # 转换为datetime
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('datetime', inplace=True)
    
    # 确保价格数据是数值类型
    for col in ['open', 'high', 'low', 'close']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 创建backtrader数据对象
    data = bt.feeds.PandasData(
        dataname=df,
        timeframe=bt.TimeFrame.Minutes,
        compression=240  # 4小时=240分钟
    )
    
    cerebro.adddata(data)
    cerebro.addstrategy(TestStrategy)
    
    # 设置初始资金
    cerebro.broker.setcash(100000.0)
    
    # 添加分析器
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    
    print(f'Initial Portfolio Value: {cerebro.broker.getvalue():.2f}')
    
    # 运行回测
    results = cerebro.run()
    
    print(f'Final Portfolio Value: {cerebro.broker.getvalue():.2f}')
    
    # 打印分析结果
    strat = results[0]
    
    # 获取夏普比率
    sharpe_analysis = strat.analyzers.sharpe.get_analysis()
    if sharpe_analysis and 'sharperatio' in sharpe_analysis:
        print(f'Sharpe Ratio: {sharpe_analysis["sharperatio"]:.2f}')
    
    # 获取最大回撤
    drawdown_analysis = strat.analyzers.drawdown.get_analysis()
    if drawdown_analysis and 'max' in drawdown_analysis:
        print(f'Max Drawdown: {drawdown_analysis["max"]["drawdown"]:.2f}%')
    
    # 获取收益率
    returns_analysis = strat.analyzers.returns.get_analysis()
    if returns_analysis and 'rtot' in returns_analysis:
        print(f'Total Return: {returns_analysis["rtot"]:.2f}%')
    
    # 绘制结果 (注释掉以节省时间)
    # cerebro.plot(style='candlestick')