# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a comprehensive trading algorithm development project featuring Pine Script indicators for TradingView and Python backtesting frameworks. The codebase contains technical analysis tools, trading strategies, and supporting documentation for quantitative trading development.

### Key Components

- **Pine Script Development**: Complete library of technical indicators and strategies for TradingView
- **Python Backtesting**: Backtrader framework for strategy backtesting
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

### `Doji_Ashi_Strategy 2.6.PINE` Default Settings Update

The default input settings for `pinescript/strategies/reversal/Doji_Ashi_Strategy 2.6.PINE` have been updated to streamline testing and provide a more focused baseline configuration.

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
