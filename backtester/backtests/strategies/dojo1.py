"""
Doji Ashi Strategy v1.1 - Backtrader Implementation
Converted from Pine Script: claudecode/strategies/reversal/doji1_1.pine

Strategy Logic:
- Uses daily trend filter (20, 50, 200 SMAs)
- Entry trigger based on 3/8 MA crossover
- ATR-based stop loss and take profit
"""

import backtrader as bt
import backtrader.indicators as btind


class DojiAshiStrategy(bt.Strategy):
    """
    Doji Ashi Strategy - Core version for Backtrader
    """
    
    params = (
        # Strategy Parameters
        ('trade_direction', 'long'),  # 'long', 'short', 'both'
        ('enable_daily_trend_filter', True),
        ('trend_mode', 'strict'),  # 'strict', 'flexible'
        ('enable_entry_trigger', True),
        ('trigger_ma_type', 'ema'),  # 'ema', 'zlema', 'hull'
        ('entry_mode', 'above_below'),  # 'cross', 'above_below'
        
        # Risk Management
        ('atr_length', 14),
        ('atr_multiplier', 1.5),
        ('risk_reward_ratio', 2.0),
        
        # Position Sizing
        ('order_percent', 0.20),  # 20% of equity per trade
        ('cooldown_bars', 5),     # Cooldown bars between signals
    )
    
    def __init__(self):
        # Store parameters
        self.trade_direction = self.params.trade_direction.lower()
        self.enable_daily_trend_filter = self.params.enable_daily_trend_filter
        self.trend_mode = self.params.trend_mode.lower()
        self.enable_entry_trigger = self.params.enable_entry_trigger
        self.trigger_ma_type = self.params.trigger_ma_type.lower()
        self.entry_mode = self.params.entry_mode.lower()
        
        # Daily data for trend filter (resampled from primary data)
        if len(self.datas) > 1:
            self.daily_data = self.datas[1]
        else:
            self.daily_data = self.datas[0]
        
        # Daily indicators
        self.daily_sma20 = btind.SMA(self.daily_data, period=20)
        self.daily_sma50 = btind.SMA(self.daily_data, period=50)
        self.daily_sma200 = btind.SMA(self.daily_data, period=200)
        
        # Count how many SMAs price is above
        self.sma_pass_count = (
            (self.daily_data.close > self.daily_sma20) +
            (self.daily_data.close > self.daily_sma50) +
            (self.daily_data.close > self.daily_sma200)
        )
        
        # Determine trend direction
        if self.trend_mode == 'strict':
            self.daily_uptrend = self.sma_pass_count == 3
            self.daily_downtrend = self.sma_pass_count == 0
        else:  # flexible
            self.daily_uptrend = self.sma_pass_count >= 2
            self.daily_downtrend = self.sma_pass_count <= 1
        
        # Entry trigger MAs
        if self.trigger_ma_type == 'ema':
            self.ma3 = btind.EMA(period=3)
            self.ma8 = btind.EMA(period=8)
        elif self.trigger_ma_type == 'zlema':
            # Zero Lag EMA approximation
            ema3 = btind.EMA(period=3)
            ema8 = btind.EMA(period=8)
            self.ma3 = 2 * ema3 - ema3(-3)
            self.ma8 = 2 * ema8 - ema8(-8)
        else:  # hull
            self.ma3 = btind.HMA(period=3)
            self.ma8 = btind.HMA(period=8)
        
        # Entry signals
        if self.entry_mode == 'cross':
            self.ema_cross_up = btind.CrossUp(self.ma3, self.ma8)
            self.ema_cross_down = btind.CrossDown(self.ma3, self.ma8)
        else:  # above_below
            self.ema_cross_up = self.ma3 > self.ma8
            self.ema_cross_down = self.ma3 < self.ma8
        
        # ATR for stop loss/take profit
        self.atr = btind.ATR(period=self.params.atr_length)
        
        # Track orders
        self.order = None
        self.entry_orders = []  # Store bracket orders list
        
        # Track last trade bars for cooldown
        self.last_long_bar = -9999
        self.last_short_bar = -9999
        
    def next(self):
        # Wait for daily indicators to be ready
        if len(self.daily_sma200) < 1:
            return
            
        # If we have open orders, do nothing
        if self.entry_orders:
            return
            
        # If we already have a position, do nothing (SL/TP handled by bracket orders)
        if self.position:
            return
            
        # Check cooldown
        current_bar = len(self)
        long_ok = current_bar - self.last_long_bar >= self.params.cooldown_bars
        short_ok = current_bar - self.last_short_bar >= self.params.cooldown_bars
            
        # Check entry conditions
        long_entry = True
        short_entry = True
        
        # Apply daily trend filter if enabled
        if self.enable_daily_trend_filter:
            long_entry = long_entry and self.daily_uptrend[0]
            short_entry = short_entry and self.daily_downtrend[0]
        
        # Apply entry trigger if enabled
        if self.enable_entry_trigger:
            long_entry = long_entry and self.ema_cross_up[0]
            short_entry = short_entry and self.ema_cross_down[0]
        
        # Execute trades based on direction
        if long_entry and long_ok and self.trade_direction in ['long', 'both']:
            self.last_long_bar = current_bar
            self.enter_long()
        elif short_entry and short_ok and self.trade_direction in ['short', 'both']:
            self.last_short_bar = current_bar
            self.enter_short()
    
    def enter_long(self):
        """Enter long position with SL/TP"""
        # Calculate position size based on total portfolio value
        portfolio_value = self.broker.getvalue()
        if portfolio_value <= 0:
            return
        # Use percentage of portfolio value
        position_value = portfolio_value * self.params.order_percent
        size = position_value / self.data.close[0]
        size = max(1, int(size))  # At least 1 unit, round to whole number
        
        # Calculate SL and TP levels
        sl_price = self.data.close[0] - (self.atr[0] * self.params.atr_multiplier)
        tp_price = self.data.close[0] + ((self.data.close[0] - sl_price) * self.params.risk_reward_ratio)
        
        # Create bracket order (entry with attached SL/TP)
        self.entry_orders = self.buy_bracket(
            size=size,
            price=self.data.close[0],  # Market order for entry
            stopprice=sl_price,       # Stop loss price
            limitprice=tp_price       # Take profit price
        )
        
        # Log the trade
        self.log(f'LONG ENTER: Price={self.data.close[0]:.2f}, '
                f'SL={sl_price:.2f}, TP={tp_price:.2f}, Size={size}')
    
    def enter_short(self):
        """Enter short position with SL/TP"""
        # Calculate position size based on total portfolio value
        portfolio_value = self.broker.getvalue()
        if portfolio_value <= 0:
            return
        # Use percentage of portfolio value
        position_value = portfolio_value * self.params.order_percent
        size = position_value / self.data.close[0]
        size = max(1, int(size))  # At least 1 unit, round to whole number
        
        # Calculate SL and TP levels
        sl_price = self.data.close[0] + (self.atr[0] * self.params.atr_multiplier)
        tp_price = self.data.close[0] - ((sl_price - self.data.close[0]) * self.params.risk_reward_ratio)
        
        # Create bracket order (entry with attached SL/TP)
        self.entry_orders = self.sell_bracket(
            size=size,
            price=self.data.close[0],  # Market order for entry
            stopprice=sl_price,       # Stop loss price
            limitprice=tp_price       # Take profit price
        )
        
        # Log the trade
        self.log(f'SHORT ENTER: Price={self.data.close[0]:.2f}, '
                f'SL={sl_price:.2f}, TP={tp_price:.2f}, Size={size}')
    
    def notify_order(self, order):
        """Called when order status changes"""
        if order.status in [order.Submitted, order.Accepted]:
            # Order submitted/accepted - do nothing
            return
            
        # Check if order is completed
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED: Price={order.executed.price:.2f}, '
                        f'Cost={order.executed.value:.2f}, '
                        f'Comm={order.executed.comm:.2f}')
            else:
                self.log(f'SELL EXECUTED: Price={order.executed.price:.2f}, '
                        f'Cost={order.executed.value:.2f}, '
                        f'Comm={order.executed.comm:.2f}')
                        
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log(f'Order {order.getstatusname()}')
        
        # Check if all orders in bracket are completed
        if self.entry_orders:
            all_completed = all(o.status in [o.Completed, o.Canceled, o.Margin, o.Rejected] 
                               for o in self.entry_orders)
            if all_completed:
                self.entry_orders = []
    
    def notify_trade(self, trade):
        """Called when trade status changes"""
        if not trade.isclosed:
            return
            
        self.log(f'TRADE PROFIT: Gross={trade.pnl:.2f}, Net={trade.pnlcomm:.2f}')
    
    def log(self, txt, dt=None):
        """Logging function"""
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')
    
    def stop(self):
        """Called when backtesting finishes"""
        print(f'\n=== Strategy Parameters ===')
        print(f'Trade Direction: {self.params.trade_direction}')
        print(f'Daily Trend Filter: {self.params.enable_daily_trend_filter}')
        print(f'Trend Mode: {self.params.trend_mode}')
        print(f'Entry Trigger: {self.params.enable_entry_trigger}')
        print(f'MA Type: {self.params.trigger_ma_type}')
        print(f'Entry Mode: {self.params.entry_mode}')
        print(f'ATR Period: {self.params.atr_length}')
        print(f'ATR Multiplier: {self.params.atr_multiplier}')
        print(f'Risk/Reward Ratio: {self.params.risk_reward_ratio}')
        print(f'Order Percent: {self.params.order_percent*100:.0f}%')