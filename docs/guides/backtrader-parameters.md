# Backtrader 参数参考手�?

## 概述

本手册是 Backtrader 参数配置的“字典”。当你需要了解某个具体参数的用法时，可以在这里快速查阅。本文档采用�?*参数 - 解释 - 示例**”的结构�?

---

### 目录
1.  [策略参数 (Strategy)](#1-策略参数-strategy)
2.  [数据源参�?(Data Feeds)](#2-数据源参�?data-feeds)
3.  [经纪商参�?(Broker)](#3-经纪商参�?broker)
4.  [策略优化参数 (Optimization)](#4-策略优化参数-optimization)
5.  [分析器参�?(Analyzers)](#5-分析器参�?analyzers)

---

## 1. 策略参数 (Strategy)

在策略类内部通过 `params` 元组定义�?

- **用�?*: 定义策略内部的可调参数，如指标周期、风险比例等�?
- **示例**:
  ```python
  class MyStrategy(bt.Strategy):
      params = (
          ('period', 20),           # 移动平均周期
          ('risk_percent', 0.02),   # 风险比例
          ('print_log', True),      # 是否打印日志
      )
      
      def __init__(self):
          # 在策略中使用参数
          self.sma = bt.indicators.SMA(self.data.close, period=self.p.period)
  ```
- **覆盖**: 可在 `addstrategy` 时或通过配置文件覆盖默认值�?
  ```python
  # �?cerebro 中覆�?
  cerebro.addstrategy(MyStrategy, period=30)
  ```

---

## 2. 数据源参�?(Data Feeds)

在加载数据时配置，通常使用 `bt.feeds.GenericCSVData` 或其子类�?

- **用�?*: 定义数据文件的格式、时间范围和其他属性�?
- **核心参数**:
    - `dataname`: CSV 文件路径�?
    - `dtformat`: 日期时间格式。对于毫秒级时间戳，通常需要自定义一个数据类�?
    - `timeframe`: 数据的时间框架，�?`bt.TimeFrame.Minutes`�?
    - `compression`: 时间压缩率。例如，`timeframe` 为分钟，`compression` �?240，代�?小时线�?
    - `fromdate`, `todate`: 回测的起止日期�?
- **示例**:
  ```python
  # 自定义数据类以处理毫秒时间戳
  class MillisecondCSVData(bt.feeds.GenericCSVData):
      params = (
          ('dtformat', lambda x: datetime.datetime.utcfromtimestamp(float(x) / 1000)),
      )

  # 加载数据
  data = MillisecondCSVData(
      dataname='data.csv',
      datetime=0,        # 时间列索�?
      open=1,            # 开盘价列索�?
      high=2,            # 最高价列索�?
      low=3,             # 最低价列索�?
      close=4,           # 收盘价列索引
      volume=5,          # 成交量列索引
      timeframe=bt.TimeFrame.Minutes,
      compression=240,   # 4小时
      fromdate=datetime.datetime(2022, 1, 1)
  )
  cerebro.adddata(data)
  ```

---

## 3. 经纪商参�?(Broker)

通过 `cerebro.broker` 对象进行设置�?

- **用�?*: 模拟真实的交易环境，包括资金、手续费、滑点和杠杆�?
- **核心方法**:
    - `setcash(cash)`: 设置初始资金�?
    - `setcommission(commission, commtype, mult)`: 设置手续费�?
    - `set_slippage_perc(perc)`: 设置百分比滑点�?
- **手续�?(`setcommission`) 详解**:
    - `commission`: 费率�?
    - `commtype`: 手续费类型�?
        - `bt.CommInfoBase.COMM_PERC`: 百分�?(默认)�?
        - `bt.CommInfoBase.COMM_FIXED`: 固定金额�?
    - `mult`: 杠杆乘数 (保证金交�?�?
- **示例**:
  ```python
  # 设置初始资金
  cerebro.broker.setcash(10000.0)

  # 设置0.1%的百分比手续�?
  cerebro.broker.setcommission(commission=0.001)

  # 设置10倍杠杆的保证�?
  cerebro.broker.setcommission(commission=0.001, mult=10)
  ```

---

## 4. 策略优化参数 (Optimization)

使用 `cerebro.optstrategy` 代替 `addstrategy`�?

- **用�?*: 对策略参数进行优化，寻找最佳参数组合�?
- **配置**: 在调�?`optstrategy` 时，为需要优化的参数传入一个可迭代对象 (�?`range` 或列�?�?
- **示例**:
  ```python
  # 定义参数范围
  cerebro.optstrategy(
      MyStrategy,
      period=range(10, 51, 5),      # 测试周期 10, 15, ..., 50
      risk_percent=[0.01, 0.02, 0.03]  # 测试三种风险比例
  )

  # 运行优化，可指定CPU核心�?
  results = cerebro.run(maxcpus=4)
  ```

---

## 5. 分析器参�?(Analyzers)

通过 `cerebro.addanalyzer` 添加�?

- **用�?*: 在回测结束后，计算并提供详细的性能指标�?
- **常用分析�?*:
    - `bt.analyzers.SharpeRatio`: 夏普比率�?
    - `bt.analyzers.DrawDown`: 最大回撤�?
    - `bt.analyzers.Returns`: 收益率�?
    - `bt.analyzers.TradeAnalyzer`: 交易分析 (胜率、盈亏等)�?
- **命名与访�?*: 使用 `_name` 参数为分析器命名，便于后续访问结果�?
- **示例**:
  ```python
  # 添加分析器并命名
  cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
  cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
  cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

  # 运行回测
  results = cerebro.run()

  # 获取分析结果
  sharpe_ratio = results[0].analyzers.sharpe.get_analysis()['sharperatio']
  max_drawdown = results[0].analyzers.drawdown.get_analysis()['max']['drawdown']
  win_rate = results[0].analyzers.trades.get_analysis()['won']['total'] / results[0].analyzers.trades.get_analysis()['total']['total']
  ```

