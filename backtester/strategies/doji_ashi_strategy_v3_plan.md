# Doji Ashi Strategy v3 开发文档

## 项目概述

Doji Ashi Strategy v3 是基于 Pine Script `Doji_Ashi_Strategy_v2.6.pine` 的完整 Python 实现，专为 Backtrader 回测框架设计。该版本相比 v2 版本有显著改进，更完整地复现了原始 Pine Script 的功能和逻辑。

**源文件路径**: `claudecode/pinescript/strategies/reversal/Doji_Ashi_Strategy_v2.6.pine`  
**目标实现**: `claudecode/backtester/strategies/doji_ashi_strategy_v3.py`

---

## 核心改进 (v3 vs v2)

### 1. **Market Type 预设模式**
- **Pine Script 原版**: 支持 "Stocks" 和 "Crypto" 预设，自动配置相应过滤器
- **v2 实现**: 缺失预设模式，需要手动配置所有过滤器
- **v3 改进**: 
  - ✅ 完整实现 `market_type` 参数 ("stocks"/"crypto")
  - ✅ Crypto 模式自动启用 BTC 市场过滤器
  - ✅ Stocks 模式支持 SPY 过滤器和相对强度过滤器

### 2. **相对强度过滤器增强**
- **Pine Script 原版**: `rel_strength = close / spy`, 比较与 SMA 的关系
- **v2 实现**: 基础实现，逻辑不完整
- **v3 改进**: 
  - ✅ 准确计算相对强度线: `close / market_close`
  - ✅ 相对强度 MA 比较逻辑
  - ✅ 仅在 Stocks 模式下启用

### 3. **市场过滤器强度计算**
- **Pine Script 原版**: 计算市场指数相对于其 SMA 的强度百分比
- **v2 实现**: 缺失市场强度计算
- **v3 改进**: 
  - ✅ 实现 `market_strength` 计算
  - ✅ 支持后续可视化扩展

### 4. **时间过滤器改进**
- **Pine Script 原版**: 复杂的时区和市场开盘时间处理
- **v2 实现**: 简化的时间过滤器
- **v3 改进**: 
  - ✅ 更精确的时间参数映射
  - ✅ 支持 `ignore_hour`、`ignore_minute`、`ignore_minutes`
  - 📝 注意: 实际时区处理仍需根据具体交易时段调整

### 5. **完整参数映射**
- **Pine Script 原版**: 33 个主要参数
- **v2 实现**: 部分参数缺失或命名不一致
- **v3 改进**: 
  - ✅ 完整映射所有主要参数
  - ✅ 参数命名与 Pine Script 保持一致
  - ✅ 合理的默认值设置

---

## 功能特性

### 🔧 **多重过滤器系统**

1. **日线趋势过滤器**
   - SMA 20/50/200 的通过计数
   - Strict 模式: 全部通过(3/3) 或全部不通过(0/3)
   - Flexible 模式: 多数通过(≥2/3) 或少数通过(≤1/3)

2. **市场过滤器** (Market Filter)
   - Crypto 模式: 自动使用 BTC/USDT 作为市场指标
   - Stocks 模式: 支持 SPY 或其他市场指数
   - 市场趋势方向必须与交易方向一致

3. **相对强度过滤器** (仅 Stocks 模式)
   - 计算个股相对市场指数的强度
   - 多头交易要求个股强于指数
   - 空头交易要求个股弱于指数

4. **3/8 MA 触发器**
   - 支持 Cross 模式: 交叉触发
   - 支持 Above/Below 模式: 状态触发
   - 默认使用 EMA，支持 TA-Lib 优化

5. **VWAP 过滤器**
   - 多头交易要求价格在 VWAP 之上
   - 空头交易要求价格在 VWAP 之下

6. **相对成交量过滤器**
   - 成交量必须超过 N 期均值的指定倍数
   - 默认: 20 期均值的 1.2 倍

7. **时间过滤器**
   - 避免特定时间段交易
   - 支持 UTC 时区设置

### 🎯 **风险管理系统**

