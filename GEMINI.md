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
    Install Backtrader-specific dependencies:
    ```bash
    pip install -r backtester/requirements.txt
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

### Pine Script Usage
Pine Script files (`.PINE` extension) are designed for use on the TradingView platform. They are not compiled or run locally in the traditional sense. To use them:
1.  Open the desired `.PINE` file in a text editor.
2.  Copy the entire script content.
3.  Paste it into the Pine Editor on TradingView and save it as a new indicator or strategy.

## Development Conventions

### Pine Script Standards
All Pine Script development must adhere to the guidelines specified in `docs/pine-script-standards.md`. This includes:
-   **Naming Conventions**: Use type indicators (e.g., `float_`, `int_`) and camelCase.
-   **Code Structure**: Single-line `strategy()` and `indicator()` declarations, functions defined in global scope.
-   **Type Safety & Performance**: Explicit type casting, input validation, and optimization techniques.

### Python Development
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

### `Doji_Ashi_Strategy 2.6.PINE` Default Settings Update

The default input settings for `strategies/reversal/Doji_Ashi_Strategy 2.6.PINE` have been updated to streamline testing and provide a more focused baseline configuration.

**Summary of Changes:**

*   **General Filters:** Most boolean (true/false) filters have been disabled by default to allow for more targeted analysis.
    *   `Use Market Trend Filter (SPY/BTC)`: `false`
    *   `Use Relative Strength Filter`: `false`
    *   `Use Relative Volume Filter`: `false`
    *   `Use Trailing Stop`: `false`
    *   `Use Time-based Exit`: `false`
    *   All visualization options (`Show SL/TP Levels`, `Show VWAP Line`, etc.): `false`
*   **Core Logic Enabled:**
    *   `Use Daily Trend Filter (Above SMAs)`: Remains `true` as a core component of the strategy's logic.
    *   `Use Entry Trigger`: Set to `true` to enforce the 3/8 MA entry condition.
*   **Configuration Presets:**
    *   `Market Type Preset`: Defaulted to `"crypto"`.
    *   `Trade Direction`: Defaulted to `"long"`.
    *   `Trigger MA Type`: Defaulted to `"EMA"`.
    *   `3/8 MA Entry Mode`: Defaulted to `"Above/Below"`.

These changes establish a cleaner starting point for strategy analysis, focusing on the daily trend filter and the EMA-based entry trigger.


### Documentation System Overhaul

Updated and expanded documentation system:

- **Main Index**: `docs/README.md` with comprehensive documentation navigation
- **Development Workflow**: `docs/development-workflow.md` for command operations
- **Python Frameworks**: `docs/python-frameworks-guide.md` for VectorBT integration
- **Strategy Conversion**: `docs/strategy-conversion-guide.md` for Pine → Python conversion
- **Context Management**: `docs/context-management-guide.md` for conversation optimization

### Requirements Management

Added complete `requirements.txt` with all necessary Python dependencies:

- **Data Analysis**: pandas, numpy, pandas-ta
- **Visualization**: matplotlib, seaborn, plotly
- **Machine Learning**: scikit-learn, optional TensorFlow/PyTorch
- **Backtesting**: VectorBT (optional)
- **Performance**: numba, scipy for optimization