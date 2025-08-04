# 策略转换指南
# Pine Script策略到Python实现的转换方法

## 目的
本指南提供将Pine Script策略转换为Python实现的方法，支持Jesse和VectorBT框架，确保在所有三个平台间保持一致性。

## Conversion Workflow

### 1. Pine Script Analysis
- Parse Pine Script strategy logic and indicators
- Extract entry/exit conditions and parameters
- Identify technical indicators and their calculations
- Document signal generation rules

### 2. Framework-Specific Conversion
- **Jesse Conversion**: Generate class-based strategy implementation
- **VectorBT Conversion**: Generate vectorized function-based implementation
- Maintain identical signal logic across both frameworks

### 3. Consistency Validation
- Verify signal consistency between Pine Script and Python implementations
- Test parameter compatibility and edge cases
- Ensure timeframe and data handling consistency

## Conversion Templates

### Jesse Strategy Template
```python
# Jesse Strategy Template
import jesse.strategies as Strategy
from jesse import utils

class ConvertedStrategy(Strategy):
    def __init__(self):
        super().__init__()
        # Parameters from Pine Script
        self.param1 = 14
        self.param2 = 3
        
    def should_long(self) -> bool:
        # Long entry conditions converted from Pine Script
        return self.long_condition()
    
    def should_short(self) -> bool:
        # Short entry conditions converted from Pine Script
        return self.short_condition()
    
    def should_cancel(self) -> bool:
        # Exit conditions converted from Pine Script
        return self.exit_condition()
    
    def go_long(self):
        # Entry logic
        entry_price = self.price
        qty = self.capital * 0.1 / entry_price
        self.buy = qty, entry_price
    
    def go_short(self):
        # Entry logic
        entry_price = self.price
        qty = self.capital * 0.1 / entry_price
        self.sell = qty, entry_price
    
    def update_position(self):
        # Position management
        if self.should_cancel():
            self.liquidate()
    
    # Technical indicator methods (converted from Pine Script)
    def calculate_indicator(self):
        # Converted indicator calculations
        pass
    
    def long_condition(self):
        # Converted long entry logic
        pass
    
    def short_condition(self):
        # Converted short entry logic
        pass
    
    def exit_condition(self):
        # Converted exit logic
        pass
```

### VectorBT Strategy Template
```python
# VectorBT Strategy Template
import numpy as np
import pandas as pd
import vectorbt as vbt

def convert_pine_to_vectorbt(data, params):
    """
    Convert Pine Script strategy to VectorBT implementation
    
    Parameters:
    - data: OHLCV DataFrame
    - params: Strategy parameters from Pine Script
    
    Returns:
    - entries: Entry signals
    - exits: Exit signals
    """
    
    # Calculate indicators (converted from Pine Script)
    indicator1 = calculate_indicator_vectorbt(data, params)
    
    # Generate entry signals (converted from Pine Script logic)
    long_entries = generate_long_entries(data, indicator1, params)
    short_entries = generate_short_entries(data, indicator1, params)
    
    # Generate exit signals
    long_exits = generate_long_exits(data, indicator1, params)
    short_exits = generate_short_exits(data, indicator1, params)
    
    return long_entries, short_entries, long_exits, short_exits

def calculate_indicator_vectorbt(data, params):
    """Convert Pine Script indicator calculations to VectorBT"""
    # Vectorized implementation of Pine Script indicators
    pass

def generate_long_entries(data, indicator, params):
    """Convert Pine Script long entry conditions"""
    # Vectorized long entry logic
    pass

def generate_short_entries(data, indicator, params):
    """Convert Pine Script short entry conditions"""
    # Vectorized short entry logic
    pass

def generate_long_exits(data, indicator, params):
    """Convert Pine Script long exit conditions"""
    # Vectorized long exit logic
    pass

def generate_short_exits(data, indicator, params):
    """Convert Pine Script short exit conditions"""
    # Vectorized short exit logic
    pass
```

## Conversion Rules

### Pine Script to Python Mapping
- `ta.rsi()` → `pandas_ta.rsi()` or custom calculation
- `ta.macd()` → `pandas_ta.macd()` or custom calculation
- `strategy.entry()` → Jesse: `self.buy`/`self.sell`, VectorBT: signal arrays
- `strategy.close()` → Jesse: `self.liquidate()`, VectorBT: exit signals
- `plot()` → matplotlib/seaborn visualization