1. **ATR 基础的止损止盈**
   - 止损: 入场价 ± ATR × 倍数
   - 止盈: 风险回报比 × 止损距离
   - 支持 OCO 订单

2. **追踪止损** (可选)
   - 百分比追踪止损
   - 替代固定止损止盈

3. **时间退出** (可选)
   - 最大持仓 K 线数限制
   - 防止长期被套

4. **仓位管理**
   - 股权百分比仓位sizing
   - 支持杠杆计算
   - 最小仓位和步长控制

5. **交易冷却期**
   - 同方向交易间隔 K 线数
   - 防止过度交易

### 📊 **技术指标**

- **移动平均线**: EMA (支持 TA-Lib 加速)
- **ATR**: 真实波幅 (支持 TA-Lib)
- **VWAP**: 成交量加权平均价
- **成交量指标**: SMA 成交量均线

---

## 参数配置指南

### 🏗️ **基础设置**

```python
# 市场类型和方向
market_type="crypto",           # "stocks" | "crypto"  
trade_direction="both",         # "long" | "short" | "both"
```

### 🔍 **过滤器开关**

```python
# 主要过滤器
enable_daily_trend_filter=True,     # 日线趋势过滤器
enable_entry_trigger=True,          # 3/8 MA 触发器
enable_market_filter_input=False,   # 市场过滤器 (仅 Stocks 模式手动)
enable_relative_strength=False,     # 相对强度过滤器 (仅 Stocks 模式)

# 辅助过滤器  
enable_volume_filter=False,         # 相对成交量过滤器
enable_vwap_filter_entry=False,     # VWAP 入场过滤器
enable_time_filter=False,           # 时间过滤器
```

### ⚙️ **技术参数**

```python
# 3/8 MA 触发器
trigger_ma_type="EMA",              # 移动平均类型
entry_mode="above_below",           # "cross" | "above_below"
fast_ma_len=3,                      # 快速 MA 长度
slow_ma_len=8,                      # 慢速 MA 长度

# 日线趋势
trend_mode="strict",                # "strict" | "flexible"
daily_sma_20=20,                    # 日线 SMA 长度
daily_sma_50=50,
daily_sma_200=200,

# ATR 风险管理
atr_length=14,                      # ATR 周期
atr_multiplier=1.5,                 # 止损距离倍数
risk_reward_ratio=2.0,              # 风险回报比
```

### 💰 **资金管理**

```python
# 仓位设置
order_percent=0.20,                 # 每笔交易占股权百分比
leverage=4.0,                       # 杠杆倍数
min_size=0.001,                     # 最小仓位
size_step=0.001,                    # 仓位步长

# 交易节奏
cooldown_bars=10,                   # 冷却期 K 线数
```

---

## 使用场景和配置建议

### 📈 **加密货币交易**

```python
DojiAshiStrategyV3(
    market_type="crypto",                    # 自动启用 BTC 过滤器
    trade_direction="both",
    enable_daily_trend_filter=True,
    trend_mode="flexible",                   # 加密市场波动大，使用灵活模式
    enable_volume_filter=True,               # 加密市场成交量重要
    enable_entry_trigger=True,
    entry_mode="above_below",                # 状态触发更适合趋势跟踪
    order_percent=0.15,                      # 更保守的仓位
    leverage=3.0,                            # 适中的杠杆
    cooldown_bars=15,                        # 较长的冷却期
)
```

### 📊 **股票交易**

```python
DojiAshiStrategyV3(
    market_type="stocks",                    # 支持 SPY 和相对强度
    trade_direction="long",                  # 股票偏向多头
    enable_daily_trend_filter=True,
    trend_mode="strict",                     # 股票市场要求更严格的趋势确认
    enable_market_filter_input=True,         # 启用 SPY 过滤器
    enable_relative_strength=True,           # 启用相对强度过滤器
    enable_vwap_filter_entry=True,          # VWAP 对日内交易重要
    enable_time_filter=True,                 # 避免开盘前30分钟
    ignore_hour=14, ignore_minute=30,        # UTC 时间设置
    ignore_minutes=30,
    order_percent=0.25,                      # 股票波动较小，可更高仓位
    leverage=2.0,                            # 更保守的杠杆
)
```

