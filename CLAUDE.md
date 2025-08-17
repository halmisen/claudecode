# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Architecture

This is a professional cryptocurrency trading strategy backtesting system built on Backtrader with advanced Bokeh visualization. The codebase follows a modular architecture centered around translating Pine Script strategies to Python for rigorous backtesting and analysis.

### 🖥️ Development Environment

**Primary Platform**: Windows 11  
**Shell Commands**: PowerShell/Windows CMD compatible  
**Python Environment**: Windows-native Python with virtual environments

⚠️ **Important**: All command-line instructions and automated scripts must use Windows-compatible syntax. Use PowerShell commands when cross-platform compatibility is needed.

### 🚀 项目状态总览

#### Vegas Tunnel XZ 项目 (已归档)
**当前版本**: Vegas Tunnel XZ Strategy v1.3 END ✅  
**文件位置**: `pinescript/strategies/trend/Vegas_Tunnel_XZ_v1_3_end_strategy.pine`  
**项目状态**: 已完成并归档 - 专注转向波段策略开发  
**核心功能**: 五条EMA隧道系统 + ADX + MACD多重确认，低胜率(~40%)趋势跟踪策略

#### 四剑客波段策略 (当前主力)
**当前版本**: Four Swords Swing Strategy v1.7.4 ⭐⭐⭐⭐⭐  
**Pine Script**: `pinescript/strategies/oscillator/Four_Swords_Swing_Strategy_v1_7_4.pine`  
**Python实现**: `backtester/strategies/four_swords_swing_strategy_v1_7_4.py`  
**运行器**: `backtester/run_four_swords_v1_7_4.py`  
**项目状态**: ✅ 生产级优化完成 - 新基线配置锁定 (2025-08-16)  
**开发进度**: v1.7.4完整实现，5.6年历史数据验证，性能突破

**核心功能** (v1.7.4):
- 🎯 基于SQZMOM_WaveTrend + 智能退出逻辑
- 🛡️ 智能状态管理：动量加速等待压缩退出 vs 动量衰竭直接退出
- ⚙️ 可选EMA趋势过滤 + Volume + WaveTrend多重过滤器
- 📊 **新基线突破**: limit_offset=0.0实现Maker模式最优性能
- 🏆 **认证指标**: 26.24%总收益率，61.59%胜率，2.056夏普比率

### 📁 Current Project Structure

