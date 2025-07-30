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

## Pine Script Standards
All code follows the **PineScript v5 Golden Rulebook V1.1**:

### Foundational Principles

#### Code Structure & Naming Conventions
- **Variable Prefixes**: Use type indicators
  - `float_`: Floating-point numbers
  - `int_`: Integers
  - `bool_`: Booleans
  - `string_`: Strings
  - `color_`: Colors

- **Naming Style**: 
  - Use camelCase for variables and functions
  - Names must indicate purpose and type
  - **Scope**: The `type_` prefix rule applies **only to variables**. Functions should be named using simple camelCase (e.g., `calculateEma`) and declared using the `name(params) => returnType` syntax
- **Declaration Style**: `strategy()` and `indicator()` declarations must be single-line statements. Multi-line declarations will cause compilation errors

#### Type Safety & Performance

##### Function Guidelines
- Limit functions to 3-5 parameters
- Use single-line function declarations
- Always use `=>` on the same line as function declaration
- Return types must be explicitly declared

##### Input Validation
```pinescript
// Validate inputs to prevent errors
bool validateInput(float input) => 
    not na(input) and 
    input != float.POSITIVE_INFINITY and 
    input != float.NEGATIVE_INFINITY and 
    math.abs(input) < 1000000
```

##### Optimization Techniques
- Cache expensive calculations
- Use efficient conditionals
- Avoid redundant operations
- Minimize `request.security` calls
- **Compiler Compatibility First**: Prioritize robust, warning-free code over micro-optimizations. For instance, avoid hoisting `ta.*` function calls out of loops, as this can trigger compiler warnings about data inconsistency

#### Best Practices

##### Conditional Statements
**Correct:**
```pinescript
float value = condition ? trueValue : falseValue
```
**Incorrect:**
```pinescript
// No multi-line conditionals with backslashes or colons
float value = condition ?
    trueValue :
    falseValue
```

##### Variable Declaration
- Use `const` for truly constant values
- Use `var` for series values needing persistence

##### Plotting & Visualization
- Use color transparency for overlays
- Avoid duplicate plot operations
- Optimize drawing operations

#### Error Prevention

##### Prevent Common Pitfalls
- Explicit type casting
- Zero tolerance for implicit conversions
- Implement validation guards
- **Global Function Scope**: Functions **must** be defined in the global scope, not inside conditional (`if`) or loop (`for`) blocks. Placing a function definition inside a block will cause a misleading `Syntax error at input '=>'` error.

  **Incorrect:**
  ```pinescript
  // This will fail because the function is defined inside the 'if' block.
  if (bool_showStats)
      // ERROR: Defining a function here is not allowed.
      arrayVariance(src) =>
          // ... function body ...
          result
  ```

  **Correct:**
  ```pinescript
  // Define the function in the global scope (outside any blocks).
  arrayVariance(src) =>
      // ... function body ...
      result

  // Call the function from within the 'if' block.
  if (bool_showStats)
      float variance = arrayVariance(myArray)
  ```

##### Safe Division Methods
```pinescript
float safeDivide(float num, float denom, float defaultValue) => 
    denom != 0.0 ? num / denom : defaultValue
```

#### Advanced Techniques

##### Dynamic Calculations
- Adaptive parameter calculation
- Normalized volatility measurements
- Trend strength detection

#### Key Takeaways
1. Always declare types explicitly
2. Prioritize performance and readability
3. Use single-line function and conditional syntax
4. Implement robust input validation
5. Optimize memory and computation usage

## Key Development Patterns

### Strategy Backtest Settings
Strategies use standardized backtest configuration:
```pinescript
strategy(
    title               = "Strategy Name",
    initial_capital     = 500,
    default_qty_type    = strategy.percent_of_equity,
    default_qty_value   = 20,
    margin_long         = 25,
    margin_short        = 25,
    commission_type     = strategy.commission.percent,
    commission_value    = 0.02
)
```

### Kelly Criterion Integration

When asked to add Kelly criterion statistics to a Pine Script V5 strategy, append the following logic to the end of the script. This module calculates and displays key performance indicators based on the strategy's trade history.

#### Guidelines
- **Compliance**: All naming and style must strictly follow the PineScript v5 Golden Rulebook V1.1
- **Data Type Awareness (Series vs. Array)**: Crucially, understand that `ta.*` functions (e.g., `ta.variance`) work on **series** data (a value for each bar), not **arrays**. The Kelly module collects trade data into an `array`. Therefore, you **must** use custom functions for statistical calculations on this array, as shown in the implementation block
- **Isolation**: New code must not interfere with existing trading logic
- **Position**: All new code must be placed at the end of the script, separated by the comment `//––– Kelly Stats –––`

