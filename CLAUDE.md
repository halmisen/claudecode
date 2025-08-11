# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Architecture

This is a professional cryptocurrency trading strategy backtesting system built on Backtrader with advanced Plotly visualization. The codebase follows a modular architecture centered around translating Pine Script strategies to Python for rigorous backtesting and analysis.

### Core Components

**Strategy Development Pipeline**: Pine Script prototypes in `pinescript/` → Python implementations in `backtester/strategies/` → Execution via runners in `backtester/run_*.py`

**Data Management**: Raw market data stored as ZIP archives in `backtester/data/` with automatic preprocessing and validation for OHLCV formats from Binance

**Visualization Engine**: Dual-layer approach using traditional Backtrader plotting and advanced Plotly integration with plotly-resampler optimization for large datasets (>5K points)

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
- **Main Strategy (V5)**: `backtester/strategies/doji_ashi_strategy_v5.py`
- **Main Runner (V5)**: `backtester/run_doji_ashi_strategy_v5.py`
- **Legacy (V4)**: `backtester/strategies/doji_ashi_strategy_v4.py` (deprecated)
- **Documentation**: `docs/development_log_v5_final_solution.md`
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

This project uses Claude Code specialized agents (wshobson/agents) for enhanced analysis capabilities:

### Core Trading Agents
- **quant-analyst**: Quantitative strategy analysis, backtesting optimization, performance metrics evaluation
- **risk-manager**: Portfolio risk assessment, drawdown analysis, position sizing optimization
- **data-scientist**: Market data pattern analysis, statistical validation, correlation studies

### Supporting Agents  
- **data-engineer**: ETL pipeline optimization, data preprocessing automation
- **ml-engineer**: Machine learning model development for predictive signals (optional)

### Agent Usage
- **Auto-invocation**: Claude automatically selects appropriate agents based on task context
- **Explicit invocation**: Mention agent name directly (e.g., "Ask quant-analyst to analyze strategy performance")
- **Installation**: Agents located in `~/.claude/agents/` (local configuration, not in project git)

### Preferred Agent Workflows
- Strategy optimization → **quant-analyst**
- Risk analysis → **risk-manager** 
- Data quality issues → **data-scientist**
- Pipeline performance → **data-engineer**
- Advanced ML features → **ml-engineer**

## Documentation References

Key documentation files:
- `docs/strategies/doji_ashi_strategy_v4_guide.md`: Complete v4 strategy guide
- `docs/development-workflow.md`: Command-line operations and Git workflow
- `docs/pine-script-standards.md`: Pine Script coding standards
- `docs/backtrader-quickstart.md`: Framework quick start
- `docs/BACKTRADER_RETURNS_FIX.md`: Technical issue resolution