```
BIGBOSS/
├── 📋 CLAUDE.md                   # 项目指南和架构文档
├── 📋 README.md                   # 项目概览和快速入门
├── 📋 CLAUDE_GEMINI_MEGA_COLLABORATION_EXECUTION_MASTER_DOCUMENT.md  # 协作执行主文档
├── 🔧 .gitignore                  # Git忽略文件配置
├── 🔧 .env                        # 环境变量 (API密钥等)
├── 🗂️ backtester/                # 🐍 Python回测系统
│   ├── 🔧 run_doji_ashi_strategy_v5.py    # ⭐ V5主运行器 (RECOMMENDED)
│   ├── 🔧 run_four_swords_v1_7_4.py       # ⭐ Four Swords主运行器 (NEW BASELINE)
│   ├── 📁 strategies/
│   │   ├── 🔧 doji_ashi_strategy_v5.py    # ⭐ V5策略实现 (RECOMMENDED)
│   │   └── 🔧 four_swords_swing_strategy_v1_7_4.py  # ⭐ Four Swords策略 (OPTIMIZED)
│   ├── 📁 deprecated_v1_7_4/              # 🗄️ Four Swords旧版本备份
│   ├── 📁 utils/
│   │   └── 🔧 plotly_bt.py               # 可视化工具
│   ├── 📁 data/                          # 📊 历史市场数据
│   │   ├── 📁 BTCUSDT/, ETHUSDT/, SOLUSDT/ ...
│   │   └── 📁 [SYMBOL]/[INTERVAL]/
│   │       ├── 📁 zips/                  # 原始ZIP文件
│   │       ├── 📁 csv/                   # 解压的月度CSV
│   │       └── 📄 [SYMBOL]-merged.csv    # 合并的完整数据
│   └── 📁 venv/                          # Python虚拟环境
├── 📁 pinescript/                 # 📊 Pine Script策略和指标
│   ├── 📁 indicators/
│   │   ├── 📁 trend/              # 趋势指标
│   │   ├── 📁 oscillator/         # 震荡器指标
│   │   ├── 📁 volume/            # 成交量指标
│   │   ├── 📁 structure/         # 结构分析
│   │   ├── 📁 risk/              # 风险管理
│   │   └── 📁 ml/                # 机器学习指标
│   └── 📁 strategies/
│       ├── 📁 trend/              # 趋势跟踪策略
│       ├── 📁 reversal/           # 反转策略  
│       └── 📁 oscillator/         # 震荡器策略
│           └── ⭐ Four_Swords_Swing_Strategy_v1_4.pine  # 四剑客v1.4 (最新版)
├── 📁 plots/                      # 📈 生成的可视化图表
│   └── 📄 *.html                  # Bokeh交互式图表
├── 📁 scripts/                    # 🔧 辅助脚本
│   └── 🔧 download_data.py        # 数据下载脚本
├── 📁 examples/                   # 📚 使用示例
│   └── 🔧 run_csv_and_plot.py     # CSV绘图示例
├── 📁 config/                     # ⚙️ 配置文件
│   ├── 📄 requirements.txt         # 主要依赖
│   └── 📄 requirements-local.txt   # 本地专用依赖
├── 📁 docs/                       # 📚 技术文档
│   ├── 📁 standards/                      # 📏 标准规范 (CLAUDE.md引导)
│   │   ├── 📄 pine-script-standards.md    # Pine Script编码规范
│   │   └── 📄 trading-parameters.md       # 默认交易参数
│   ├── 📁 guides/                         # 📖 使用指南
│   │   ├── 📄 backtrader-quickstart.md    # Backtrader快速入门
│   │   ├── 📄 backtrader-architecture.md  # Backtrader架构指南
│   │   ├── 📄 backtrader-parameters.md    # Backtrader参数参考
│   │   ├── 📄 v5-usage.md                 # V5使用指南
│   │   └── 📄 context-management.md       # 上下文管理指南
│   ├── 📁 workflows/                      # 🔄 工作流程 (核心)
│   │   ├── 📄 pine-to-python-conversion.md # Pine Script转Python流程
│   │   ├── 📄 tradingview-testing-guide.md # TradingView回测标准
│   │   └── 📄 development-workflow.md     # 开发工作流程
│   ├── 📁 troubleshooting/               # 🔧 问题修复
│   │   ├── 📄 backtrader-returns-fix.md  # 技术问题解决
│   │   ├── 📄 v4-optimization-log.md     # V4优化日志
│   │   └── 📄 v5-development-log.md      # V5开发日志
│   ├── 📁 templates/                      # 📝 代码模板
│   │   ├── 📄 kelly-criterion.pine        # Kelly准则模板
│   │   └── 📄 strategy-config.pine        # 策略配置模板
│   └── 📄 README.md                       # 文档概览
└── 📁 deprecated_v4/              # 🗄️ 已废弃的V4文件备份
    ├── 🔧 run_doji_ashi_strategy_v4.py     # V4运行器 (已废弃)
    ├── 🔧 doji_ashi_strategy_v4.py         # V4策略 (已废弃)
    └── 📄 *.html, *.png                   # V4相关图表
```

### Core Components

**Strategy Development Pipeline**: Pine Script prototypes in `pinescript/` → Python implementations in `backtester/strategies/` → Execution via runners in `backtester/run_*.py`

**Data Management**: Raw market data stored as ZIP archives in `backtester/data/` with automatic preprocessing and validation for OHLCV formats from Binance

**Visualization Engine**: **V5 System** - backtrader-plotting + Bokeh interactive web charts with zero performance overhead

### Dependency Architecture

The codebase uses **graceful degradation** with capability detection:
- Core dependencies (backtrader, pandas, numpy) are required
- Optional dependencies (TA-Lib, plotly-resampler) enable enhanced features
- Each strategy file includes standardized import guards with `HAS_*` flags
- Missing optional dependencies trigger automatic fallbacks

## Common Commands

### Environment Setup
```bash
# Activate virtual environment
backtester\venv\Scripts\activate

# Install core dependencies 
pip install backtrader pandas numpy backtrader-plotting

# Install optional TA-Lib (requires precompiled binary)
pip install TA-Lib
```

### Running Strategies
```bash
# Run Four Swords v1.7.4 with optimized baseline configuration (NEW BASELINE)
python backtester\run_four_swords_v1_7_4.py --data backtester\data\BTCUSDT\4h\BTCUSDT-4h-merged.csv --initial_cash 500 --leverage 4 --risk_pct 0.20 --order_style maker --limit_offset 0.0 --no_ema_filter --no_volume_filter --no_wt_filter

# Run Doji Ashi v5 with Bokeh interactive visualization (RECOMMENDED)
python backtester\run_doji_ashi_strategy_v5.py --data backtester\data\ETHUSDT\2h\ETHUSDT-2h-merged.csv --market_data backtester\data\BTCUSDT\2h\BTCUSDT-2h-merged.csv --market_type crypto --cash 500.0 --commission 0.0002 --trade_direction long --enable_backtrader_plot

# Run with custom parameters
python backtester\run_doji_ashi_strategy_v5.py --data [data_file] --market_type crypto --cash 1000 --leverage 2.0 --atr_multiplier 2.0

# Historical reference (v4 - deprecated)
python backtester\run_doji_ashi_strategy_v4.py --data [data_file] --market_type crypto --enable_plotly --plot_theme plotly_dark
```

