# Pine Script Standards

This document contains the complete Pine Script v5 Golden Rulebook V1.1 standards for trading algorithm development.

## Foundational Principles

### Code Structure & Naming Conventions

#### Variable Prefixes
Use type indicators for all variables:

- `float_`: Floating-point numbers
- `int_`: Integers  
- `bool_`: Booleans
- `string_`: Strings
- `color_`: Colors

#### Naming Style
- Use camelCase for variables and functions
- Names must indicate purpose and type
- **Scope**: The `type_` prefix rule applies **only to variables**. Functions should be named using simple camelCase (e.g., `calculateEma`) and declared using the `name(params) => returnType` syntax

#### Declaration Style
`strategy()` and `indicator()` declarations must be single-line statements. Multi-line declarations will cause compilation errors.

### Type Safety & Performance

#### Function Guidelines
- Limit functions to 3-5 parameters
- Use single-line function declarations
- Always use `=>` on the same line as function declaration
- Return types must be explicitly declared

#### Input Validation
```pinescript
// Validate inputs to prevent errors
bool validateInput(float input) => 
    not na(input) and 
    input != float.POSITIVE_INFINITY and 
    input != float.NEGATIVE_INFINITY and 
    math.abs(input) < 1000000
```

#### Optimization Techniques
- Cache expensive calculations
- Use efficient conditionals
- Avoid redundant operations
- Minimize `request.security` calls
- **Compiler Compatibility First**: Prioritize robust, warning-free code over micro-optimizations. For instance, avoid hoisting `ta.*` function calls out of loops, as this can trigger compiler warnings about data inconsistency

### Best Practices

#### Conditional Statements
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

#### Variable Declaration
- Use `const` for truly constant values
- Use `var` for series values needing persistence

#### Plotting & Visualization
- Use color transparency for overlays
- Avoid duplicate plot operations
- Optimize drawing operations

### Error Prevention

#### Prevent Common Pitfalls
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

#### Safe Division Methods
```pinescript
float safeDivide(float num, float denom, float defaultValue) => 
    denom != 0.0 ? num / denom : defaultValue
```

### Advanced Techniques

#### Dynamic Calculations
- Adaptive parameter calculation
- Normalized volatility measurements
- Trend strength detection

### Key Takeaways
1. Always declare types explicitly
2. Prioritize performance and readability
3. Use single-line function and conditional syntax
4. Implement robust input validation
5. Optimize memory and computation usage

### Common Input Patterns
- Boolean inputs for toggling features: `bool_enable_filter = input.bool(true, "Filter Name")`
- Grouped inputs with `group=` parameter
- String selectors with `options=` for mode selection
- Tooltip hints for complex inputs

### Version Support
- Most scripts use `//@version=5`
- Some newer indicators use `//@version=6`
- Maintain compatibility with TradingView's latest features

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

## Critical Pine Script v5 Syntax Issues & Solutions

### Series vs Simple Type Conflicts

#### The Problem
Pine Script v5 distinguishes between `simple` and `series` types. Built-in functions like `ta.ema()` require `simple int` parameters, but calculated values are often `series int`.

**Error Example:**
```pinescript
// This will fail with "series int was used but simple int is expected"
int_adaptiveLength = bool_condition ? 10 : 20
float_ema = ta.ema(close, int_adaptiveLength)  // ERROR!
```

**Solutions:**
1. **Use Fixed Parameters**: Avoid dynamic parameter calculation for TA functions
```pinescript
// ✅ Correct - Use original input directly
int_length = input.int(10, "Length")
float_ema = ta.ema(close, int_length)
```

2. **Alternative: Use Conditional Logic After Calculation**
```pinescript
// ✅ Correct - Calculate both, then choose
float_ema10 = ta.ema(close, 10)
float_ema20 = ta.ema(close, 20)
float_result = bool_condition ? float_ema10 : float_ema20
```

### Variable Declaration Requirements

#### Variable Scope and State Management
All variables must be properly declared before use, especially state variables.

**Required Pattern:**
```pinescript
// ✅ Correct - All state variables declared with var
var bool bool_waitLongExit = false
var bool bool_waitShortExit = false
var float float_stopPrice = na
var float float_entryPrice = na
var int int_barsInTrade = 0
```

#### Variable Naming with Confirmation Score
**Incorrect:**
```pinescript
confirmationScore += 30.0  // ERROR: Undeclared identifier
```

