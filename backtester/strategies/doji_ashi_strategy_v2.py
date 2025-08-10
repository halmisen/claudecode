"""
Doji Ashi Strategy v2 - Backtrader Implementation (Stability/Correctness Focus)

Source Reference: pinescript/strategies/reversal/Doji_Ashi_Strategy_v2.6.pine
Baseline Derived From: backtester/strategies/dojo1.py

Notes:
- Multi-timeframe safety: prefer confirmed daily values (use previous daily bar), warmup guard.
- ATR preference: TA-Lib when available; fallback to Backtrader.
- VWAP filter default OFF (enable later per roadmap); Volume filter optional.
- Order correctness: parent market entry; on fill compute SL/TP from executed price; create OCO children.
- Optional trailing stop and time-based exit.

Daily feed usage: If a daily feed is supplied as datas[1], it will be used; otherwise we fall back to primary feed.
"""

from __future__ import annotations

import backtrader as bt
import backtrader.indicators as btind


class DojiAshiStrategyV2(bt.Strategy):
    params = (
        # Direction & Filters
        ("trade_direction", "long"),  # 'long' | 'short' | 'both'
        ("enable_daily_trend_filter", True),
        ("trend_mode", "strict"),  # 'strict' | 'flexible'
        ("enable_entry_trigger", True),
        ("entry_mode", "above_below"),  # 'cross' | 'above_below'

        # Optional entry filters
        ("enable_vwap_filter_entry", False),
        ("enable_volume_filter", True),

        # Exit controls
        ("atr_length", 14),
        ("atr_multiplier", 1.5),
        ("risk_reward_ratio", 2.0),
        ("use_trailing_stop", False),
        ("trail_offset_percent", 1.0),  # percent
        ("use_time_exit", True),
        ("max_bars_in_trade", 100),

        # Sizing & trading cadence
        ("order_percent", 0.20),  # fraction of equity per trade (safer default)
        ("min_size", 0.001),
        ("size_step", 0.001),
        ("leverage", 4.0),
        ("cooldown_bars", 10),
        ("maker_mode", True),
        ("maker_limit_offset_percent", 0.02),  # 0.02% default maker offset to avoid instant fill
        ("pending_order_timeout_bars", 10),    # cancel unfilled maker orders after N bars

        # TALib preference
        ("use_talib", True),

        # Warmup control
        ("warmup_daily", 200),
    )

    def __init__(self):
        # Normalize enums
        self.trade_direction = str(self.p.trade_direction).lower()
        self.trend_mode = str(self.p.trend_mode).lower()
        self.entry_mode = str(self.p.entry_mode).lower()

        # Data references
        self.data_close = self.datas[0].close
        self.data_high = self.datas[0].high
        self.data_low = self.datas[0].low
        self.data_volume = getattr(self.datas[0], "volume", None)

        # Daily feed: prefer datas[1] if provided
        self.daily_data = self.datas[1] if len(self.datas) > 1 else self.datas[0]

        # Daily trend indicators
        self.daily_sma20 = btind.SMA(self.daily_data.close, period=20)
        self.daily_sma50 = btind.SMA(self.daily_data.close, period=50)
        self.daily_sma200 = btind.SMA(self.daily_data.close, period=200)

        # Count passes above SMAs (boolean sums)
        self.sma_pass_count = (
            (self.daily_data.close > self.daily_sma20)
            + (self.daily_data.close > self.daily_sma50)
            + (self.daily_data.close > self.daily_sma200)
        )

        # Define trend lines; use confirmed (previous) daily bar in logic
        if self.trend_mode == "strict":
            self.daily_uptrend = self.sma_pass_count == 3
            self.daily_downtrend = self.sma_pass_count == 0
        else:  # flexible
            self.daily_uptrend = self.sma_pass_count >= 2
            self.daily_downtrend = self.sma_pass_count <= 1

        # Trigger moving averages: EMA only (default)
        try:
            if self.p.use_talib and hasattr(bt, "talib"):
                self.ma3 = bt.talib.EMA(self.data_close, timeperiod=3)
                self.ma8 = bt.talib.EMA(self.data_close, timeperiod=8)
            else:
                raise AttributeError
        except Exception:
            self.ma3 = btind.EMA(self.data_close, period=3)
            self.ma8 = btind.EMA(self.data_close, period=8)

        # Entry signals (cross vs state)
        if self.entry_mode == "cross":
            self.sig_up = btind.CrossUp(self.ma3, self.ma8)
            self.sig_dn = btind.CrossDown(self.ma3, self.ma8)
        else:
            self.sig_up = self.ma3 > self.ma8
            self.sig_dn = self.ma3 < self.ma8

        # Optional filters
        if self.p.enable_vwap_filter_entry:
            try:
                self.vwap = btind.VWAP(self.datas[0])
            except Exception:
                self.vwap = None
        else:
            self.vwap = None
        if self.p.enable_volume_filter and self.data_volume is not None:
            self.avg_volume = btind.SMA(self.data_volume, period=20)
            self.high_rel_volume = self.data_volume > (self.avg_volume * 1.2)
        else:
            self.avg_volume = None
            self.high_rel_volume = None

        # ATR preference: TA‑Lib when available
        try:
            if self.p.use_talib and hasattr(bt, "talib"):
                self.atr = bt.talib.ATR(self.data_high, self.data_low, self.data_close, timeperiod=self.p.atr_length)
            else:
                raise AttributeError
        except Exception:
            self.atr = btind.ATR(self.datas[0], period=self.p.atr_length)

        # State
        self.parent_order = None
        self.sl_order = None
        self.tp_order = None
        self.trail_order = None
        self.entry_bar_index = None
        # Warmup bars for daily indicators (allow override via param)
        self.warmup_daily = max(int(self.p.warmup_daily), int(self.p.atr_length))
        self.last_long_bar = -10 ** 9
        self.last_short_bar = -10 ** 9
        self.parent_order_placed_bar = None

    # -------- Utility helpers --------
    def _confirmed_daily(self, line) -> bool:
        # Use previous daily value only; avoid lookahead
        if len(line) < 2:
            return False
        return bool(line[-1])

    def _can_long(self) -> bool:
        ok = True
        if self.p.enable_daily_trend_filter:
            ok = ok and bool(self._confirmed_daily(self.daily_uptrend))
        if self.p.enable_entry_trigger:
            ok = ok and bool(self.sig_up[0])
        if self.p.enable_vwap_filter_entry and self.vwap is not None:
            ok = ok and (self.data_close[0] > self.vwap[0])
        if self.p.enable_volume_filter and self.high_rel_volume is not None:
            ok = ok and bool(self.high_rel_volume[0])
        return ok

    def _can_short(self) -> bool:
        ok = True
        if self.p.enable_daily_trend_filter:
            ok = ok and bool(self._confirmed_daily(self.daily_downtrend))
        if self.p.enable_entry_trigger:
            ok = ok and bool(self.sig_dn[0])
        if self.p.enable_vwap_filter_entry and self.vwap is not None:
            ok = ok and (self.data_close[0] < self.vwap[0])
        if self.p.enable_volume_filter and self.high_rel_volume is not None:
            ok = ok and bool(self.high_rel_volume[0])
        return ok

    def _calc_size(self) -> float:
        equity = float(self.broker.getvalue())
        price = float(self.data_close[0])
        if equity <= 0 or price <= 0:
            return 0.0
        # allow leverage in position value
        position_value = equity * float(self.p.order_percent) * float(self.p.leverage)
        raw_size = position_value / price
        size = max(self.p.min_size, float(raw_size))
        # round down to size_step if provided
        step = float(getattr(self.p, "size_step", 0.0) or 0.0)
        if step > 0:
            size = (int(size / step)) * step
        return size

    # -------- Utility: order GC --------
    def _gc_orders(self):
        for name in ("parent_order", "sl_order", "tp_order", "trail_order"):
            o = getattr(self, name)
            if o is not None and not o.alive():
                setattr(self, name, None)

    # -------- Core Backtrader callbacks --------
    def next(self):
        # garbage-collect any completed/rejected orders to prevent deadlocks
        self._gc_orders()
        # Warmup: need confirmed daily SMAs and trigger MAs
        if len(self.daily_data) < self.warmup_daily:
            return

        # If any orders are pending or position open, manage exit/time only
        if self.parent_order or self.sl_order or self.tp_order or self.trail_order:
            # pending maker order timeout handling
            if self.parent_order and self.p.maker_mode and int(self.p.pending_order_timeout_bars) > 0:
                try:
                    placed_delta = (len(self) - int(self.parent_order_placed_bar)) if self.parent_order_placed_bar is not None else 0
                    if placed_delta >= int(self.p.pending_order_timeout_bars) and self.parent_order.alive():
                        self.cancel(self.parent_order)
                        self.parent_order = None
                        self.parent_order_placed_bar = None
                except Exception:
                    pass
            self._check_time_exit()
            # do not place new orders while any are pending/managed this bar
            return

        if self.position:
            self._check_time_exit()
            return

        # Cooldown
        current_bar = len(self)
        can_long_cool = current_bar - self.last_long_bar >= int(self.p.cooldown_bars)
        can_short_cool = current_bar - self.last_short_bar >= int(self.p.cooldown_bars)

        # Signals
        allow_long = self._can_long() and can_long_cool and self.trade_direction in ("long", "both")
        allow_short = self._can_short() and can_short_cool and self.trade_direction in ("short", "both")

        if allow_long:
            size = self._calc_size()
            if size <= 0:
                return
            if self.p.maker_mode:
                # place a slightly off-market limit to avoid taker
                offset = float(self.p.maker_limit_offset_percent) / 100.0
                limit_price = float(self.data_close[0]) * (1.0 - offset)
                self.parent_order = self.buy(size=size, exectype=bt.Order.Limit, price=limit_price)
                self.parent_order_placed_bar = current_bar
                self.last_long_bar = current_bar
            else:
                self.parent_order = self.buy(size=size, exectype=bt.Order.Market)
                self.last_long_bar = current_bar
        elif allow_short:
            size = self._calc_size()
            if size <= 0:
                return
            if self.p.maker_mode:
                offset = float(self.p.maker_limit_offset_percent) / 100.0
                limit_price = float(self.data_close[0]) * (1.0 + offset)
                self.parent_order = self.sell(size=size, exectype=bt.Order.Limit, price=limit_price)
                self.parent_order_placed_bar = current_bar
                self.last_short_bar = current_bar
            else:
                self.parent_order = self.sell(size=size, exectype=bt.Order.Market)
                self.last_short_bar = current_bar

    def _submit_children_after_fill(self, order: bt.Order):
        # Called when parent market order is completed
        executed_price = float(order.executed.price)
        size = float(order.executed.size)

        if self.p.use_trailing_stop:
            # Trailing stop only; no fixed TP
            if order.isbuy():
                self.trail_order = self.sell(exectype=bt.Order.StopTrail, trailpercent=self.p.trail_offset_percent / 100.0, size=size)
            else:
                self.trail_order = self.buy(exectype=bt.Order.StopTrail, trailpercent=self.p.trail_offset_percent / 100.0, size=size)
            return

        # Fixed SL/TP using OCO
        if order.isbuy():
            sl_price = executed_price - float(self.atr[0]) * float(self.p.atr_multiplier)
            tp_price = executed_price + (executed_price - sl_price) * float(self.p.risk_reward_ratio)
            tp = self.sell(exectype=bt.Order.Limit, price=tp_price, size=size)
            self.sl_order = self.sell(exectype=bt.Order.Stop, price=sl_price, size=size, oco=tp)
            self.tp_order = tp
        else:
            sl_price = executed_price + float(self.atr[0]) * float(self.p.atr_multiplier)
            tp_price = executed_price - (sl_price - executed_price) * float(self.p.risk_reward_ratio)
            tp = self.buy(exectype=bt.Order.Limit, price=tp_price, size=size)
            self.sl_order = self.buy(exectype=bt.Order.Stop, price=sl_price, size=size, oco=tp)
            self.tp_order = tp

    def _check_time_exit(self):
        if not self.p.use_time_exit:
            return
        if not self.position:
            return
        if self.entry_bar_index is None:
            return
        if (len(self) - int(self.entry_bar_index)) >= int(self.p.max_bars_in_trade):
            # Close the position; cancel protective orders
            if self.sl_order:
                self.cancel(self.sl_order)
                self.sl_order = None
            if self.tp_order:
                self.cancel(self.tp_order)
                self.tp_order = None
            if self.trail_order:
                self.cancel(self.trail_order)
                self.trail_order = None
            self.close()

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order == self.parent_order:
                # Parent filled → submit children and record entry bar
                self.entry_bar_index = len(self)
                self._submit_children_after_fill(order)
                self.parent_order = None
                self.parent_order_placed_bar = None
            else:
                # Child orders filled → clear references
                if order == self.sl_order:
                    self.sl_order = None
                elif order == self.tp_order:
                    self.tp_order = None
                elif order == self.trail_order:
                    self.trail_order = None
                # If position flat after child fill, clear all state
                if not self.position:
                    self.sl_order = self.tp_order = self.trail_order = None
                    self.entry_bar_index = None

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            # Clear references on failure
            if order == self.parent_order:
                self.parent_order = None
                self.parent_order_placed_bar = None
            elif order == self.sl_order:
                self.sl_order = None
            elif order == self.tp_order:
                self.tp_order = None
            elif order == self.trail_order:
                self.trail_order = None

    def notify_trade(self, trade):
        if trade.isclosed:
            self.sl_order = self.tp_order = self.trail_order = None
            self.entry_bar_index = None

    def stop(self):
        # Optional: final parameter printout for reproducibility
        print("\n=== DojiAshiStrategyV2 Parameters ===")
        print(f"Direction: {self.p.trade_direction}")
        print(f"Daily Trend Filter: {self.p.enable_daily_trend_filter} ({self.p.trend_mode})")
        print(f"Trigger: {self.p.enable_entry_trigger} EMA/{self.p.entry_mode}")
        print(f"ATR len/mult: {self.p.atr_length}/{self.p.atr_multiplier}  RR: {self.p.risk_reward_ratio}")
        print(f"VWAP/Volume filters: {self.p.enable_vwap_filter_entry}/{self.p.enable_volume_filter}")
        print(f"Trailing/Time Exit: {self.p.use_trailing_stop}/{self.p.use_time_exit} (trail%={self.p.trail_offset_percent}, maxBars={self.p.max_bars_in_trade})")
        print(f"Order%: {self.p.order_percent}  MinSize: {self.p.min_size}  Cooldown: {self.p.cooldown_bars}")

