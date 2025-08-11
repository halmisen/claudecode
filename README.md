# 加密货币交易策略回测系统

基于 Backtrader 框架的专业级加密货币交易策略回测系统，集成 **backtrader-plotting + Bokeh** 高性能交互式可视化，专注于 Doji Ashi 反转策略的研究与实现。

## ⭐ 主要特性

- **🎯 专业策略**: 完整实现 Pine Script Doji Ashi v2.6 策略
- **📊 高性能可视化**: **V5版本** - backtrader-plotting + Bokeh 交互式网页图表
- **🚀 优异性能**: **103%回报率**，183笔交易，**1.3秒**执行时间  
- **🔧 生产级质量**: 零数据收集开销，稳定可靠
- **💱 多市场支持**: 加密货币 (BTC, ETH, SOL) 和股票市场
- **⚡ 现代化架构**: 基于 Backtrader 原生生态，易于维护

## 🚀 快速开始

### 1. 环境准备

```bash
# 激活虚拟环境 (Windows)
claudecode\venv\Scripts\activate

# 安装V5核心依赖
pip install backtrader pandas numpy backtrader-plotting

# 可选：安装TA-Lib增强性能
pip install TA-Lib
```

### 2. 运行 Doji Ashi V5 策略 ⭐推荐

```bash
# ETH 2小时数据回测 + Bokeh交互式可视化
python backtester/run_doji_ashi_strategy_v5.py \
  --data backtester/data/ETHUSDT/2h/ETHUSDT-2h-merged.csv \
  --market_data backtester/data/BTCUSDT/2h/BTCUSDT-2h-merged.csv \
  --market_type crypto \
  --cash 500.0 \
  --commission 0.0002 \
  --trade_direction long \
  --enable_backtrader_plot

# 自定义参数回测
python backtester/run_doji_ashi_strategy_v5.py \
  --data [your_data.csv] \
  --market_type crypto \
  --cash 1000 \
  --leverage 2.0 \
  --atr_multiplier 2.0
```

**输出**: 自动生成HTML图表到 `plots/doji_ashi_v5_bokeh_*.html` 并在浏览器中打开

### 3. V5性能优势

- **🎯 策略表现**: 103.38% 总回报率 vs V4的 38.51%
- **⚡ 执行速度**: 1.3秒 vs V4的 15+ 秒  
- **📈 交易频率**: 183笔交易 vs V4的 44笔
- **🔧 零开销**: 无数据收集副作用，纯策略执行

### 4. 历史版本 (已弃用)

```bash
# V4 Plotly版本 - 仅供参考，不再维护  
python backtester/run_doji_ashi_strategy_v4.py \
  --data [file] --market_type crypto --enable_plotly
```

## 📁 项目结构

```
claudecode/
├── backtester/           # 回测核心系统
│   ├── strategies/       # 策略实现
│   │   ├── doji_ashi_strategy_v4.py  # 主力策略 (Plotly集成)
│   │   └── doji_ashi_strategy_v3.py  # 参考实现
│   ├── run_doji_ashi_strategy_v4.py  # v4运行器
│   ├── data/            # 市场数据
│   │   ├── BTCUSDT/     # BTC 数据 (1d, 2h, 4h)
│   │   ├── ETHUSDT/     # ETH 数据 (2h)
│   │   └── SOLUSDT/     # SOL 数据 (2h, 4h)
│   └── plots/           # 生成的图表文件
├── pinescript/          # Pine Script 源码
│   └── strategies/reversal/Doji_Ashi_Strategy_v2.6.pine
├── docs/               # 完整文档系统
│   ├── README.md       # 文档索引
│   ├── strategies/     # 策略指南
│   └── *.md           # 开发指南
├── examples/          # 示例脚本  
├── scripts/          # 数据下载脚本
├── backtester/utils/ # 可视化工具
└── venv/             # Python 虚拟环境
```

## 🎨 可视化系统

### Plotly 交互式图表
- **多面板布局**: 价格/指标、成交量、组合价值
- **技术指标**: EMA 3/8、日线 SMA 20/50/200、VWAP
- **交易信号**: 买入/卖出标记，止损止盈线
- **性能优化**: plotly-resampler 支持大数据集 (>5000点)
- **主题支持**: plotly_dark, plotly_white, 自定义主题