**Correct:**
```pinescript
float_confirmationScore = 0.0  // Declare first
if (condition)
    float_confirmationScore += 30.0  // Then modify
```

### Strategy Function Parameters

#### Strategy.entry() Correct Usage
**Incorrect:**
```pinescript
strategy.entry("Long", strategy.long, qty_percent=15.0)  // ERROR: No qty_percent parameter
```

**Correct Options:**
```pinescript
// Option 1: Use default_qty_type in strategy declaration
strategy(..., default_qty_type=strategy.percent_of_equity, default_qty_value=15)
strategy.entry("Long", strategy.long)

// Option 2: Use qty parameter with calculated size
float_dollarAmount = strategy.equity * 0.15
float_shares = float_dollarAmount / close
strategy.entry("Long", strategy.long, qty=float_shares)

// Option 3: Use qty parameter with percentage (Pine Script handles conversion)
strategy.entry("Long", strategy.long, qty=15.0)  // When default_qty_type is percent_of_equity
```

### Multi-line Statement Restrictions

#### Ternary Operators Must Be Single Line
**Incorrect:**
```pinescript
float_result = condition ?
    trueValue :
    falseValue  // ERROR: Multi-line not allowed
```

**Correct:**
```pinescript
float_result = condition ? trueValue : falseValue
```

#### Function Declarations Must Be Single Line
**Incorrect:**
```pinescript
calculateValue(param1, param2) =>
    result = param1 + param2
    result  // ERROR: Multi-line declaration
```

**Correct:**
```pinescript
calculateValue(param1, param2) => param1 + param2
```

### Best Practices for Complex Strategies

#### 1. Simplify Adaptive Parameters
Instead of dynamic parameter adjustment, use conditional logic:
```pinescript
// ✅ Recommended approach
float_ema_trending = ta.ema(close, 15)
float_ema_ranging = ta.ema(close, 25)
float_adaptive_ema = bool_trending ? float_ema_trending : float_ema_ranging
```

#### 2. Proper State Management Pattern
```pinescript
// ✅ Complete state management template
var bool bool_inLongTrade = false
var bool bool_inShortTrade = false
var float float_entryPrice = na
var float float_stopLoss = na
var int int_tradeDuration = 0

// State updates
if (entryCondition and strategy.position_size == 0)
    bool_inLongTrade := true
    float_entryPrice := close
    float_stopLoss := close * 0.98

if (exitCondition or strategy.position_size == 0)
    bool_inLongTrade := false
    float_entryPrice := na
    float_stopLoss := na
    int_tradeDuration := 0
```

#### 3. Variable Assignment vs Modification
```pinescript
// ✅ Correct initialization and modification
float_score = 0.0  // Initialize

// Then modify conditionally
if (condition1)
    float_score += 25.0
if (condition2)
    float_score += 15.0
```

### Testing and Validation Checklist

#### Pre-Compilation Checklist
- [ ] All variables declared before use
- [ ] No dynamic parameters for TA functions
- [ ] All ternary operators are single-line
- [ ] strategy.entry() uses correct parameters
- [ ] Variable names follow type prefix conventions
- [ ] State variables use `var` keyword
- [ ] No functions defined inside conditional blocks

#### Common Error Messages and Solutions
1. **"series int was used but simple int is expected"**
   - Solution: Use fixed input parameters for TA functions

2. **"Undeclared identifier"**
   - Solution: Declare all variables before use with proper type prefixes

3. **"The function does not have an argument with the name"**
   - Solution: Check Pine Script v5 documentation for correct parameter names

4. **"Syntax error at input 'end of line without line continuation'"**
   - Solution: Combine multi-line statements into single lines

### Performance Optimization Notes

#### Memory Efficiency
- Use `var` only for variables that need persistence across bars
- Avoid creating unnecessary series variables
- Cache expensive calculations when possible

#### Execution Efficiency
- Minimize conditional complexity in hot paths
- Use built-in functions instead of custom implementations when available
- Avoid redundant calculations within the same bar

## Version Compatibility Notes

### Pine Script v5 Specific Requirements
- Stricter type checking than v4
- Enhanced series/simple type distinction
- More restrictive multi-line syntax
- Improved error messages but stricter compilation

### Migration from v4 to v5
- Review all dynamic parameter usage
- Update strategy.entry() calls to remove deprecated parameters
- Ensure all variables are properly scoped and declared
- Test thoroughly as some functions behave differently

### Clean, efficient, and predictable code is the ultimate goal! 🚀