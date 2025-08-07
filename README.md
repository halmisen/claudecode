# Project Overview

This project has undergone several structural optimizations to improve clarity, consistency, and maintainability.

## Optimizations Performed:

1.  **Unified Pine Script File Extensions**: All Pine Script files (`.PINE`) have been standardized to use the lowercase `.pine` extension for consistency.
2.  **Standardized Filenames**: Filenames containing spaces have been renamed to use underscores (`_`) for better compatibility and readability in command-line environments. For example, `Doji_Ashi_Strategy 2.6.PINE` is now `Doji_Ashi_Strategy_v2.6.pine`.
3.  **Consolidated Redundant Scripts**: The duplicate `download_data.py` script in `backtester/scripts/` has been removed, with the primary version retained in the project root for centralized utility management.
4.  **Organized Documentation**: Specific strategy-related documentation, such as `doji3_conversion_plan.md`, has been moved into a new `docs/strategies/` subdirectory to maintain a cleaner and more organized `docs` root.
5.  **Consistent Naming for Pine Script Strategies**: Pine Script strategy files like `doji1_1.pine` and `doji2_v1.2.pine` have been renamed to `doji_v1.1.pine` and `doji_v1.2.pine` respectively, to follow a more consistent `strategy_name_vX.X.pine` format.

These changes aim to make the project structure more intuitive and easier to navigate for future development and collaboration.