#### Implementation Code Block

Use this code block to implement the functionality. It is fully compatible with PineScript v5:

```pinescript
//––– Kelly Stats –––
// This code block calculates and displays Kelly criterion statistics.
// It runs only on the last bar to collect data from all closed trades.

// Function to calculate the sample variance of a float array.
arrayVariance(src) =>
    float float_mean = array.avg(src)
    float float_sumOfSquares = 0.0
    for i = 0 to array.size(src) - 1
        float_sumOfSquares += math.pow(array.get(src, i) - float_mean, 2)
    int int_n = array.size(src)
    float result = int_n > 1 ? float_sumOfSquares / (int_n - 1) : 0.0
    result

// 1. Declare a global array to store the return of each trade.
//    Use the 'var' keyword to ensure the array persists across bars.
var array<float> array_float_tradeReturns = array.new_float()

// 2. Main logic block, executed only on the last historical bar.
if barstate.islast
    // Populate the array from all closed trades.
    if strategy.closedtrades > 0 and array.size(array_float_tradeReturns) == 0
        for i = 0 to strategy.closedtrades - 1
            // Calculate the initial capital of the trade for v5.
            float float_entryVal = strategy.closedtrades.entry_price(i) * strategy.closedtrades.size(i)
            // Avoid division by zero error if capital is not zero.
            if float_entryVal != 0
                // Calculate the percentage return of this trade.
                float float_tradeReturn = (strategy.closedtrades.profit(i) / float_entryVal) * 100
                // Store the return in the global array.
                array.push(array_float_tradeReturns, float_tradeReturn)

    // 3. If there is trade data, calculate Kelly criterion statistics.
    float float_meanReturn = na
    float float_varianceReturn = na
    float float_kellyFraction = na

    if array.size(array_float_tradeReturns) > 0
        // Calculate the average return (average profit percentage per trade).
        float_meanReturn := array.avg(array_float_tradeReturns)
        // Calculate the variance of returns (sample variance) using the custom function.
        float_varianceReturn := arrayVariance(array_float_tradeReturns)
        // Calculate the Kelly fraction, handling the case where variance is zero.
        if float_varianceReturn != 0
            float_kellyFraction := float_meanReturn / float_varianceReturn

    // 4. Display statistics in a table on the chart.
    //    The table is created only once and updated on the last bar.
    var table table_kellyStats = table.new(position.top_left, 2, 4, border_width = 1)
    if barstate.islast
        // Table header
        table.cell(table_kellyStats, 0, 0, "Metric", bgcolor = color.new(color.blue, 75))
        table.cell(table_kellyStats, 1, 0, "Value", bgcolor = color.new(color.blue, 75))
        
        // Average return
        table.cell(table_kellyStats, 0, 1, "Mean Return (%)")
        table.cell(table_kellyStats, 1, 1, str.tostring(float_meanReturn, "0.00"))
        
        // Return variance
        table.cell(table_kellyStats, 0, 2, "Return Variance")
        table.cell(table_kellyStats, 1, 2, str.tostring(float_varianceReturn, "0.00"))

        // Kelly fraction
        table.cell(table_kellyStats, 0, 3, "Kelly Fraction")
        table.cell(table_kellyStats, 1, 3, str.tostring(float_kellyFraction, "0.00"))
```

### Common Input Patterns
- Boolean inputs for toggling features: `bool_enable_filter = input.bool(true, "Filter Name")`
- Grouped inputs with `group=` parameter
- String selectors with `options=` for mode selection
- Tooltip hints for complex inputs

### Version Support
- Most scripts use `//@version=5`
- Some newer indicators use `//@version=6`
- Maintain compatibility with TradingView's latest features

## Code Quality Guidelines

### Error Prevention
- Use safe division: `denom != 0.0 ? num / denom : defaultValue`
- Validate inputs for infinity and NaN values
- Implement validation guards for edge cases
- **Global Function Scope**: Functions **must** be defined in the global scope, not inside conditional (`if`) or loop (`for`) blocks

### Function Design
- Limit to 3-5 parameters
- Single-line declarations with explicit return types
- Define functions in global scope only
- Always use `=>` on the same line as function declaration
- Return types must be explicitly declared

### Visualization
- Use color transparency for overlays
- Optimize drawing operations
- Avoid duplicate plot operations

## File Organization

