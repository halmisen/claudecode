# Python Backtesting Frameworks Guide

This document provides comprehensive guidance for Python backtesting using Jesse and VectorBT frameworks.

## Framework Guidelines

### Jesse Framework

#### Structure
- **Structure**: Follow Jesse's recommended directory structure
- **Routes**: Use `routes.py` for defining trading routes and timeframes
- **Strategies**: Inherit from `Strategy` class, implement `should_long`, `should_short`, `go_long`, `go_short`
- **Data**: Use Jesse's built-in data fetching or custom data utilities
- **Testing**: Use `jesse.trade()` for backtesting and `jesse.live()` for paper trading

#### Environment Setup
```bash
cd jesse && python -m venv jesse_env && source jesse_env/bin/activate  # or jesse_env\Scripts\activate on Windows
```

#### Dependency Management
```bash
cd jesse && pip install -r requirements.txt
```

#### Data Management
```bash
cd jesse/data && python fetch_data.py
```

### VectorBT Framework

#### Structure
- **Structure**: Organize by strategy type and timeframe
- **Data**: Use pandas DataFrames with OHLCV format
- **Indicators**: Leverage VectorBT's built-in indicators or custom pandas-based implementations
- **Backtesting**: Use vectorbt.Portfolio for portfolio-level backtesting
- **Optimization**: Utilize VectorBT's parameter optimization capabilities

#### Environment Setup
```bash
cd vectorbt && python -m venv venv && source venv/bin/activate  # or venv\Scripts\activate on Windows
```

#### Dependency Management
```bash
cd vectorbt && pip install -r requirements.txt
```

#### Data Management
```bash
cd vectorbt/data && python fetch_data.py
```

## Python Coding Standards

### Code Quality
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Implement comprehensive error handling
- Add docstrings for all public functions and classes
- Use logging for debugging and monitoring

### Data Management
- Store data in efficient formats (CSV, Parquet, HDF5)
- Implement data validation and cleaning
- Use caching for expensive computations
- Handle missing data appropriately

### Performance Optimization
- Use vectorized operations with pandas/numpy
- Implement parallel processing for computationally intensive tasks
- Optimize memory usage for large datasets
- Use appropriate data types for numerical computations

## Strategy Development

### Conversion from Pine Script to Python
- Adapt Pine Script logic to Python/pandas paradigms
- Implement equivalent technical indicators using pandas operations
- Handle timeframe conversions and resampling
- Maintain consistency in signal generation and trade execution logic

### Testing and Validation
- Implement unit tests for individual components
- Use cross-validation for strategy robustness
- Compare results with original Pine Script implementations
- Document performance characteristics and limitations

## Development Workflow

### Strategy Development Process
1. Create and test strategies in respective framework directories
2. Run backtests using framework-specific commands
3. Compare results across frameworks and with Pine Script implementations
4. Validate performance and optimize as needed

### Key Commands
```bash
# Jesse backtesting
jesse trade

# VectorBT backtesting
python backtest.py

# Run tests
pytest tests/
```

## Clean, efficient, and predictable code is the ultimate goal! 🚀