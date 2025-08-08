# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a comprehensive trading algorithm development project featuring Pine Script indicators for TradingView and Python backtesting frameworks. The codebase contains technical analysis tools, trading strategies, and supporting documentation for quantitative trading development.

### Key Components

- **Pine Script Development**: Complete library of technical indicators and strategies for TradingView
- **Python Backtesting**: Backtrader framework for strategy backtesting
- **Interactive Visualization**: A new Plotly-based module (`viz/plotly_bt.py`) for creating interactive charts from CSV data, with an example script in `examples/`.
- **Virtual Environment**: Isolated Python environment (`venv/`) for dependency management
- **Documentation System**: Comprehensive guides for development workflows and standards
- **Context Management**: Automated conversation management for efficient development sessions

## Code Architecture

### Directory Structure

#### Pine Script Components
- `indicators/` - All indicator files organized by type
  - `trend/` - Trend-following indicators (EMA, KCB, GRaB systems)
  - `oscillator/` - Oscillator-based indicators (RSI, SQZMOM, WaveTrend)
  - `structure/` - Market structure and divergence indicators
  - `volume/` - Volume analysis indicators
  - `ml/` - Machine learning enhanced indicators
  - `risk/` - Risk management and stop-loss tools
- `strategies/` - Complete trading strategies organized by approach
  - `trend/` - Trend-following strategies
  - `oscillator/` - Oscillator-based strategies
  - `reversal/` - Reversal pattern strategies
- `utils/` - Utility functions and helper scripts
- `docs/` - Documentation and coding standards
- `requirements.txt` - Python dependencies for backtesting frameworks

#### Python Backtesting Components
- `backtests/` - Backtrader backtesting framework
  - `src/` - Source code files (backtest_engine.py, bt_configurable.py, bt_simple.py, etc.)
  - `config/` - Configuration files for strategies and broker settings
  - `data/` - Historical data files (CSV format)
  - `README.md` - Complete usage guide with virtual environment instructions
- `venv/` - Virtual environment for isolated Python development
- `requirements.txt` - Python dependencies including backtrader, pandas, numpy
- `requirements-local.txt` - For local-only dependencies (e.g., custom TA-Lib builds).

#### Visualization & Examples
- `viz/` - Visualization modules, including `plotly_bt.py`.
- `examples/` - Example scripts like `run_csv_and_plot.py`.
- `reports/` - Default output directory for plots.

#### Documentation & Templates
- `docs/` - Comprehensive documentation
  - `README.md` - Main documentation index and quick start guide
  - `pine-script-standards.md` - Complete Pine Script v5 Golden Rulebook V1.1
  - `development-workflow.md` - Development workflow and command operations
  - `python-frameworks-guide.md` - Python backtesting frameworks guide
  - `strategy-conversion-guide.md` - Pine Script to Python conversion guide
  - `context-management-guide.md` - Context management and optimization guide
  - `templates/` - Reusable code templates
    - `kelly-criterion.pine` - Kelly criterion statistics implementation
    - `strategy-config.pine` - Standard strategy configuration template

## Key Development Patterns

### Pine Script Development
- **Standards**: Follow `docs/pine-script-standards.md` for complete Pine Script v5 Golden Rulebook V1.1
- **Kelly Criterion**: Use `docs/templates/kelly-criterion.pine` template for adding Kelly statistics
- **Strategy Config**: Use `docs/templates/strategy-config.pine` for standardized backtest settings
- **File Organization**: Follow naming conventions in `docs/development-workflow.md`

### Python Backtesting (Active Implementation)