### ⚡ **高频短线**

```python
DojiAshiStrategyV3(
    entry_mode="cross",                      # 交叉触发更敏感
    fast_ma_len=2,                          # 更短的 MA 周期
    slow_ma_len=5,
    enable_volume_filter=True,               # 成交量确认重要
    enable_vwap_filter_entry=True,          # VWAP 指导入场
    cooldown_bars=5,                         # 较短的冷却期
    use_trailing_stop=True,                  # 追踪止损适合短线
    trail_offset_percent=0.5,                # 较紧的追踪距离
    max_bars_in_trade=20,                    # 短时间持仓
)
```

---

## 技术实现细节

### 🔧 **多时间框架数据**

策略支持最多 3 个数据源:
1. `datas[0]`: 主要交易数据 (例如: 4H K线)
2. `datas[1]`: 日线数据 (用于日线趋势过滤器)
3. `datas[2]`: 市场指数数据 (用于市场过滤器和相对强度)

### 📊 **指标优化**

- **TA-Lib 优先**: 当 `HAS_TALIB=True` 时使用 TA-Lib 计算 EMA 和 ATR
- **Backtrader 后备**: TA-Lib 不可用时回退到 Backtrader 内置指标
- **预热期管理**: 自动计算所需的最大预热期

### 🛡️ **订单管理**

- **OCO 订单**: 止损和止盈使用 OCO (One-Cancels-Other) 逻辑
- **追踪止损**: 支持百分比追踪止损作为替代方案
- **订单清理**: 自动清理完成或失败的订单引用

### 🔄 **状态管理**

- **冷却期**: 跟踪最后交易 K 线，防止过度交易
- **多重过滤器**: 所有激活的过滤器必须同时满足才能入场
- **未来函数预防**: 使用确认的日线数据避免回测偏差

---

## 测试和验证

### 🧪 **回测建议**

1. **数据要求**:
   - 主要数据: 至少 300 根 K 线用于指标预热
   - 日线数据: 至少 200 天历史数据
   - 市场数据: 与主要数据时间范围一致

2. **参数测试**:
   - 从保守参数开始 (trend_mode="strict", 较少过滤器)
   - 逐步增加过滤器复杂度
   - 测试不同市场条件 (牛市/熊市/震荡市)

3. **性能指标**:
   - 胜率 (Win Rate)
   - 风险回报比 (Risk-Reward Ratio)  
   - 最大回撤 (Maximum Drawdown)
   - 夏普比率 (Sharpe Ratio)
   - 系统质量数 (SQN)

### ⚠️ **已知限制**

1. **时间过滤器**: 当前实现简化，实际使用需要更精确的时区处理
2. **市场数据依赖**: Stocks 模式的过滤器需要相应的市场指数数据
3. **滑点和手续费**: 回测需要配置合理的交易成本
4. **数据质量**: 依赖准确的 OHLCV 和成交量数据

---

## 后续开发路线图

### 🚀 **v3.1 计划**
- [ ] 完善时间过滤器的时区处理
- [ ] 增加更多技术指标选项 (RSI, MACD 等)
- [ ] 实现动态参数调整功能

### 🎯 **v3.2 计划**  
- [ ] 增加机器学习信号过滤器
- [ ] 实现多品种组合交易
- [ ] 增加实时交易接口

### 📈 **长期目标**
- [ ] 完整的可视化分析面板
- [ ] 参数优化和自动调参
- [ ] 风险管理的动态调整

---

## 总结

Doji Ashi Strategy v3 是一个功能完整、高度可配置的多重过滤器交易策略。它成功地将 Pine Script 的逻辑转换为 Backtrader Python 实现，同时保持了原始策略的核心特性和灵活性。

通过合理的参数配置和过滤器组合，该策略可以适应不同的市场环境和交易风格，为量化交易提供了一个稳固的基础框架。