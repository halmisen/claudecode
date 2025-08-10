# Development Workflow Guide

This document provides detailed command-line operations and development workflows for the cryptocurrency trading strategy project.

## Pine Script Development Workflow

### Development Process
1. Creating/modifying `.pine` files
2. Testing in TradingView editor
3. Validating against the Golden Rulebook standards (see `docs/pine-script-standards.md`)
4. Committing changes with descriptive messages

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