# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a comprehensive trading algorithm development project featuring both Pine Script indicators for TradingView and Python backtesting frameworks. The codebase contains technical analysis tools, trading strategies, and complete backtesting environments using Jesse and VectorBT frameworks.

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

#### Python Backtesting Frameworks
- `jesse/` - Jesse trading framework setup
  - `strategies/` - Strategy implementations for Jesse
  - `indicators/` - Technical indicators in Python
  - `data/` - Data fetching and processing utilities
  - `utils/` - Helper functions and tools
  - `requirements.txt` - Python dependencies
- `vectorbt/` - VectorBT backtesting framework setup
  - `strategies/` - Strategy implementations for VectorBT
  - `indicators/` - Technical indicators in Python
  - `data/` - Data fetching and processing utilities
  - `utils/` - Helper functions and tools
  - `requirements.txt` - Python dependencies

#### Documentation & Templates
- `docs/` - Comprehensive documentation
  - `pine-script-standards.md` - Complete Pine Script v5 Golden Rulebook V1.1
  - `python-frameworks-guide.md` - Python backtesting frameworks guide
  - `development-workflow.md` - Development workflow and command operations
  - `templates/` - Reusable code templates
    - `kelly-criterion.pine` - Kelly criterion statistics implementation
    - `strategy-config.pine` - Standard strategy configuration template

## Key Development Patterns

### Pine Script Development
- **Standards**: Follow `docs/pine-script-standards.md` for complete Pine Script v5 Golden Rulebook V1.1
- **Kelly Criterion**: Use `docs/templates/kelly-criterion.pine` template for adding Kelly statistics
- **Strategy Config**: Use `docs/templates/strategy-config.pine` for standardized backtest settings
- **File Organization**: Follow naming conventions in `docs/development-workflow.md`

### Python Backtesting
- **Frameworks**: Refer to `docs/python-frameworks-guide.md` for Jesse and VectorBT guidance
- **Environment Setup**: Use virtual environments and proper dependency management
- **Strategy Conversion**: Adapt Pine Script logic to Python/pandas paradigms
- **Testing**: Implement comprehensive validation against Pine Script implementations

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

#### Python Development
- **Framework Setup**: Use `docs/python-frameworks-guide.md` for environment setup
- **Strategy Implementation**: Follow framework-specific guidelines
- **Data Management**: Use provided utilities for data fetching and processing
- **Testing & Validation**: Implement comprehensive testing procedures

#### General Development
- **Command Line Operations**: Use `docs/development-workflow.md` for file operations
- **Documentation Standards**: Follow documentation guidelines for all files
- **Git Workflow**: Use proper commit standards and branch management

### Sub-Agent Access Pattern

For specific tasks, Claude Code should:

1. **Check CLAUDE.md first** for high-level guidance
2. **Refer to appropriate sub-agent** for detailed implementation:
   - Pine Script standards → `docs/pine-script-standards.md`
   - Python frameworks → `docs/python-frameworks-guide.md`
   - Development workflow → `docs/development-workflow.md`
   - Code templates → `docs/templates/`
3. **Follow the documented patterns** while maintaining consistency across the codebase

### File Creation Priority

When creating new files:
1. **Check existing structure** first
2. **Use appropriate templates** when available
3. **Follow naming conventions** from development workflow
4. **Include proper documentation** as specified in standards

