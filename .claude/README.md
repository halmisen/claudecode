# Claude Agent Configuration for Pine Script Trading Project

This directory contains specialized agent configurations for enhanced Pine Script development and trading strategy implementation.

## Available Agents

### Pine Script Specialist Agent
**Location**: `agents/pine-script-specialist.md`  
**Purpose**: Expert Pine Script v5 development with syntax validation and error prevention

**Capabilities**:
- Pine Script v5 syntax validation and compilation error prevention
- SQZMOM and WaveTrend indicator implementation expertise
- Trading strategy development and optimization
- TradingView integration and backtesting setup
- Performance optimization and best practices enforcement

**Auto-Activation Triggers**:
- Keywords: pine script, tradingview, strategy, indicator, sqzmom, wavetrend
- File extensions: .pine
- Directories: pinescript/, pinescript/strategies/, pinescript/indicators/

## Setup Instructions

### 1. Global Agent Installation (Recommended)
Copy the agent to your global Claude configuration:
```bash
# Create global Claude config directory if it doesn't exist
mkdir -p "%USERPROFILE%\.claude\agents"

# Copy the Pine Script specialist agent
copy ".claude\agents\pine-script-specialist.md" "%USERPROFILE%\.claude\agents\"
```

### 2. Project-Local Usage
The agents are already configured in this project directory (`.claude/agents/`) and will be automatically available when working within this project.

### 3. Verification
To verify the agent is available:
```bash
# Check if agent file exists
dir "%USERPROFILE%\.claude\agents\pine-script-specialist.md"

# Or check project-local version
dir ".claude\agents\pine-script-specialist.md"
```

## Usage

### Automatic Activation
The Pine Script Specialist agent will automatically activate when:
- Working with .pine files
- Mentioning Pine Script related keywords
- Working in pinescript/ directories
- Encountering Pine Script compilation errors

### Manual Activation
You can explicitly invoke the agent by mentioning:
- "Ask the pine-script-specialist to..."
- "Use pine script agent to..."
- "Pine script specialist, please..."

### Integration with Project Standards
The agent is configured to:
- Always reference `docs/standards/pine-script-standards.md`
- Follow project naming conventions and file organization
- Integrate with the Python backtesting pipeline
- Maintain consistency with existing strategies

## Agent Features

### Syntax Validation
- Prevents common Pine Script v5 compilation errors
- Enforces single-line function declarations and ternary operators
- Validates series vs simple type usage
- Checks proper variable declaration patterns

### Code Quality
- Enforces type prefix naming conventions
- Ensures proper variable scoping with `var` keyword
- Validates strategy.entry() parameter usage
- Optimizes performance and memory usage

### Strategy Development
- Implements standardized strategy templates
- Provides SQZMOM and WaveTrend expertise
- Configures proper backtest settings
- Ensures TradingView compatibility

### Error Prevention
- Pre-compilation error checking
- Common pitfall identification
- Best practice enforcement
- Performance optimization guidance

## Configuration Files

### config.json
Contains agent settings, auto-activation triggers, and project integration settings.

### Standards Integration
The agent automatically references:
- `docs/standards/pine-script-standards.md` - Complete Pine Script v5 standards
- `docs/templates/` - Code templates and examples
- `docs/workflows/pine-to-python-conversion.md` - Conversion workflows

## Troubleshooting

### Agent Not Activating
1. Verify agent file exists in `%USERPROFILE%\.claude\agents\`
2. Check that keywords are properly spelled
3. Ensure you're working within the project directory

### Standards Not Found
If the agent cannot find the standards document:
1. Verify `docs/standards/pine-script-standards.md` exists
2. Check that you're in the project root directory
3. Update the path in `config.json` if necessary

### Compilation Errors
If Pine Script code still has compilation errors:
1. Manually reference the standards document
2. Check for series vs simple type conflicts
3. Verify all variables are properly declared
4. Ensure functions are in global scope

## Contributing

To improve the Pine Script Specialist agent:
1. Update `agents/pine-script-specialist.md` with new capabilities
2. Add new keywords to `config.json` auto-activation triggers
3. Update this README with new features
4. Test the agent with real Pine Script development tasks

## Related Documentation

- [Pine Script Standards](../docs/standards/pine-script-standards.md)
- [Pine to Python Conversion Workflow](../docs/workflows/pine-to-python-conversion.md)
- [TradingView Testing Guide](../docs/workflows/tradingview-testing-guide.md)
- [Project Architecture](../CLAUDE.md)