### Data Download
```bash
# Download 4-hour BTCUSDT data
python scripts\download_data.py --symbol BTCUSDT --interval 4h

# Download and merge into single CSV  
python scripts\download_data.py --symbol ETHUSDT --interval 2h --merge-csv

# Download COIN-M futures data
python scripts\download_data.py --symbol BTCUSD_PERP --interval 1h --market cm
```

### Visualization Options
```bash
# V5: Bokeh interactive web charts (recommended)
# Automatically generates HTML files: plots/doji_ashi_v5_bokeh_crypto_TIMESTAMP.html
# Opens in browser with full interactivity

# V4: Plotly charts (deprecated - kept for reference)
python examples\run_csv_and_plot.py --csv [ohlcv.csv] --trades [trades.csv] --equity [equity.csv] --out reports\plot.html --title "Strategy Backtest"
```

## Code Standards and Import Template

### Standardized Import Structure
All Python strategy files must follow this import template for consistent dependency management:

```python
"""
Strategy docstring with Pine Script source reference
"""
from __future__ import annotations

# --- Standard Library ---
import datetime
from typing import Optional, Dict, List, Any

# --- Core Scientific ---
import numpy as np
import pandas as pd

# --- Backtesting ---
import backtrader as bt
import backtrader.indicators as btind

# TA-Lib (optional with capability detection)
try:
    import talib
    HAS_TALIB = True
except Exception:
    talib = None
    HAS_TALIB = False

# --- Visualization (Enhanced Plotly Support) ---
try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    HAS_PLOTLY = True
except Exception:
    go = None
    make_subplots = None
    HAS_PLOTLY = False

try:
    from plotly_resampler import FigureResampler
    HAS_PLOTLY_RESAMPLER = True
except Exception:
    FigureResampler = None
    HAS_PLOTLY_RESAMPLER = False
```

### Pine Script Development Standards
- All Pine Script files use `.pine` extension
- Naming convention: `Category_Name_v1_2.pine` (underscores, no spaces)
- Standardized summary modules: `// ⌘ SUMMARY:` with Type, Purpose, Key Inputs, etc.
- File organization: `pinescript/indicators/[category]/` and `pinescript/strategies/[category]/`

## Strategy Architecture

### Multi-Market Strategy System
Strategies support different market types through configuration:
- **Crypto Mode**: Uses BTC filter, crypto-specific indicators
- **Stocks Mode**: Uses SPY filter, relative strength analysis

### Technical Indicator Hierarchy
1. **TA-Lib** (preferred, if available)
2. **Backtrader built-ins** (fallback)
3. **pandas_ta** (optional enhancements)
4. **Custom implementations** (ZLEMA, HMA, etc.)

### Visualization Integration

**V5 Strategy (RECOMMENDED)** - backtrader-plotting + Bokeh:
- Native Backtrader visualization with zero overhead
- Interactive Bokeh web charts automatically generated
- HTML output for easy sharing and analysis
- Superior strategy performance (103% vs 38% returns)
- No data collection impact on strategy execution

**V4 Strategy (DEPRECATED)** - Plotly integration:
- Multi-panel layouts (price/indicators, volume, portfolio value)  
- Interactive technical indicators (EMA, SMA, VWAP)
- Trade signal markers with detailed hover information
- Performance impact due to data collection overhead

## Data Processing

### Expected Data Formats
- **OHLCV Files**: Columns must include open, high, low, close, volume
- **Time Indexing**: Supports datetime, timestamp, open_time columns with auto-detection
- **Timestamp Formats**: Millisecond Unix timestamps, ISO date strings, pandas datetime
- **Missing Data**: Automatic forward-fill and validation

### Data Preprocessing Pipeline
1. **ZIP Extraction**: Automatic extraction from `backtester/data/[symbol]/[interval]/zips/`
2. **Format Validation**: OHLCV column verification and type conversion  
3. **Time Indexing**: Convert timestamps to pandas DatetimeIndex
4. **Deduplication**: Remove duplicate timestamps, sort chronologically
5. **Merging**: Optional CSV merging for continuous datasets

