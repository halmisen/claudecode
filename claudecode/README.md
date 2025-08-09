交互式图表（Plotly）
1）安装依赖
   pip install -r requirements.txt
   # 如需 TA-Lib（本机）：
   # pip install -r requirements-local.txt

2）从 CSV 生成交互图（K线 + 成交标记 + 资金曲线）
   python examples/run_csv_and_plot.py --csv path/to/ohlcv.csv --out reports/plot.html
   # 携带成交与资金曲线（列名自适应）：
   python examples/run_csv_and_plot.py --csv path/to/ohlcv.csv --trades path/to/trades.csv --equity path/to/equity.csv --out reports/plot.html --title "BTCUSDT 4h Backtest"

3）CSV 列名约定
   - 时间列：datetime / date / time / timestamp / open_time 其一 (现在支持毫秒级Unix时间戳，预处理后转换为YYYY-MM-DD HH:MM:SS)
   - 价格列：open / high / low / close
   - 成交量：volume/vol（可选）
   - 交易明细：至少包含 datetime 与 price；可选 side（buy/sell）、size、pnl
   - 资金曲线：任意一列作为数值，允许列名 equity 或 value，并支持 datetime 作为索引列

# Project Overview

This project has undergone several structural optimizations to improve clarity, consistency, and maintainability.

## Optimizations Performed:

1.  **Unified Pine Script File Extensions**: All Pine Script files (`.PINE`) have been standardized to use the lowercase `.pine` extension for consistency.
2.  **Standardized Filenames**: Filenames containing spaces have been renamed to use underscores (`_`) for better compatibility and readability in command-line environments. For example, `Doji_Ashi_Strategy 2.6.PINE` is now `Doji_Ashi_Strategy_v2.6.pine`.
3.  **Consolidated Redundant Scripts**: The duplicate `download_data.py` script in `backtester/scripts/` has been removed, with the primary version retained in the project root for centralized utility management.
4.  **Organized Documentation**: Specific strategy-related documentation, such as `doji3_conversion_plan.md`, has been moved into a new `docs/strategies/` subdirectory to maintain a cleaner and more organized `docs` root.
5.  **Consistent Naming for Pine Script Strategies**: Pine Script strategy files like `doji1_1.pine` and `doji2_v1.2.pine` have been renamed to `doji_v1.1.pine` and `doji_v1.2.pine` respectively, to follow a more consistent `strategy_name_vX.X.pine` format.

### Backtrader Plotting with Bokeh

*   The `dojo1_v2.py` strategy now automatically uses `backtrader_plotting` with `Bokeh` for interactive visualizations when run directly.
*   Data preprocessing is handled automatically for timestamp conversion.


# Project Overview

This project has undergone several structural optimizations to improve clarity, consistency, and maintainability.

## Optimizations Performed:

1.  **Unified Pine Script File Extensions**: All Pine Script files (`.PINE`) have been standardized to use the lowercase `.pine` extension for consistency.
2.  **Standardized Filenames**: Filenames containing spaces have been renamed to use underscores (`_`) for better compatibility and readability in command-line environments. For example, `Doji_Ashi_Strategy 2.6.PINE` is now `Doji_Ashi_Strategy_v2.6.pine`.
3.  **Consolidated Redundant Scripts**: The duplicate `download_data.py` script in `backtester/scripts/` has been removed, with the primary version retained in the project root for centralized utility management.
4.  **Organized Documentation**: Specific strategy-related documentation, such as `doji3_conversion_plan.md`, has been moved into a new `docs/strategies/` subdirectory to maintain a cleaner and more organized `docs` root.
5.  **Consistent Naming for Pine Script Strategies**: Pine Script strategy files like `doji1_1.pine` and `doji2_v1.2.pine` have been renamed to `doji_v1.1.pine` and `doji_v1.2.pine` respectively, to follow a more consistent `strategy_name_vX.X.pine` format.

These changes aim to make the project structure more intuitive and easier to navigate for future development and collaboration.