- **Standard Imports (VENV-aware rule)**: All Python strategy files (`backtester/backtests/strategies/*.py`) must begin with the following import template. Core imports reflect the current virtual environment. Optional packages are guarded with try/except to avoid runtime failures if not present.

  ```python
  # --- Standard Library ---
  import datetime
  from typing import Optional

  # --- Core Scientific ---
  import numpy as np
  import pandas as pd

  # Optional scientific (guarded)
  try:
      from scipy import stats  # noqa: F401
  except Exception:
      stats = None

  # --- Backtesting ---
  import backtrader as bt

  # TA-Lib (installed in venv) and Backtrader-TALIB bridge
  try:
      import talib  # noqa: F401
      HAS_TALIB = True
  except Exception:
      talib = None
      HAS_TALIB = False

  # pandas_ta: optional
  try:
      import pandas_ta as ta  # noqa: F401
      HAS_PANDAS_TA = True
  except Exception:
      ta = None
      HAS_PANDAS_TA = False

  # --- Data & HTTP ---
  import requests  # installed in venv
  try:
      import yfinance as yf  # noqa: F401
      HAS_YFINANCE = True
  except Exception:
      yf = None
      HAS_YFINANCE = False

  # --- Visualization ---
  import matplotlib.pyplot as plt
  try:
      import seaborn as sns  # noqa: F401
      HAS_SEABORN = True
  except Exception:
      sns = None
      HAS_SEABORN = False
  try:
      import plotly.graph_objects as go  # noqa: F401
      HAS_PLOTLY = True
  except Exception:
      go = None
      HAS_PLOTLY = False

  # --- Performance & Utilities (optional) ---
  try:
      from numba import jit  # noqa: F401
      HAS_NUMBA = True
  except Exception:
      jit = None
      HAS_NUMBA = False
  try:
      from loguru import logger  # noqa: F401
      HAS_LOGURU = True
  except Exception:
      logger = None
      HAS_LOGURU = False
  ```

- **Usage Guidance**:
  - Prefer TA-Lib indicators when `HAS_TALIB` is True; otherwise gracefully fallback to Backtrader indicators.
  - Keep optional dependencies behind capability flags (e.g., `HAS_PANDAS_TA`, `HAS_YFINANCE`).
  - Do not hard-crash on missing optional libs; degrade features instead.

- **Backtrader Framework**: Complete backtesting system in `backtests/` with multiple strategies and configuration options
- **Virtual Environment**: Use `venv/` for isolated Python development with all dependencies installed
- **Dependencies**: Complete Python environment defined in `requirements.txt`
- **Strategy Conversion**: Pine Script logic can be adapted to Python/pandas paradigms for backtesting

### Virtual Environment Usage
- **Activation**: `D:\BIGBOSS\claudecode\venv\Scripts\activate` (Windows) or `source D:\BIGBOSS\claudecode/venv/bin/activate` (Linux/macOS)
- **Running Backtests**: Use virtual environment Python interpreter for all backtesting scripts
- **Dependency Management**: All required packages (backtrader, pandas, numpy) are pre-installed in the virtual environment
- **Isolation**: Prevents conflicts with system Python packages and other projects

### Development Workflow
- **Process**: Follow the complete development workflow in `docs/development-workflow.md`
- **File Operations**: Use standardized command-line operations and file naming
- **Documentation**: Maintain proper documentation standards for all files
- **Testing**: Validate all changes against framework standards

## Sub-Agent Usage Guidelines

### When to Use Sub-Agents

#### Pine Script Development
- **Creating/Modifying Indicators**: Use `docs/pine-script-standards.md` for coding standards
- **Adding Kelly Statistics**: Use `docs/templates/kelly-criterion.pine` template
- **Strategy Configuration**: Use `docs/templates/strategy-config.pine` template
- **File Organization**: Refer to `docs/development-workflow.md` for naming conventions
- **Strategy Conversion**: Use `docs/strategy-conversion.md` for Pine → Python automation

#### Python Development (Optional Future Implementation)
- **Framework Integration**: Python backtesting frameworks can be independently installed and integrated as needed
- **Environment Setup**: Use virtual environments and proper dependency management when adding Python frameworks
- **Strategy Conversion**: Pine Script logic can be adapted to Python/pandas paradigms for backtesting

#### General Development
- **Command Line Operations**: Use `docs/development-workflow.md` for file operations
- **Documentation Standards**: Follow documentation guidelines for all files
- **Git Workflow**: Use proper commit standards and branch management
- **Virtual Environment**: Always use `claudecode\venv` for Python development and backtesting