### Data Structure Conversion
- Pine Script `close` → Python `data['close']`
- Pine Script `high` → Python `data['high']`
- Pine Script `low` → Python `data['low']`
- Pine Script `volume` → Python `data['volume']`

### Signal Logic Conversion
- Pine Script `if condition → strategy.entry()` → Python conditional signal generation
- Pine Script `cross()` → Python `crossover()` functions
- Pine Script `valuewhen()` → Python lookup functions

## Consistency Validation

### Signal Comparison Tests
```python
def validate_signals(pine_signals, jesse_signals, vectorbt_signals):
    """
    Validate that signals are consistent across all frameworks
    """
    # Compare signal timing and direction
    pine_vs_jesse = compare_signals(pine_signals, jesse_signals)
    pine_vs_vectorbt = compare_signals(pine_signals, vectorbt_signals)
    
    # Calculate consistency metrics
    consistency_score = calculate_consistency(pine_vs_jesse, pine_vs_vectorbt)
    
    return consistency_score >= 0.95  # 95% consistency threshold
```

### Parameter Validation
```python
def validate_parameters(pine_params, python_params):
    """
    Validate that parameters are correctly mapped between frameworks
    """
    # Check parameter ranges and types
    # Validate parameter compatibility
    pass
```

## Usage Instructions

### For Main Claude Code
When converting a Pine Script strategy:

1. **Analyze Pine Script**: Read and understand the strategy logic
2. **Extract Parameters**: Identify all strategy parameters and their ranges
3. **Convert Indicators**: Transform Pine Script indicators to Python equivalents
4. **Generate Jesse Strategy**: Create class-based Jesse implementation
5. **Generate VectorBT Strategy**: Create vectorized VectorBT implementation
6. **Validate Consistency**: Test that all three implementations produce identical signals

### Command Reference
- **`/convert-strategy [filename]`**: Convert specific Pine Script strategy
- **`/validate-conversion [strategy_name]`**: Validate conversion consistency
- **`/conversion-report [strategy_name]`**: Generate conversion validation report

## Error Handling

### Common Conversion Issues
- **Indicator Availability**: Some Pine Script indicators may not have direct Python equivalents
- **Timeframe Handling**: Different timeframe handling between frameworks
- **Lookback Periods**: Different lookback period calculations
- **Floating Point Precision**: Numerical precision differences between platforms

### Error Resolution
- **Indicator Fallback**: Use custom implementations when direct equivalents don't exist
- **Parameter Tuning**: Adjust parameters to account for framework differences
- **Signal Filtering**: Apply additional filtering to ensure signal consistency
- **Validation Logging**: Detailed logging for debugging conversion issues

## Integration with Existing Infrastructure

### Dependencies
- **Pine Script Standards**: Follow `docs/pine-script-standards.md`
- **Python Frameworks**: Use `docs/python-frameworks-guide.md`
- **Development Workflow**: Follow `docs/development-workflow.md`
- **Validation Utilities**: Use `utils/validation/` tools

### File Organization
- **Jesse Strategies**: Store in `jesse/strategies/`
- **VectorBT Strategies**: Store in `vectorbt/strategies/`
- **Validation Reports**: Store in `validation/reports/`
- **Conversion Logs**: Store in `conversion/logs/`

## Best Practices

### Conversion Quality
- **Maintain Original Logic**: Don't optimize or change strategy logic during conversion
- **Parameter Preservation**: Keep all original parameters and their ranges
- **Signal Accuracy**: Ensure entry/exit timing is identical across frameworks
- **Error Handling**: Add framework-specific error handling without changing core logic

### Documentation
- **Document Conversion Changes**: Keep detailed logs of all conversion decisions
- **Parameter Mapping**: Document how Pine Script parameters map to Python parameters
- **Indicator Equivalents**: Document which Python indicators correspond to Pine Script indicators
- **Validation Results**: Include validation reports with converted strategies

### Testing
- **Unit Testing**: Test individual indicator conversions
- **Integration Testing**: Test complete strategy conversions
- **Cross-Platform Testing**: Test across all three frameworks
- **Performance Testing**: Ensure converted strategies perform efficiently