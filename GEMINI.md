# Project Overview

This repository hosts a comprehensive trading algorithm development project, integrating Pine Script for TradingView indicators and strategies with Python for robust backtesting using the Backtrader framework. It's designed to facilitate the development, testing, and analysis of quantitative trading strategies.

## Key Components

### 📊 Pine Script Development
Located primarily in the `pinescript/` directory, this section contains a library of technical indicators and trading strategies designed for the TradingView platform.
-   `pinescript/indicators/`: Organized by type (trend, oscillator, structure, volume, ML, risk), containing various custom indicators.
-   `pinescript/strategies/`: Contains complete trading strategies categorized by their approach (trend, oscillator, reversal).

### 🐍 Python Backtesting
The `backtester/` directory houses the Python-based backtesting framework, utilizing Backtrader.
-   `backtester/backtests/strategies/`: Contains Python implementations of trading strategies, including `doji3.py` which is a conversion from Pine Script.
-   `backtester/backtests/data/`: Stores historical market data used for backtesting.
-   `backtester/requirements.txt`: Specifies Python dependencies for the backtesting environment.

### 📈 Interactive Visualization
-   `viz/`: Contains visualization modules, starting with `plotly_bt.py` for creating interactive charts from backtest results.
-   `examples/`: Includes example scripts, such as `run_csv_and_plot.py`, demonstrating how to use the visualization tools.
-   `reports/`: Default output directory for generated plots and reports.

### 📚 Documentation
The `docs/` directory provides extensive documentation covering various aspects of the project.
-   `docs/README.md`: The main index for all project documentation.
-   `docs/pine-script-standards.md`: Detailed coding standards and best practices for Pine Script.
-   `docs/backtrader-quickstart.md`: Guides for getting started with Backtrader.
-   `docs/strategy-conversion-guide.md`: Instructions and templates for converting Pine Script strategies to Python.
-   `docs/development-workflow.md`: Outlines the general development process, file operations, and Git workflow.

### 🛠️ Utilities
-   `download_data.py`: A Python script for downloading historical market data from Binance.
-   `requirements.txt`: Top-level Python dependencies for general project utilities and analysis.
-   `requirements-local.txt`: For local-only dependencies that should not be committed to version control (e.g., locally built wheels).

## Building and Running

### Python Environment Setup
This project uses Python and relies on virtual environments for dependency management.

1.  **Create and Activate Virtual Environment**:
    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On Linux/macOS:
    source venv/bin/activate
    ```

2.  **Install Dependencies**:
    Install the core project dependencies:
    ```bash
    pip install -r requirements.txt
    ```
    For special local dependencies (like a custom-built TA-Lib wheel):
    ```bash
    pip install -r requirements-local.txt
    ```

### Data Acquisition
Historical market data can be downloaded using the provided Python script:
```bash
python download_data.py
```
This script will download BTCUSDT data for 4-hour and 1-day intervals into `backtester/backtests/data/BTCUSDT/`.

### Running Backtests
Backtrader strategies are Python scripts that can be executed directly. For example, to run `doji3.py`:
```bash
python backtester/backtests/strategies/doji3.py
```
The `if __name__ == '__main__':` block within strategy files typically contains the setup for `cerebro` (Backtrader's engine) and initiates the backtest.

### Generating Interactive Plots
You can generate interactive Plotly charts from CSV files containing OHLCV data, and optionally include trade markers and equity curves.
```bash
# Basic plot from OHLCV data
python examples/run_csv_and_plot.py --csv path/to/your/ohlcv.csv --out reports/my_plot.html

# Plot with trades and equity curve
python examples/run_csv_and_plot.py --csv path/to/ohlcv.csv --trades path/to/trades.csv --equity path/to/equity.csv --out reports/full_backtest.html --title "My Strategy Backtest"
```

### Pine Script Usage
Pine Script files (`.pine` extension) are designed for use on the TradingView platform. They are not compiled or run locally in the traditional sense. To use them:
1.  Open the desired `.pine` file in a text editor.
2.  Copy the entire script content.
3.  Paste it into the Pine Editor on TradingView and save it as a new indicator or strategy.

## Development Conventions

### Pine Script Standards
All Pine Script development must adhere to the guidelines specified in `docs/pine-script-standards.md`. This includes:
-   **Naming Conventions**: Use type indicators (e.g., `float_`, `int_`) and camelCase.
-   **Code Structure**: Single-line `strategy()` and `indicator()` declarations, functions defined in global scope.
-   **Type Safety & Performance**: Explicit type casting, input validation, and optimization techniques.

-### Python Development
-   **Standard Imports (VENV-aware rule)**: All Python strategy files (`backtester/backtests/strategies/*.py`) must begin with the following import template. Core imports reflect the current virtual environment. Optional packages are guarded with try/except to avoid runtime failures if not present.

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
-   **Virtual Environments**: Always work within the activated `venv/` to manage dependencies.
-   **Backtrader Usage**: Refer to `docs/backtrader-quickstart.md` for core concepts and `docs/backtrader-parameter-reference.md` for detailed parameter usage.
-   **Strategy Conversion**: When converting Pine Script to Python, follow the guidelines in `docs/strategy-conversion-guide.md`.

### General Workflow
-   **File Operations**: Consult `docs/development-workflow.md` for standardized command-line operations and file naming conventions.
-   **Documentation**: Maintain proper documentation for all new and modified files.
-   **Git Workflow**: Follow standard Git practices for version control.

## Important Documentation

-   `CLAUDE.md`: Provides guidance for AI agents (like Claude Code) on working with this repository.
-   `docs/README.md`: The main entry point for all project documentation.
-   `docs/pine-script-standards.md`: Essential reading for Pine Script developers.
-   `docs/strategy-conversion-guide.md`: Crucial for translating Pine Script logic to Python.
-   `docs/development-workflow.md`: General guidelines for contributing to the project.
-   `requirements.txt` & `backtester/requirements.txt`: Define project dependencies.

## Sub-Agent Usage Guidelines

### When to Use Sub-Agents

#### Pine Script Development
- **Creating/Modifying Indicators**: Use `docs/pine-script-standards.md` for coding standards
- **Adding Kelly Statistics**: Use `docs/templates/kelly-criterion.pine` template
- **Strategy Configuration**: Use `docs/templates/strategy-config.pine` for standardized backtest settings
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
