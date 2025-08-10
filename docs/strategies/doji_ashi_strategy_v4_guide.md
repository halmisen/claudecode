# Doji Ashi Strategy v4 开发指南

## 概述

Doji Ashi Strategy v4 是基于 Pine Script `Doji_Ashi_Strategy_v2.6.pine` 的完整 Python 实现，专为 Backtrader 框架设计。这是目前最先进和功能最完整的版本，集成了完整的 Plotly 交互式可视化系统。

**核心文件**:
- `claudecode/backtester/strategies/doji_ashi_strategy_v4.py` - 主策略实现
- `claudecode/backtester/run_doji_ashi_strategy_v4.py` - 运行脚本
- `claudecode/pinescript/strategies/reversal/Doji_Ashi_Strategy_v2.6.pine` - 源 Pine Script 参考

---

## 主要特性

### 🎯 完整功能实现
- **市场类型预设**: `Crypto` 和 `Stocks` 模式，自动配置相应过滤器
- **多重过滤器系统**: 日线趋势、市场情绪、相对强度、成交量、VWAP、时间过滤器
- **智能入场触发器**: 3/8 EMA 交叉或高低位模式
- **完善风险管理**: ATR 基础止损止盈、追踪止损、时间退出
- **灵活仓位管理**: 百分比仓位、杠杆支持、冷却期控制

### 📊 高级可视化系统
- **Plotly 集成**: 完整的交互式图表系统
- **plotly-resampler**: 大数据集性能优化
- **多面板布局**: 价格/指标、成交量、组合价值
- **实时数据收集**: 自动收集所有回测数据用于可视化
- **自动保存**: HTML 图表自动保存并在浏览器中打开

### 🔧 技术亮点
- **标准化导入**: 使用项目标准导入模板，优雅降级处理
- **能力检测**: 动态检测可用依赖，智能回退
- **多时间框架**: 支持主数据、日线数据、市场数据
- **Pine Script 对等**: 99% 参数映射完整性

---

## 核心参数配置

### 市场类型预设
```python
# 加密货币模式 (推荐用于BTC/ETH等)
market_type = "Crypto"
# 自动启用: BTC市场过滤器, 禁用相对强度

# 股票模式 (需要SPY等市场数据)
market_type = "Stocks" 
# 自动启用: SPY过滤器, 相对强度过滤器
```

### 关键过滤器配置
```python
# 日线趋势过滤器 (推荐启用)
enable_daily_trend_filter = True
trend_mode = "strict"  # strict: 3/3 SMA通过, flexible: 2/3通过

# 3/8 EMA触发器 (核心逻辑)
enable_entry_trigger = True
entry_mode = "above_below"  # 或 "cross" 交叉模式
fast_ma_len = 3
slow_ma_len = 8

# 可选增强过滤器
enable_volume_filter = False    # 相对成交量过滤
enable_vwap_filter_entry = False  # VWAP价位过滤
enable_time_filter = False      # 时间窗口过滤
```

### 风险管理设置
```python
# ATR基础风险管理
atr_length = 14
atr_multiplier = 1.5        # 止损距离
risk_reward_ratio = 2.0     # 止盈比例

# 可选追踪止损
use_trailing_stop = False
trail_offset_percent = 1.0

# 时间退出
use_time_exit = False
max_bars_in_trade = 100
```

### Plotly 可视化配置
```python
# 启用完整可视化
enable_plotly = True
use_resampler = True           # 大数据集优化
plot_indicators = True         # 显示技术指标
plot_signals = True           # 显示交易信号
plot_volume = True            # 显示成交量面板
plot_theme = "plotly_dark"    # 图表主题
max_plot_points = 5000        # resampler最大点数
```

---

## 使用方法

### 基本运行命令
```bash
# 激活环境
.\claudecode\venv\Scripts\activate

# 标准加密货币回测
python claudecode/backtester/run_doji_ashi_strategy_v4.py \
  --data claudecode/backtester/data/ETHUSDT/2h/ETHUSDT-2h-merged.csv \
  --market_type crypto \
  --enable_plotly

# 高级可视化设置
python claudecode/backtester/run_doji_ashi_strategy_v4.py \
  --data claudecode/backtester/data/BTCUSDT/4h/BTCUSDT-4h-merged.csv \
  --market_type crypto \
  --enable_plotly \
  --plot_theme plotly_dark \
  --use_resampler \
  --max_plot_points 3000
```

### 股票模式 (需要市场数据)
```bash
python claudecode/backtester/run_doji_ashi_strategy_v4.py \
  --data path/to/stock_data.csv \
  --daily_data path/to/daily_data.csv \
  --market_data path/to/spy_data.csv \
  --market_type stocks \
  --enable_plotly
```