### Sub-Agent Access Pattern

For specific tasks, Claude Code should:

1. **Check CLAUDE.md first** for high-level guidance
2. **Refer to appropriate sub-agent** for detailed implementation:
   - Pine Script standards → `docs/pine-script-standards.md`
   - Strategy conversion → `docs/strategy-conversion-guide.md`
   - Development workflow → `docs/development-workflow.md`
   - Python frameworks → `docs/python-frameworks-guide.md`
   - Context management → `docs/context-management-guide.md`
   - Code templates → `docs/templates/`
3. **Follow the documented patterns** while maintaining consistency across the codebase

### File Creation Priority

When creating new files:
1. **Check existing structure** first
2. **Use appropriate templates** when available
3. **Follow naming conventions** from development workflow
4. **Include proper documentation** as specified in standards

## Context Management

### Automated Context Monitoring
Claude Code includes automated context management through the context management system (`docs/context-management-guide.md`). This system:

- **Monitors conversation length** and provides compact recommendations
- **Tracks context usage patterns** and performance indicators
- **Suggests optimal timing** for context cleanup
- **Provides focused compact commands** for task switching

### Context Management Commands
- **`/context-check`**: Analyze current conversation and provide compact recommendations
- **`/context-stats`**: Show statistics about current context usage
- **`/compact-help`**: Get help with context management best practices

### When to Use Context Management
- **After 15+ messages** in a single conversation
- **When switching between major tasks** (e.g., from git operations to coding)
- **When response times increase** noticeably
- **Before starting new complex tasks**

### Compact Best Practices
- **Use focused compacts**: `/compact focus on [current_task]`
- **Compact at task boundaries**: Clean context when finishing major work
- **Monitor performance**: Watch for degraded response quality
- **Regular maintenance**: Compact periodically during long development sessions

## Recent Changes

### Backtesting Setup and Data Preprocessing Enhancements

This update details the improvements made to the backtesting setup, focusing on data handling, dependency compatibility, and plotting.

*   **Automated Bokeh Plotting**:
    *   Modified `backtester/backtests/strategies/dojo1_v2.py` to automatically use `Bokeh` for plotting when `cerebro.plot()` is called without an explicit `plotter` argument.
*   **Dual Data Feed Support**:
    *   Enhanced `backtester/backtests/strategies/dojo1_v2.py` to accept two distinct data feeds (`--main_data` for primary OHLCV and `--daily_data` for daily trend filtering) via command-line arguments.
*   **Dependency Compatibility Fixes**:
    *   **`numpy` and `bokeh`**: Resolved `AttributeError: module 'numpy' has no attribute 'bool8'` and `AttributeError: module 'numpy' has no attribute 'object'` by:
        *   Downgrading `numpy` to `1.26.4` in `requirements.txt`.
        *   Temporarily patching `backtester/venv/Lib/site-packages/backtrader_plotting/bokeh/figure.py` to replace `np.object` with `object` (Note: This is a temporary fix and will be overwritten upon reinstallation of `backtrader_plotting`).
    *   **`backtrader_plotting` Module**: Added `backtrader_plotting==2.0.0` to `requirements.txt` to ensure its proper installation.
*   **Robust Timestamp Handling (Data Preprocessing)**:
    *   Addressed `ValueError: time data '...' does not match format '%Y-%m-%d %H:%M:%S'` by:
        *   Creating `preprocess_data.py` to convert毫秒级 Unix 时间戳 to `YYYY-MM-DD HH:MM:SS` format.
        *   Integrated `preprocess_data.py` into `dojo1_v2.py` to automatically preprocess data files before loading them into `backtrader`. This ensures consistent date/time formatting.
    *   Modified `preprocess_data.py` to use `errors='coerce'` during `pd.to_datetime` conversion to handle any invalid timestamps gracefully.

These changes significantly improve the stability and usability of the backtesting environment, especially when dealing with various data sources and plotting requirements.
