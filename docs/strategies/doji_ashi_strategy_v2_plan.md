# Doji Ashi Strategy v2.6 → Backtrader Conversion Plan (doji3)

This document tracks the conversion from `pinescript/strategies/reversal/Doji_Ashi_Strategy_v2.6.pine` to the current Python implementation in `claudecode/backtester/strategies/doji_ashi_strategy_v2.py`. It outlines the features implemented, identifies remaining gaps, and defines the future development roadmap. This file reflects the state of the **latest version** of the strategy.

---

### Current Implementation Status: `doji3.py`

The Python version has reached a high level of feature parity with the Pine Script reference and includes additional enhancements for robust backtesting.

**Core Logic & Filters:**
- **Trade Direction:** Fully supports `long`, `short`, and `both` via the `trade_direction` parameter.
- **Daily Trend Filter:** Implemented using a secondary daily data feed (`datas[1]`). Supports `SMA` and `EMA` (`trend_ma_type_daily`) of a configurable length (`trend_ma_len_daily`) with `strict` and `flexible` modes.
- **Entry Trigger:** Core 3/8 MA logic is in place, using `fast_ma_len` and `slow_ma_len`. Supports `cross` and `above_below` modes (`entry_mode`).
- **Trigger MA Types:** Supports `EMA`, `SMA`, `HMA` (Hull), and `ZLEMA`. *(Note: See Gap Analysis for ZLEMA fidelity)*.
- **Market Filter (SPY/BTC):** Implemented using a third data feed (`datas[2]`). The market is considered bullish/bearish based on its price relative to a configurable MA (`market_ma_type`, `market_ma_len`).
- **Relative Strength Filter:** Implemented for stocks vs. a market index (e.g., SPY). Calculates a Relative Strength line and compares it to its MA (`rs_ma_len`).
- **Volume Filter:** Filters entries based on volume being a certain multiple (`volume_factor`) above its moving average (`volume_ma_len`).
- **VWAP Filter:** Filters long/short entries based on price being above/below the VWAP.
- **Time Filter:** Allows trades to be restricted to a specific time window (`time_filter_start_hour/min`, `time_filter_end_hour/min`).
- **Cooldown Period:** Prevents new trades for a specified number of bars (`cooldown_bars`) after a trade is closed.

**Risk Management & Exits:**
- **ATR Bracket Orders:** Primary risk management using ATR-based Stop Loss and Take Profit levels (`atr_length`, `atr_multiplier`, `risk_reward_ratio`).
- **Trailing Stop:** Optional percentage-based trailing stop (`use_trailing_stop`, `trail_percent`) as an alternative to the fixed bracket.
- **Time-based Exit:** Optional exit after a maximum number of bars in a trade (`use_time_exit`, `max_bars_in_trade`).

**Backtesting & Infrastructure:**
- **Multi-Timeframe Handling:** Correctly set up with `cerebro.resampledata` for the daily feed and `cerebro.adddata` for the market feed, preventing lookahead bias.
- **Sizing & Costs:** Uses `PercentSizer` for position sizing (`sizing_pct`) and includes settings for commission.
- **Indicator Fidelity:** Uses TA-Lib for indicators where available (`HAS_TALIB` flag), with fallbacks to Backtrader's built-in indicators.
- **Analytics & Logging:** Integrates standard Backtrader analyzers (Sharpe, DrawDown, SQN, TradeAnalyzer) and uses `loguru` for detailed logging.

---

### Gap Analysis & Future Improvements

1.  **ZLEMA Implementation Fidelity:**
    -   **Current:** The `ZLEMA` indicator in `doji3.py` is currently implemented as a DEMA (Double Exponential Moving Average): `(2 * EMA(price)) - EMA(EMA(price))`.
    -   **Required:** The standard Pine Script ZLEMA formula is `EMA(2*price - price[period-1], period)`.
    -   **Action:** The custom `ZLEMA` class should be updated to match the correct formula to ensure strategy logic aligns perfectly with the reference.

2.  **Robustness & Testing:**
    -   **Current:** The strategy is functionally complete but lacks a dedicated suite of unit and integration tests.
    -   **Required:** Create tests to verify the correctness of:
        -   Custom indicators (especially the fixed ZLEMA).
        -   Entry/exit conditions under various filter combinations.
        -   Multi-timeframe data handling and alignment.
        -   Behavior of different exit strategies (bracket vs. trailing vs. time-based).

3.  **Configuration & Presets:**
    -   **Current:** Parameters are exposed, but there are no presets that mirror the Pine Script version (e.g., "Crypto" or "Stocks" presets that configure multiple parameters at once).
    -   **Action:** Consider adding a `preset` parameter that automatically configures related settings for easier testing of standard scenarios.

---

### Roadmap

**V1 (Completed in `doji3.py`)**
-   Full feature parity with Pine Script v2.6, including all filters (Daily, Market, RS, Volume, VWAP, Time), exit strategies, and core logic.
-   Robust backtesting infrastructure with multi-timeframe data, analytics, and logging.

**V2 (Next Steps)**
-   **[High Priority]** Correct the `ZLEMA` indicator implementation to match the standard formula.
-   Develop a comprehensive test suite to ensure the strategy's logic is deterministic and correct.
-   Refine parameter validation and add configuration presets for simplified use.

**V3 (Future Enhancements)**
-   Performance optimization of indicator calculations if needed.
-   Integration with additional analytics or visualization tools.

---

### Parameter Mapping: Pine → Python (`doji3.py`)

The mapping is nearly 1-to-1. All major parameters from the Pine Script version are available in the Python implementation.

-   `Trade Direction` → `trade_direction`
-   `Use Daily Trend Filter` → `enable_daily_trend_filter`
-   `Use Market Trend Filter` → `enable_market_filter`
-   `Use Relative Strength Filter` → `enable_relative_strength`
-   `Use Entry Trigger` → `enable_entry_trigger`
-   `Trigger MA Type` → `trigger_ma_type`
-   `3/8 MA Entry Mode` → `entry_mode`
-   `Use VWAP for Entry Filter` → `enable_vwap_filter_entry`
-   `Use Relative Volume Filter` → `enable_volume_filter`
-   `Use Trailing Stop` → `use_trailing_stop`
-   `Use Time-based Exit` → `use_time_exit`
-   ... and all corresponding length, multiplier, and level parameters.