---

## 可视化输出

### 图表结构
- **主面板**: K线图 + 技术指标 + 交易信号
  - 蜡烛图 (绿涨红跌)
  - EMA 3/8 移动平均线
  - 日线 SMA 20/50/200 (虚线)
  - VWAP (如启用)
  - 买入/卖出信号标记
  
- **成交量面板**: 成交量柱状图 + 平均成交量线
  
- **组合价值面板**: 实时权益曲线

### 交互功能
- **缩放**: 鼠标滚轮或框选缩放
- **平移**: 拖拽移动视图
- **悬停信息**: 鼠标悬停显示详细数据
- **图例切换**: 点击图例隐藏/显示指标
- **性能优化**: plotly-resampler 自动处理大数据集

### 保存路径
- 默认保存至: `claudecode/backtester/plots/`
- 文件名格式: `doji_ashi_v4_{market_type}_{timestamp}.html`
- 自动浏览器打开

---

## 开发模式和扩展

### 添加自定义指标
```python
def _setup_custom_indicators(self):
    """添加自定义技术指标"""
    # 在 __init__ 方法中调用
    if HAS_PANDAS_TA:
        # 使用pandas_ta指标
        pass
    elif HAS_TALIB:
        # 使用TA-Lib指标
        self.custom_indicator = bt.talib.INDICATOR(...)
    else:
        # 回退到Backtrader指标
        self.custom_indicator = btind.INDICATOR(...)
```

### 扩展可视化
```python
def _collect_plot_data(self):
    """收集绘图数据 - 扩展版"""
    # 调用父类方法
    super()._collect_plot_data()
    
    # 添加自定义数据
    if 'custom_indicator' not in self.plot_data:
        self.plot_data['custom_indicator'] = []
    self.plot_data['custom_indicator'].append(
        float(self.custom_indicator[0]) if len(self.custom_indicator) > 0 else np.nan
    )
```

### 参数预设扩展
```python
def _configure_custom_presets(self):
    """自定义市场预设"""
    if self.market_type == "forex":
        # 外汇市场特定设置
        self.use_market_filter = True
        self.enable_time_filter = True
        # 设置外汇交易时间
```

---

## 性能优化建议

### 大数据集处理
- 启用 `use_resampler=True` 处理 >5000 个数据点
- 调整 `max_plot_points` 平衡性能和精度
- 考虑数据预处理，过滤无关时间段

### 内存管理
- 大型回测使用 `plot_indicators=False` 减少内存占用
- 禁用不需要的过滤器减少计算负担
- 合理设置 `warmup_daily` 参数

### 并行回测
- 多个时间段或参数组合可并行运行
- 注意Plotly图表生成的内存峰值

---

## 故障排除

### 常见问题

**1. Plotly图表为空**
```python
# 检查数据收集
print(f"Collected data points: {len(self.plot_data['datetime'])}")
# 确保enable_plotly=True且HAS_PLOTLY=True
```

**2. plotly-resampler错误**
```bash
# 安装依赖
pip install plotly-resampler
# 或禁用resampler
use_resampler = False
```

**3. 内存不足**
```python
# 减少绘图数据
max_plot_points = 1000
plot_indicators = False
plot_volume = False
```

**4. 依赖缺失**
- 策略会自动降级，检查终端输出的警告信息
- 参考 `requirements.txt` 安装完整依赖

---

## 版本迁移指南

### 从 v2/v3 升级到 v4
1. **更新导入模板**: 使用 v4 的标准化导入
2. **启用Plotly**: 添加可视化相关参数
3. **检查参数映射**: v4 有更完整的参数集
4. **更新运行脚本**: 使用 `run_doji_ashi_strategy_v4.py`

### 参数映射变更
- v2/v3 → v4 参数基本兼容
- 新增可视化参数可安全忽略（默认禁用）
- 市场类型预设参数需要适配

---

## 最佳实践

### 策略开发
1. **从预设开始**: 使用 `crypto`/`stocks` 预设作为基础
2. **逐步调试**: 先禁用所有过滤器，再逐步启用
3. **可视化验证**: 利用交互式图表验证策略逻辑
4. **参数优化**: 使用网格搜索优化关键参数

### 生产使用
1. **数据质量**: 确保数据完整性和时间戳正确性
2. **风险控制**: 合理设置仓位大小和风险参数
3. **监控系统**: 实施实时监控和警报系统
4. **定期回测**: 定期使用最新数据验证策略有效性

这份指南提供了 Doji Ashi Strategy v4 的完整使用和开发指南。建议配合实际代码和交互式图表进行学习和调试。