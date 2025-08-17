# GEMINI Project Guide

This document provides a comprehensive guide for interacting with the cryptocurrency trading strategy backtesting system. It outlines the project's architecture, development workflows, and key operational commands.

## Project Overview

This is a professional-grade system for developing, backtesting, and analyzing cryptocurrency trading strategies. The project's core is the **Four Swords Swing Strategy**, which is prototyped in Pine Script (for TradingView) and then translated to Python for rigorous backtesting using the **Backtrader** framework.

The system is designed with a modular architecture, emphasizing a clear pipeline from strategy conception in Pine Script to quantitative analysis in Python.

### Key Technologies

*   **Pine Script v5**: For initial strategy development and testing on TradingView.
*   **Python 3**: For advanced backtesting, data analysis, and automation.
*   **Backtrader**: The core framework for Python-based strategy backtesting.
*   **backtrader-plotting (Bokeh)**: For generating interactive and high-performance visualization charts.
*   **Pandas**: For data manipulation and analysis.
*   **GitHub Actions**: For CI/CD and automated workflows.

### Architecture

The project follows a well-defined development pipeline:

1.  **Strategy Prototyping**: Strategies are first developed and validated in Pine Script within the `pinescript/` directory.
2.  **Python Implementation**: The validated Pine Script logic is translated into a Python class within `backtester/strategies/`.
3.  **Backtesting**: The Python strategy is run against historical data using runner scripts located in the `backtester/` directory.
4.  **Analysis**: The performance is analyzed using the generated metrics and interactive Bokeh charts.

## Building and Running

### Environment Setup

All development and execution should be done within the provided Python virtual environment.

1.  **Activate Virtual Environment (Windows):**
    ```powershell
    backtester\venv\Scripts\activate
    ```

2.  **Install Dependencies:**
    The project uses a `requirements.txt` file to manage dependencies.
    ```bash
    pip install -r config/requirements.txt
    ```
    For high-performance technical analysis, it is recommended to install `TA-Lib`. Please refer to its documentation for platform-specific installation instructions.

### Running a Backtest

The primary backtesting script is `run_doji_ashi_strategy_v5.py`. It is highly configurable via command-line arguments.

**Recommended Command:**

```bash
python backtester/run_doji_ashi_strategy_v5.py --data backtester/data/ETHUSDT/2h/ETHUSDT-2h-merged.csv --market_type crypto --enable_backtrader_plot
```

This command runs the `DojiAshiStrategyV5` with ETH/USDT 2-hour data and generates an interactive Bokeh plot of the results.

### Downloading Market Data

The `scripts/download_data.py` script is used to fetch historical market data from Binance.

**Example Usage:**

```bash
# Download 4-hour BTC/USDT data and merge it into a single file
python scripts/download_data.py --symbol BTCUSDT --interval 4h --merge-csv
```

## Development Conventions

### Pine Script Standards

The project adheres to a strict set of Pine Script coding standards to ensure code quality, readability, and performance. All Pine Script development must follow the guidelines outlined in:
*   **[Pine Script Standards](./docs/standards/pine-script-standards.md)**

Key conventions include:
*   **Variable Naming**: Use of prefixes (e.g., `int_`, `float_`, `bool_`).
*   **Type Safety**: Explicit type casting and avoidance of `series` vs `simple` type conflicts.
*   **Syntax**: Single-line function declarations and ternary operators.
*   **Structure**: Standardized summary blocks at the top of each script.

### Python Code Style

*   **Imports**: Follow the standardized import structure outlined in `CLAUDE.md`, which prioritizes standard libraries, then scientific libraries, and finally project-specific modules.
*   **Dependency Management**: The code uses graceful degradation, with `HAS_*` flags to detect optional dependencies like `TA-Lib` and fall back to alternatives if they are not installed.
*   **Docstrings**: All modules, classes, and functions should have clear and concise docstrings.

### Git Workflow

*   **Branching**: Use feature branches for all new development.
*   **Commits**: Follow the conventional commit format.
*   **Pull Requests**: All changes should be submitted via pull requests for review.

## Key Files and Directories

*   `GEMINI.md`: This file. Your primary guide for interacting with the project.
*   `CLAUDE.md`: The primary project guide, containing detailed architecture and workflow information.
*   `README.md`: A high-level project overview.
*   `pinescript/`: Contains all Pine Script indicators and strategies.
    *   `pinescript/strategies/oscillator/Four_Swords_Swing_Strategy_v1_6_1_simplified.pine`: The latest simplified version of the main strategy.
*   `backtester/`: The Python backtesting system.
    *   `backtester/run_doji_ashi_strategy_v5.py`: The main entry point for running backtests.
    *   `backtester/strategies/`: Python implementations of the trading strategies.
*   `docs/`: Contains all project documentation.
    *   `docs/standards/pine-script-standards.md`: The rulebook for Pine Script development.
    *   `docs/workflows/development-workflow.md`: The guide for the end-to-end development process.
*   `config/requirements.txt`: The list of Python dependencies.
*   `.github/workflows/`: Contains GitHub Actions workflows for automation.