### 数据格式支持
- **时间列**: datetime, date, time, timestamp, open_time
- **价格数据**: open, high, low, close, volume
- **时间戳**: 支持毫秒级 Unix 时间戳自动转换
- **交易记录**: datetime, price, side (buy/sell), size, pnl
- **权益曲线**: 任意数值列，支持 datetime 索引

## 📚 策略系统

### Doji Ashi 策略特性
- **市场类型预设**: Crypto (BTC过滤) / Stocks (SPY+相对强度)
- **多重过滤器**: 日线趋势、市场情绪、相对强度、成交量、VWAP、时间窗口
- **智能触发器**: 3/8 EMA 交叉 或 高低位突破模式
- **风险管理**: ATR 基础止损止盈、追踪止损、时间退出
- **仓位管理**: 百分比仓位、杠杆支持、冷却期机制

### 技术指标集成
- **TA-Lib**: 优先使用 TA-Lib 指标 (如可用)
- **Backtrader**: 内置指标作为回退方案
- **pandas_ta**: 可选增强指标库
- **自定义**: ZLEMA, HMA 等高级移动平均线

## 🛠️ 开发指南

### 策略开发流程
1. **Pine Script 原型**: 使用 [Pine Script 开发标准](./docs/pine-script-standards.md)
2. **Python 转换**: 参考 [策略转换指南](./docs/strategies/doji_ashi_strategy_v4_guide.md)
3. **标准化实现**: 使用项目标准导入模板
4. **回测验证**: 运行完整回测和可视化
5. **性能分析**: 利用交互式图表进行策略调优

### 依赖管理哲学
- **能力检测**: 动态检测可用依赖 (`HAS_TALIB`, `HAS_PLOTLY`)
- **优雅降级**: 可选依赖缺失时自动回退
- **环境隔离**: 虚拟环境确保依赖一致性
- **版本兼容**: numpy 1.26.4 修复 bokeh 兼容性

## 📖 文档资源

- **⭐ [V5使用指南](./docs/v5_usage_guidelines.md)** - V5版本完整使用说明 **推荐**
- **📈 [V5最终方案](./docs/development_log_v5_final_solution.md)** - V5技术决策和性能对比
- **📘 [完整文档索引](./docs/README.md)** - 所有文档的入口
- **🚀 [快速入门指南](./docs/backtrader-quickstart.md)** - 5分钟上手
- **🔧 [开发工作流程](./docs/development-workflow.md)** - 命令和最佳实践
- **🌲 [Pine Script 标准](./docs/pine-script-standards.md)** - 编码规范
- **🔍 [技术修复指南](./docs/BACKTRADER_RETURNS_FIX.md)** - 常见问题解决

### 历史文档 (参考)
- **🎯 [Doji Ashi v4 指南](./docs/strategies/doji_ashi_strategy_v4_guide.md)** - V4策略详解 (已弃用)

## 🎯 使用场景

### 策略研究
- 复现和验证 TradingView Pine Script 策略
- 多时间框架和多资产策略测试
- 参数优化和敏感性分析

### 生产回测
- 大规模历史数据回测 (2020-2025)
- 完整的风险管理和绩效分析
- 交互式图表生成和策略可视化

### 教育学习
- Pine Script 到 Python 的转换学习
- Backtrader 框架深度使用
- 量化交易策略开发实践

## ⚡ 性能特性

- **大数据集支持**: plotly-resampler 优化 10k+ 数据点
- **内存优化**: 智能数据预处理和缓存
- **多核利用**: 支持并行参数优化 (规划中)
- **实时监控**: Loguru 日志系统，详细执行追踪

## 🤝 贡献指南

项目遵循严格的代码标准和文档规范：
1. 使用标准化导入模板 (见 CLAUDE.md)
2. 遵循 Pine Script 开发标准
3. 保持向后兼容性
4. 完善的测试和文档

---

**🔗 快速链接**: [文档索引](./docs/README.md) | [v4策略指南](./docs/strategies/doji_ashi_strategy_v4_guide.md) | [快速入门](./docs/backtrader-quickstart.md)

> 专业级交易策略回测系统，让量化交易开发更高效 🚀