## Testing and Development

### Strategy Development Workflow
1. Create/modify Pine Script in `pinescript/strategies/`
2. Test strategy logic in TradingView
3. Implement Python version following import template
4. Use V5 runner for optimal performance and Bokeh visualization
5. Compare results with Pine Script implementation

### File Organization Standards
- **Four Swords Strategy (NEW BASELINE)**: `backtester/strategies/four_swords_swing_strategy_v1_7_4.py`
- **Four Swords Runner (NEW BASELINE)**: `backtester/run_four_swords_v1_7_4.py`
- **Main Strategy (V5)**: `backtester/strategies/doji_ashi_strategy_v5.py`
- **Main Runner (V5)**: `backtester/run_doji_ashi_strategy_v5.py`
- **Legacy (V4)**: `deprecated_v4/doji_ashi_strategy_v4.py` (moved to backup)
- **Four Swords Legacy**: `backtester/deprecated_v1_7_4/` (old versions)
- **Documentation**: `DEVELOPMENT_LOG.md` (Four Swords), `docs/development_log_v5_final_solution.md` (V5)
- **Pine Scripts**: `pinescript/strategies/[category]/[Strategy_Name].pine`

## Debugging and Performance

### Performance Optimization (V5)
- **Zero data collection overhead**: V5 uses native Backtrader visualization
- **Faster execution**: ~1.3 seconds vs 15+ seconds for V4
- **Lower memory usage**: Single data store (no duplicate plot data)
- **Better strategy performance**: 103% vs 38% returns due to no execution interference

### Common Issues and Solutions
- **backtrader-plotting**: Install with `pip install backtrader-plotting`
- **TA-Lib Installation**: Requires precompiled binary on Windows
- **Bokeh compatibility**: Uses Bokeh 2.3.x (included with backtrader-plotting)
- **Time Zone Handling**: All timestamps converted to timezone-naive for consistency
- **HTML Output**: Charts saved to `plots/doji_ashi_v5_bokeh_*.html`

### Legacy V4 Issues (Deprecated)
- **Plotly memory usage**: High memory consumption due to duplicate data
- **Data collection overhead**: Performance impact from real-time data collection
- **Dependency conflicts**: Complex plotly-resampler version management

## Specialized Agents Configuration

This project uses Claude Code specialized agents for enhanced development capabilities:

### Core Trading Agents
- **pine-script-specialist**: Pine Script v5 development, syntax validation, and compilation error prevention ⭐ NEW
- **quant-analyst**: Quantitative strategy analysis, backtesting optimization, performance metrics evaluation
- **risk-manager**: Portfolio risk assessment, drawdown analysis, position sizing optimization
- **data-scientist**: Market data pattern analysis, statistical validation, correlation studies

### Supporting Agents  
- **data-engineer**: ETL pipeline optimization, data preprocessing automation
- **ml-engineer**: Machine learning model development for predictive signals (optional)

### Pine Script Specialist Agent Features ⭐
- **Auto-activation**: Triggers on keywords like "pine script", "tradingview", "strategy", "SQZMOM", "WaveTrend"
- **Syntax validation**: Prevents Pine Script v5 compilation errors before they happen
- **Standards compliance**: Always references `docs/standards/pine-script-standards.md`
- **Error prevention**: Catches series vs simple type conflicts, undeclared variables, etc.
- **Location**: `.claude/agents/pine-script-specialist.md` (project-tracked for team collaboration)

### Agent Usage
- **Auto-invocation**: Claude automatically selects appropriate agents based on task context
- **Explicit invocation**: Mention agent name directly (e.g., "Ask pine-script-specialist to fix this syntax error")
- **Installation**: Agents located in `~/.claude/agents/` (global) and `.claude/agents/` (project-local)

### Preferred Agent Workflows
- Pine Script development → **pine-script-specialist**
- Strategy optimization → **quant-analyst**
- Risk analysis → **risk-manager** 
- Data quality issues → **data-scientist**
- Pipeline performance → **data-engineer**
- Advanced ML features → **ml-engineer**

## File Organization and Path Management

### Lessons Learned from File Organization Process

#### Common Windows Path Issues and Solutions

**Problem**: File movement operations failing in mixed bash/PowerShell environment
- **Cause**: Using `move` command in bash environment on Windows
- **Solution**: Use PowerShell commands: `Move-Item`, `Copy-Item`, `Remove-Item`
- **Best Practice**: For problematic moves, use copy-then-delete approach

