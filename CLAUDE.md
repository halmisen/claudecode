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

# Install dependencies 
pip install -r config\requirements.txt

# Install optional TA-Lib (requires precompiled binary)
pip install TA-Lib
```

### Running Strategies
```bash
# Run Doji Ashi v4 with Plotly visualization (recommended)
python backtester\run_doji_ashi_strategy_v4.py --data backtester\data\BTCUSDT\4h\BTCUSDT-4h-merged.csv --market_type crypto --enable_plotly --plot_theme plotly_dark

# Run with plotly-resampler for large datasets
python backtester\run_doji_ashi_strategy_v4.py --data [data_file] --market_type crypto --enable_plotly --use_resampler --max_plot_points 3000

# Traditional backtest (v3)
python backtester\run_doji_ashi_strategy_v3.py --data [data_file] --market_type crypto
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

### Visualization Tools
```bash
# Generate interactive chart from CSV data
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
Strategies with `_v4` suffix include Plotly integration:
- Multi-panel layouts (price/indicators, volume, portfolio value)
- Interactive technical indicators (EMA, SMA, VWAP)
- Trade signal markers with detailed hover information
- Performance optimizations via plotly-resampler

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
4. Use v4 runner for Plotly visualization and validation
5. Compare results with Pine Script implementation

### File Organization Standards
- **Strategies**: `backtester/strategies/[strategy_name].py`
- **Runners**: `backtester/run_[strategy_name].py`
- **Documentation**: `backtester/strategies/[strategy_name]_guide.md`
- **Pine Scripts**: `pinescript/strategies/[category]/[Strategy_Name].pine`

## Debugging and Performance

### Dependency Debugging
Check dependency status with built-in diagnostics:
```python
# In strategy runners
def check_plotly_dependencies():
    # Returns dict of available capabilities
```

### Performance Optimization
- Use `plotly-resampler` for datasets >5000 points
- Set `max_plot_points` parameter for memory control
- Enable `use_resampler` flag in v4 runners
- Monitor memory usage with large multi-year datasets

### Common Issues
- **numpy 1.26.4**: Fixed version for bokeh compatibility 
- **TA-Lib Installation**: Requires precompiled binary on Windows
- **Memory Issues**: Use resampler for large datasets
- **Time Zone Handling**: All timestamps converted to timezone-naive for consistency

## Documentation References

Key documentation files:
- `docs/strategies/doji_ashi_strategy_v4_guide.md`: Complete v4 strategy guide
- `docs/development-workflow.md`: Command-line operations and Git workflow
- `docs/pine-script-standards.md`: Pine Script coding standards
- `docs/backtrader-quickstart.md`: Framework quick start
- `docs/BACKTRADER_RETURNS_FIX.md`: Technical issue resolution