# Pine Script v5 Quick Reference Card

## 🚨 Common Errors & Quick Fixes

### 1. Series vs Simple Type Error
```
❌ ERROR: "series int was used but simple int is expected"
```
**Quick Fix:**
```pinescript
// ❌ Wrong
int_adaptive = condition ? 10 : 20
float_ema = ta.ema(close, int_adaptive)

// ✅ Correct  
float_ema10 = ta.ema(close, 10)
float_ema20 = ta.ema(close, 20)
float_result = condition ? float_ema10 : float_ema20
```

### 2. Undeclared Variable Error
```
❌ ERROR: "Undeclared identifier 'variableName'"
```
**Quick Fix:**
```pinescript
// ❌ Wrong
confirmationScore += 30.0

// ✅ Correct
float_confirmationScore = 0.0
float_confirmationScore += 30.0
```

### 3. Strategy Entry Parameter Error
```
❌ ERROR: "function does not have argument 'qty_percent'"
```
**Quick Fix:**
```pinescript
// ❌ Wrong
strategy.entry("Long", strategy.long, qty_percent=15.0)

// ✅ Correct
strategy.entry("Long", strategy.long, qty=15.0)
// With: default_qty_type=strategy.percent_of_equity in strategy()
```

### 4. Multi-line Syntax Error
```
❌ ERROR: "Syntax error at input 'end of line'"
```
**Quick Fix:**
```pinescript
// ❌ Wrong
float_value = condition ? 
    trueValue : 
    falseValue

// ✅ Correct
float_value = condition ? trueValue : falseValue
```

## 📋 Essential Patterns

### Variable Declaration Template
```pinescript
// State variables
var bool bool_longEntry = false
var bool bool_shortEntry = false
var float float_stopPrice = na
var int int_barCount = 0

// Regular variables
float_confirmationScore = 0.0
bool_signalValid = false
int_length = input.int(20, "Length")
```

### Strategy Setup Template
```pinescript
strategy("Strategy Name", 
         shorttitle="Short", 
         overlay=true,
         initial_capital=500,
         default_qty_type=strategy.percent_of_equity,
         default_qty_value=15,
         commission_type=strategy.commission.percent,
         commission_value=0.02)
```

### Confirmation Score Pattern
```pinescript
float_score = 0.0
if (signal1)
    float_score += 30.0
if (signal2)  
    float_score += 25.0
if (signal3)
    float_score += 20.0

bool_highQuality = float_score >= 75.0
```

### TA Function Usage
```pinescript
// ✅ Always use input parameters directly
int_emaPeriod = input.int(20, "EMA Period")
float_ema = ta.ema(close, int_emaPeriod)

// ❌ Never use calculated series
// int_adaptive = condition ? 15 : 25  // series int
// float_ema = ta.ema(close, int_adaptive)  // ERROR!
```

### Entry/Exit Pattern
```pinescript
// Entry
if (bool_longSignal and strategy.position_size == 0)
    strategy.entry("Long", strategy.long, qty=float_positionSize)

// Exit  
if (bool_exitCondition and strategy.position_size > 0)
    strategy.close("Long", comment="Exit Reason")
```

## 🔍 Pre-Submit Checklist

**Before copying to TradingView:**

**Variables**
- [ ] All variables have type prefixes
- [ ] State variables use `var`
- [ ] No typos in variable names

**Functions**
- [ ] TA functions use input parameters only
- [ ] strategy.entry() uses correct parameters
- [ ] Single-line function declarations

**Syntax**
- [ ] Single-line ternary operators
- [ ] No multi-line statements
- [ ] Proper variable initialization

**Strategy**
- [ ] Correct strategy() declaration
- [ ] Valid position sizing approach
- [ ] Proper state management

## 🎯 Quick Debugging

### Step 1: Check Error Message
1. **"series int expected simple int"** → Fix TA function parameters
2. **"Undeclared identifier"** → Add variable declaration
3. **"function does not have argument"** → Check Pine Script v5 docs
4. **"Syntax error at input"** → Fix multi-line statements

### Step 2: Common Fixes
1. **Replace dynamic parameters** with fixed input values
2. **Add missing variable declarations** with type prefixes  
3. **Combine multi-line statements** into single lines
4. **Update function calls** to Pine Script v5 API

### Step 3: Validation
1. **Copy-paste to TradingView** Pine Editor
2. **Check for compiler errors**
3. **Verify strategy logic** works as expected
4. **Test alerts and visualization**

## 💡 Pro Tips

### Memory Optimization
- Only use `var` for variables that need persistence
- Avoid unnecessary series calculations
- Cache expensive computations

### Performance Tips
- Use built-in functions over custom logic
- Minimize conditional complexity
- Avoid redundant calculations

### Best Practices
- Always validate inputs with minval/maxval
- Add tooltips for complex parameters
- Use descriptive variable names
- Group related inputs

## 📖 Reference Links

- **Pine Script v5 User Manual**: [TradingView Pine Script Documentation](https://www.tradingview.com/pine-script-docs/)
- **Local Standards**: `docs/standards/pine-script-standards.md`
- **Syntax Fixes**: `docs/troubleshooting/pinescript-v5-syntax-fixes.md`
- **Development Workflow**: `docs/workflows/development-workflow.md`

---
*Keep this reference handy when developing Pine Script v5 strategies!*