### Naming Convention
- Use underscores instead of spaces and special characters
- Remove brackets, plus signs, and other special characters
- Indicators: `Category_Name.PINE` (e.g., `Squeeze_Momentum_LB.PINE`)
- Strategies: `Approach_Strategy.PINE` (e.g., `Simple_Reversal_Strategy.PINE`)
- Version numbers use underscores: `v2_5` instead of `v2.5`
- All files use `.PINE` extension for consistency

### Documentation
- Standardized summary modules at the beginning of each file
- Summary format: `// ⌘ SUMMARY:` followed by Type, Purpose, Key Inputs, Outputs, Functions, Logic
- Author and date headers
- Clear strategy descriptions
- Reference links to trading concepts
- Input parameter tooltips

## Development Workflow

### Pine Script Development
1. Creating/modifying `.pine` files
2. Testing in TradingView editor
3. Validating against the Golden Rulebook standards
4. Committing changes with descriptive messages

### Python Development
1. **Environment Setup**: Use virtual environments for each framework
   ```bash
   cd jesse && python -m venv jesse_env && source jesse_env/bin/activate  # or jesse_env\Scripts\activate on Windows
   cd vectorbt && python -m venv venv && source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```

2. **Dependency Management**: Install requirements from respective directories
   ```bash
   cd jesse && pip install -r requirements.txt
   cd vectorbt && pip install -r requirements.txt
   ```

3. **Data Management**: Fetch and prepare data using provided utilities
   ```bash
   cd jesse/data && python fetch_data.py
   cd vectorbt/data && python fetch_data.py
   ```

4. **Strategy Development**: Create and test strategies in respective framework directories
5. **Backtesting**: Run backtests using framework-specific commands
6. **Validation**: Compare results across frameworks and with Pine Script implementations

## Command Line Operations

### Directory Management
```bash
# Create directory structure
mkdir "path/to/directory"
mkdir "path/to/subdirectory"

# Remove directories and contents
rm -rf "path/to/directory"
```

### File Operations
```bash
# Copy files with new names
cp "source/file.pine" "destination/new_name.PINE"

# Remove individual files
rm "file/to/remove.pine"
```

### Windows Path Handling
- Use full paths with double quotes for paths containing spaces
- Example: `"C:\Users\fiver\Documents\augment-projects\KFC\indicators\trend"`
- Bash commands work on Windows when using proper path formatting

### Batch File Processing
When reorganizing large numbers of files:
1. Create new directory structure first
2. Copy files with systematic renaming
3. Verify file placement before removing originals
4. Update documentation to reflect new structure

### File Naming Conversions
- Replace spaces with underscores: `ST_GRaB XZ 4.0.PINE` → `ST_GRaB_XZ_4_0.PINE`
- Remove special characters: `[LazyBear]` → `LB`
- Version format: `v2.5` → `v2_5`
- Consistent extension: `.pine` → `.PINE`

### Clean, efficient, and predictable code is the ultimate goal! 🚀

## Python Backtesting Standards

### Framework Guidelines

#### Jesse Framework
- **Structure**: Follow Jesse's recommended directory structure
- **Routes**: Use `routes.py` for defining trading routes and timeframes
- **Strategies**: Inherit from `Strategy` class, implement `should_long`, `should_short`, `go_long`, `go_short`
- **Data**: Use Jesse's built-in data fetching or custom data utilities
- **Testing**: Use `jesse.trade()` for backtesting and `jesse.live()` for paper trading

#### VectorBT Framework
- **Structure**: Organize by strategy type and timeframe
- **Data**: Use pandas DataFrames with OHLCV format
- **Indicators**: Leverage VectorBT's built-in indicators or custom pandas-based implementations
- **Backtesting**: Use vectorbt.Portfolio for portfolio-level backtesting
- **Optimization**: Utilize VectorBT's parameter optimization capabilities

### Python Coding Standards

#### Code Quality
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Implement comprehensive error handling
- Add docstrings for all public functions and classes
- Use logging for debugging and monitoring

#### Data Management
- Store data in efficient formats (CSV, Parquet, HDF5)
- Implement data validation and cleaning
- Use caching for expensive computations
- Handle missing data appropriately

#### Performance Optimization
- Use vectorized operations with pandas/numpy
- Implement parallel processing for computationally intensive tasks
- Optimize memory usage for large datasets
- Use appropriate data types for numerical computations

### Strategy Development

#### Conversion from Pine Script to Python
- Adapt Pine Script logic to Python/pandas paradigms
- Implement equivalent technical indicators using pandas operations
- Handle timeframe conversions and resampling
- Maintain consistency in signal generation and trade execution logic

#### Testing and Validation
- Implement unit tests for individual components
- Use cross-validation for strategy robustness
- Compare results with original Pine Script implementations
- Document performance characteristics and limitations