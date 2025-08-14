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

### Clean, efficient, and predictable code is the ultimate goal! 🚀