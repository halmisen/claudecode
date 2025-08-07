# Doji Ashi V3 (doji3.py) - PineScript to Backtrader Conversion Plan

This document outlines the plan for converting the `Doji_Ashi_Strategy 2.6.PINE` script into a new Backtrader-compatible Python strategy, `doji3.py`. The development will follow an iterative approach, starting with a core functional version (V1) and outlining a roadmap for future enhancements.

---

### V1 (Current Version) - Core Logic Implementation

The primary goal for the initial version is to create a stable, understandable, and testable strategy based on the user's core requirements.

**V1 Scope:**

1.  **Trading Direction**: The strategy will be configured for **Long Only** trades to simplify the initial logic.
2.  **Position Management**: The strategy will only allow **one position to be open at a time**.
3.  **Entry Trigger**: The core entry signal will be based on the **EMA (Exponential Moving Average)**, using the **'Above/Below'** state logic (fast MA is above slow MA).
4.  **Exit Mechanism**: The primary exit strategy will be a **Trailing Stop Loss**. The trail offset will be based on a percentage (`trail_offset`). The initial stop loss price will be determined by ATR, but the position will be managed by the trailing stop order.
5.  **Enabled Filters**: The following filters will be implemented and enabled by default:
    *   `enable_volume_filter`: Confirms trade with significant volume.
    *   `enable_vwap_filter_entry`: Ensures price is on the correct side of the VWAP for entry.

---

### Future Roadmap & Planned Enhancements

These features were identified as valuable but add complexity. They will be targeted in future updates to the strategy.

1.  **Multi-Data Source Integration (Relative Strength)**:
    *   **Goal**: Implement the `enable_relative_strength` filter.
    *   **Challenge**: This requires loading a second data feed (e.g., SPY) alongside the main asset and ensuring their timestamps are synchronized. This will be a major feature update.

2.  **Multi-Timeframe Analysis (Daily Trend Filter)**:
    *   **Goal**: Implement the `enable_daily_trend_filter`.
    *   **Challenge**: This requires using Backtrader's `resampledata` functionality to create a daily data feed from the primary data. The logic must then correctly align the daily signals with the intraday trading timeframe.

3.  **Advanced Moving Averages**:
    *   **Goal**: Add support for `ZLEMA` (Zero-Lag EMA) and `HULL` (Hull Moving Average) as options for the entry trigger.
    *   **Challenge**: These are not standard Backtrader indicators and will require custom implementation.

4.  **Short Selling & Bidirectional Trading**:
    *   **Goal**: Expand the strategy to fully support `'Short'` and `'Both'` trade directions.
    *   **Challenge**: Requires adding and testing the logic for short-side entries and exits, ensuring all filters work correctly for both market directions.

---

### V1 Implementation Plan (TODO)

**Phase 1: Framework and Parameters**
1.  **Create/Update File**: Ensure `backtester/backtests/strategies/doji3.py` exists.
2.  **Define Strategy Class**: Create `DojiAshiV3(bt.Strategy)`.
3.  **Set Parameters**: Define the `params` dictionary, setting defaults according to the V1 scope (e.g., `trade_direction='Long'`, `use_trailing_stop=True`, etc.).

**Phase 2: Indicator Initialization (`__init__`)**
4.  **Reference Single Data Feed**: The `__init__` method will only work with `self.datas[0]`.
5.  **Define V1 Indicators**: Implement only the indicators needed for V1: EMA (fast/slow), VWAP, Volume SMA, and ATR.

**Phase 3: Core Trading Logic (`next` & `notify_order`)**
6.  **Implement `next()`**: Write the entry logic for **Long Only** positions, checking all V1 filter conditions.
7.  **Implement `notify_order()`**: When a buy order completes, submit a `bt.Order.StopTrail` order to manage the position's exit.

**Phase 4: Verification**
8.  **Update Runner**: Ensure the `if __name__ == '__main__':` block is simple, loading only **one** data feed to test the V1 strategy.