**Problem**: Directory creation creating files instead of directories
- **Cause**: Using `mkdir` with incorrect syntax or environment conflicts
- **Solution**: Use PowerShell `New-Item -Path [path] -ItemType Directory`
- **Verification**: Always use `Test-Path [path] -PathType Container` to verify

#### File Organization Strategy

**Successful Organization Pattern**:
```
Root Directory (Keep Minimal):
├── CLAUDE.md (project guide)
├── README.md (overview) 
└── [USER_SPECIFIED_FILES] (e.g., collaboration documents)

docs/ (All Technical Documentation):
├── archive/ (completed projects)
├── chinese/ (language-specific docs)
├── project-planning/ (roadmaps, guides)
├── templates/ (code templates)
└── [technical_documents.md]
```

#### Path Reference Management

**Critical Steps for Path Updates**:
1. **Before moving files**: Search all documentation for existing path references
   ```bash
   grep -r "filename.md" . --include="*.md"
   ```

2. **Update documentation structure diagrams**: Always update project structure sections in CLAUDE.md

3. **Update cross-references**: Check for relative path references in documentation files

4. **Verification**: Test all documented paths after reorganization

#### Windows-Specific Command Patterns

**Safe File Operations**:
```powershell
# Test if path exists as directory
Test-Path "path" -PathType Container

# Safe file move (copy-then-delete)
Copy-Item "source" "destination"
Remove-Item "source"

# Create directory reliably
New-Item -Path "path" -ItemType Directory -Force
```

**Error Recovery**:
- If files disappear during move operations, check if they were created as files instead of moved
- Always verify target directories exist before moving files
- Use absolute paths to avoid confusion

#### Documentation Maintenance

**Best Practices**:
- Keep project structure diagrams in CLAUDE.md updated with actual file layout
- Use relative paths in documentation for portability
- Mark deprecated or moved files clearly in documentation
- Create backup organization folders for future use

## Documentation Quick Reference

### 🔄 工作流程 (核心)
- [`docs/workflows/pine-to-python-conversion.md`](docs/workflows/pine-to-python-conversion.md) - Pine Script到Python完整转换流程
- [`docs/workflows/tradingview-testing-guide.md`](docs/workflows/tradingview-testing-guide.md) - TradingView回测标准和评估矩阵
- [`docs/workflows/development-workflow.md`](docs/workflows/development-workflow.md) - 命令行操作和Git工作流

### 📏 标准规范 (CLAUDE.md引导)
- [`docs/standards/pine-script-standards.md`](docs/standards/pine-script-standards.md) - Pine Script编码标准和规范
- [`docs/standards/trading-parameters.md`](docs/standards/trading-parameters.md) - 默认交易参数文档
- [`docs/templates/kelly-criterion.pine`](docs/templates/kelly-criterion.pine) - Kelly准则仓位管理模板
- [`docs/templates/strategy-config.pine`](docs/templates/strategy-config.pine) - 策略配置模板

### 📖 使用指南
- [`docs/guides/backtrader-quickstart.md`](docs/guides/backtrader-quickstart.md) - Backtrader框架快速入门
- [`docs/guides/backtrader-architecture.md`](docs/guides/backtrader-architecture.md) - Backtrader架构深度指南
- [`docs/guides/backtrader-parameters.md`](docs/guides/backtrader-parameters.md) - 完整参数参考
- [`docs/guides/v5-usage.md`](docs/guides/v5-usage.md) - V5系统使用和最佳实践
- [`docs/guides/context-management.md`](docs/guides/context-management.md) - 大项目上下文管理

### 🔧 问题修复与故障排除
- [`docs/troubleshooting/backtrader-returns-fix.md`](docs/troubleshooting/backtrader-returns-fix.md) - 技术问题解决方案
- [`docs/troubleshooting/v5-development-log.md`](docs/troubleshooting/v5-development-log.md) - V5系统开发日志
- [`docs/troubleshooting/v4-optimization-log.md`](docs/troubleshooting/v4-optimization-log.md) - V4优化历史记录

### 📋 项目文档
- [`docs/README.md`](docs/README.md) - 文档概览和索引

**快速访问提示**:
- Pine Script策略开发 → 查看 `docs/standards/pine-script-standards.md`
- 转换流程规划 → 参考 `docs/workflows/pine-to-python-conversion.md`
- TradingView回测 → 使用 `docs/workflows/tradingview-testing-guide.md`
- Backtrader问题调试 → 检查 `docs/troubleshooting/backtrader-returns-fix.md`
- V5系统优化 → 参考 `docs/guides/v5-usage.md`
- 参数设置 → 使用 `docs/standards/trading-parameters.md`