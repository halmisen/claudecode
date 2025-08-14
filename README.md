# 加密货币交易策略回测系统

基于 Backtrader 框架的专业级交易策略回测系统，集�?**backtrader-plotting + Bokeh** 高性能交互式可视化�?

## �?主要特�?

- **🎯 专业策略**: Four Swords v1.4波段策略 (基于SQZMOM+WaveTrend)
- **📊 高胜率系�?*: 适合INFP性格的波段交易，目标胜率75%+
- **🛡�?智能状态管�?*: 动量加速等待压�?vs 动量衰竭直接退�?
- **⚙️ 灵活配置**: EMA趋势过滤+成交量确认可独立开�?
- **💱 多市场支�?*: 加密货币 (BTC, ETH, SOL) 和股票市�?
- **�?现代化架�?*: 基于 Backtrader 原生生态，易于维护

## 🚀 快速开�?

### 1. 环境准备

```bash
# 激活虚拟环�?(Windows)
backtester\venv\Scripts\activate

# 安装V5核心依赖
pip install backtrader pandas numpy backtrader-plotting

# 可选：安装TA-Lib增强性能
pip install TA-Lib
```

### 2. 主力策略: Four Swords v1.4 ⭐推�?

```bash
# 加载v1.4策略到TradingView
# 文件: pinescript/strategies/oscillator/Four_Swords_Swing_Strategy_v1_4.pine
# 建议时间框架: 4H�?D波段交易
# 推荐配置: 保持默认设置(初学�?或开启所有过滤器(进阶)
```

### 3. Python回测系统 (可�?

```bash
# 运行Doji Ashi V5策略回测
python backtester/run_doji_ashi_strategy_v5.py \
  --data backtester/data/ETHUSDT/2h/ETHUSDT-2h-merged.csv \
  --market_type crypto \
  --enable_backtrader_plot
```

## 📁 项目结构

```
BIGBOSS/claudecode/
├── 📋 CLAUDE.md                    # Claude Code项目指南  
├── 📋 GEMINI.md                    # Gemini执行官手�?
├── 📋 README.md                    # 项目概览
├── 📁 pinescript/strategies/oscillator/
�?  └── �?Four_Swords_Swing_Strategy_v1_4.pine  # 当前主力策略
├── 📁 docs/
�?  ├── 📁 strategies/              # 策略开发文�?
�?  ├── 📁 archived/               # 归档文档  
�?  └── 📄 *.md                    # 技术文�?
└── 📁 backtester/                 # Python回测系统
```

## 📚 Four Swords v1.4 策略特�?

- **🎯 基于SQZMOM+WaveTrend**: 成功策略适度波段增强
- **🛡�?智能状态管�?*: 动量加速等待压缩退�?vs 动量衰竭直接退�?
- **⚙️ 可选EMA趋势过滤**: 20/50 EMA趋势确认
- **📊 成交量确�?*: 1.2x成交量增强信�?
- **📈 简�?状态面�?*: 压缩/动量/WT/趋势/成交量实时监�?

## 📖 文档资源

- **📋 [CLAUDE.md](./CLAUDE.md)** - 项目架构和开发指�?
- **🌲 [Pine Script 标准](./docs/standards/pine-script-standards.md)** - 编码规范
- **📚 [完整文档索引](./docs/README.md)** - 所有技术文�?

---

**专业级交易策略回测系统，专注Four Swords v1.4波段策略开�?🚀**
