# Development Workflow Guide

This document provides detailed command-line operations and development workflows for the cryptocurrency trading strategy project.

## Pine Script Development Workflow

### Development Process
1. Creating/modifying `.pine` files
2. **Pre-compilation syntax check** (see Pine Script v5 Checklist below)
3. Testing in TradingView editor
4. Validating against the Golden Rulebook standards (see `docs/standards/pine-script-standards.md`)
5. **Post-compilation validation** (see Validation Checklist below)
6. Committing changes with descriptive messages

### Pine Script v5 Pre-Compilation Checklist

Before testing in TradingView, always verify:

#### Variable Declaration
- [ ] All variables use type prefixes (`float_`, `bool_`, `int_`, `string_`)
- [ ] State variables declared with `var` keyword
- [ ] No undeclared identifiers or typos in variable names
- [ ] Variables initialized before use (especially for `+=` operations)

#### Function Parameters
- [ ] TA functions use `simple int` parameters (input parameters, not calculated)
- [ ] `strategy.entry()` uses correct parameter names (`qty`, not `qty_percent`)
- [ ] No dynamic parameters for `ta.ema()`, `ta.sma()`, etc.

#### Syntax Structure
- [ ] All ternary operators on single line
- [ ] No multi-line statements without proper continuation
- [ ] Function declarations on single line with `=>`
- [ ] No functions defined inside conditional blocks

#### Strategy-Specific
- [ ] Strategy declaration includes proper `default_qty_type` and `default_qty_value`
- [ ] Position sizing uses correct Pine Script v5 API
- [ ] Alert conditions use valid variable references
- [ ] Variable declaration order: inputs → calculations → state management → execution
- [ ] State variables (`var`) declared before position management logic

### Post-Compilation Validation Checklist

After successful compilation in TradingView:

#### Functional Testing
- [ ] Strategy generates entry and exit signals
- [ ] Risk management features work (stops, position sizing)
- [ ] Status panel displays correct information
- [ ] Alerts trigger properly

#### Performance Validation
- [ ] No compilation warnings or errors
- [ ] Strategy runs without timeouts
- [ ] Plots and visualizations render correctly
- [ ] Backtest executes successfully

#### Code Quality
- [ ] Logic matches intended trading strategy
- [ ] Edge cases handled properly (division by zero, etc.)
- [ ] State management works correctly across bars
- [ ] Memory usage is efficient

## Single Position Management Strategies

### Additional Development Requirements

For strategies implementing single position management (like Four Swords v1.6):

#### Variable Declaration Pattern
```pinescript
// 1. Input parameters
// 2. Market state detection
// 3. Core calculations
// 4. State management variables (CRITICAL: before usage)
var bool bool_waitLongExit = false
var bool bool_waitShortExit = false
// 5. Position state variables
bool_hasPosition = strategy.position_size != 0
bool_isLong = strategy.position_size > 0
bool_isShort = strategy.position_size < 0
```

#### Single Position Logic Checklist
- [ ] Only one position allowed at any time
- [ ] Position state variables declared before use
- [ ] Reverse signal handling (close + new entry)
- [ ] State reset on position close
- [ ] Exit logic has higher priority than entry logic
- [ ] Clear visual distinction between entry types (new vs reversal)

#### Trading Execution Priority
1. **Exit Logic** (highest priority): Stop loss, signal exit, time exit
2. **Reversal Signals** (medium priority): Close current + open opposite
3. **New Entry** (lowest priority): Only when no position exists

#### State Management Verification
- [ ] `var` variables maintain state across bars
- [ ] Position detection variables recalculate each bar
- [ ] State reset only occurs after actual position close
- [ ] Reverse signal updates all relevant state variables
- [ ] No conflicting state conditions

#### Visual Feedback Requirements
- [ ] Different colors for new entry vs reversal signals
- [ ] Position status clearly displayed in status panel
- [ ] Exit signals visually distinguishable
- [ ] Stop loss lines displayed when active

### File Organization

#### Naming Convention
- Use underscores instead of spaces and special characters
- Remove brackets, plus signs, and other special characters
- Indicators: `Category_Name.pine` (e.g., `Squeeze_Momentum_LB.pine`)
- Strategies: `Approach_Strategy.pine` (e.g., `Simple_Reversal_Strategy.pine`)
- Version numbers use underscores: `v2_5` instead of `v2.5`
- All files use `.pine` extension for consistency

#### Documentation Standards
- Standardized summary modules at the beginning of each file
- Summary format: `// ⌘ SUMMARY:` followed by Type, Purpose, Key Inputs, Outputs, Functions, Logic
- Author and date headers
- Clear strategy descriptions
- Reference links to trading concepts
- Input parameter tooltips

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

## Python Development Workflow

### Strategy Development
1. **Environment Setup**: Use virtual environments for each framework
2. **Dependency Management**: Install requirements from respective directories
3. **Data Management**: Fetch and prepare data using provided utilities
4. **Strategy Development**: Create and test strategies in respective framework directories
5. **Backtesting**: Run backtests using framework-specific commands
6. **Validation**: Compare results across frameworks and with Pine Script implementations

### Testing and Validation
- Implement unit tests for individual components
- Use cross-validation for strategy robustness
- Compare results with original Pine Script implementations
- Document performance characteristics and limitations

### Signal Frequency Debugging ⭐ NEW
**Critical for Multi-Filter Strategies**: When strategies produce insufficient trades despite sound logic:

1. **Implement Signal Flow Observability**: Add counters at each filtering stage
2. **Create Baseline Configuration**: Test core logic without filters
3. **Systematic Filter Analysis**: Test each filter independently with parameter matrices
4. **Document Signal Loss**: Track conversion rates through each filtering stage

**Key Reference**: [`signal-frequency-debugging-methodology.md`](signal-frequency-debugging-methodology.md) - Complete methodology developed during Four Swords v1.7.4 optimization

**When to Use**: 
- Strategy produces <15 trades on multi-year data
- Unclear why signal frequency is low
- Multiple filter parameters need optimization
- Converting PineScript strategies to Python for optimization

## Git Workflow

### Commit Standards
- Use descriptive commit messages
- Follow conventional commit format
- Include relevant issue numbers when applicable
- Keep commits focused on single changes

### Branch Management
- Use feature branches for new developments
- Keep master branch stable
- Use pull requests for code review
- Ensure all tests pass before merging

## Clean, efficient, and predictable code is the ultimate goal! 🚀