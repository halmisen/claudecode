# Utils Directory

This directory contains utility functions and scripts for the KFC trading algorithm project.

## Directory Structure

```
utils/
├── validation/           # Strategy validation and verification scripts
│   ├── logic_consistency_check.py
│   └── manual_logic_verification.py
└── README.md            # This file
```

## Usage

### Validation Scripts
The validation scripts are used to verify the consistency between different framework implementations:

- **logic_consistency_check.py**: Automated consistency checking between Pine Script, Jesse, and VectorBT implementations
- **manual_logic_verification.py**: Manual verification of key logic components

### Running Validation
```bash
# Run automated consistency check
python utils/validation/logic_consistency_check.py

# Run manual verification
python utils/validation/manual_logic_verification.py
```

## Adding New Utilities

When adding new utility scripts:
1. Place them in appropriate subdirectories
2. Follow the existing naming conventions
3. Include proper documentation
4. Add examples in the README

## Clean, efficient, and predictable code is the ultimate goal! 🚀