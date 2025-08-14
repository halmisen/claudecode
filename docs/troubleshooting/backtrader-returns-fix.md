# Backtrader Returns Analyzer Issue - Solution Guide

## Problem Description

When running backtests with Backtrader, the built-in `Returns` analyzer may show incorrect values such as:
- `-inf` (negative infinity)
- Extremely large negative numbers (e.g., -673315.94%)
- Values that don't match the actual portfolio performance

## Root Cause

This issue occurs because:
1. **Multiple Position Handling**: Backtrader's returns analyzer can get confused when managing multiple positions simultaneously
2. **Division by Zero**: The analyzer may attempt calculations that result in division by zero
3. **Negative Portfolio Values**: In certain scenarios, intermediate calculations may produce negative values
4. **Bracket Order Complexity**: When using SL/TP bracket orders, the analyzer may track positions incorrectly

## Solution

### 1. Manual Return Calculation (Recommended)

Always calculate returns manually using the broker's final value:

```python
initial_value = 100000.0
final_value = cerebro.broker.getvalue()
actual_return = (final_value - initial_value) / initial_value
print(f'Actual Return: {actual_return*100:.2f}%')
```

### 2. Custom Returns Analyzer

For more detailed analysis, create a custom analyzer:

```python
class CustomReturnsAnalyzer(bt.Analyzer):
    def __init__(self):
        self.start_value = None
        self.end_value = None
        
    def start(self):
        self.start_value = self.strategy.broker.getvalue()
        
    def get_analysis(self):
        if self.start_value and self.start_value != 0:
            end_value = self.strategy.broker.getvalue()
            total_return = (end_value - self.start_value) / self.start_value
            return {
                'start_value': self.start_value,
                'end_value': end_value,
                'total_return': total_return,
                'total_return_pct': total_return * 100
            }
        return {'error': 'Invalid start value'}
```

### 3. Verification Method

To verify your returns calculation:

1. Check initial vs final portfolio values
2. Verify with TradeAnalyzer's PnL
3. Cross-reference with individual trade logs

## Example Implementation

See `run_dojo_4h_with_fix.py` for a complete implementation that:
- Uses manual return calculation
- Includes a custom analyzer for comparison
- Shows both correct and incorrect analyzer outputs
- Generates proper plots with accurate return values

## Best Practices

1. **Always verify** Returns analyzer output against manual calculation
2. **Use bracket orders** carefully - they can confuse analyzers
3. **Log portfolio values** at key points to track performance
4. **Use multiple analyzers** to cross-validate results
5. **Consider position sizing** - large positions can cause calculation errors

## Common Scenarios That Cause Issues

1. **Multiple simultaneous positions**
2. **Partial position closes**
3. **SL/TP orders with different sizes**
4. **High-frequency trading strategies**
5. **Strategies with complex entry/exit logic**

## Alternative Metrics

When Returns analyzer fails, use these metrics instead:
- Total PnL from TradeAnalyzer
- Final portfolio value
- Win rate and average win/loss ratios
- Sharpe ratio (if calculated properly)
- Maximum drawdown

## Conclusion

The Backtrader Returns analyzer bug is a known issue. Always rely on manual calculation of `(final_value - initial_value) / initial_value` for accurate return percentages. The other analyzers (DrawDown, TradeAnalyzer, SharpeRatio) generally work correctly and can be used alongside manual return calculation.
