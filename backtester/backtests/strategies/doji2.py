
import backtrader as bt

class DojiAshiV2(bt.Strategy):
    """
    Simplified reversal strategy for Backtrader.
    Based on Pine Script: Doji Ashi v1.2 for Conversion

    This strategy combines a daily trend filter with a fast/slow EMA entry trigger.
    """
    params = (
        # Mode Selector
        ('trade_direction', 'Both'),  # 'Long', 'Short', 'Both'
        # Input Settings
        ('enable_daily_trend_filter', True),
        ('trend_mode', 'Strict'),  # 'Strict', 'Flexible'
        ('enable_entry_trigger', True),
        ('entry_mode', 'Above/Below'),  # 'Cross', 'Above/Below'
        # SL/TP Settings
        ('atr_length', 14),
        ('atr_multiplier', 1.5),
        ('risk_reward_ratio', 2.0),
        # Debug
        ('printlog', False),
    )

    def __init__(self):
        # Keep a reference to the "close" line in the primary data[0]
        self.dataclose = self.datas[0].close

        # --- Indicator Definitions ---
        # Primary (trading timeframe) indicators
        self.ma3 = bt.indicators.EMA(self.datas[0], period=3)
        self.ma8 = bt.indicators.EMA(self.datas[0], period=8)
        self.atr = bt.indicators.ATR(self.datas[0], period=self.p.atr_length)

        # CrossOver indicator for 'Cross' mode
        self.crossover = bt.indicators.CrossOver(self.ma3, self.ma8)

        # Daily trend filter indicators (on the secondary data feed, datas[1])
        self.daily_sma_20 = bt.indicators.SMA(self.datas[1], period=20)
        self.daily_sma_50 = bt.indicators.SMA(self.datas[1], period=50)
        self.daily_sma_200 = bt.indicators.SMA(self.datas[1], period=200)

        # To keep track of pending orders and buy price
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.sl_order = None
        self.tp_order = None

    def log(self, txt, dt=None, doprint=False):
        ''' Logging function for this strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()}, {txt}')

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm {order.executed.comm:.2f}')
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm

                # --- Place OCO (One-Cancels-Other) Exit Orders ---
                # Calculate SL/TP prices
                atr_value = self.atr[0]
                sl_price = self.buyprice - atr_value * self.p.atr_multiplier
                tp_price = self.buyprice + (self.buyprice - sl_price) * self.p.risk_reward_ratio
                
                # Sell Stop Loss
                self.sl_order = self.sell(exectype=bt.Order.Stop, price=sl_price)
                self.sl_order.addinfo(oco=True) # Mark as part of OCO
                # Sell Take Profit
                self.tp_order = self.sell(exectype=bt.Order.Limit, price=tp_price)
                self.tp_order.addinfo(oco=self.sl_order) # Link to SL order

            elif order.issell():
                self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm {order.executed.comm:.2f}')
                # For short sell, calculate SL/TP
                if self.position.size < 0: # It's a short entry
                    self.buyprice = order.executed.price # Entry price for short
                    atr_value = self.atr[0]
                    sl_price = self.buyprice + atr_value * self.p.atr_multiplier
                    tp_price = self.buyprice - (sl_price - self.buyprice) * self.p.risk_reward_ratio
                    
                    # Buy Stop Loss (to close short)
                    self.sl_order = self.buy(exectype=bt.Order.Stop, price=sl_price)
                    self.sl_order.addinfo(oco=True)
                    # Buy Take Profit (to close short)
                    self.tp_order = self.buy(exectype=bt.Order.Limit, price=tp_price)
                    self.tp_order.addinfo(oco=self.sl_order)

            # Reset order tracking
            self.order = None

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
            self.order = None # Reset order tracking

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log(f'OPERATION PROFIT, GROSS {trade.pnl:.2f}, NET {trade.pnlcomm:.2f}')

    def next(self):
        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are already in the market
        if self.position:
            return

        # --- Daily Trend Filter Logic ---
        daily_uptrend = False
        daily_downtrend = False
        if self.p.enable_daily_trend_filter:
            # Note: Backtrader aligns the data feeds automatically.
            # We can access the daily close from datas[1] directly.
            daily_close = self.datas[1].close[0]
            
            sma20_pass = daily_close > self.daily_sma_20[0]
            sma50_pass = daily_close > self.daily_sma_50[0]
            sma200_pass = daily_close > self.daily_sma_200[0]
            sma_pass_count = int(sma20_pass) + int(sma50_pass) + int(sma200_pass)

            if self.p.trend_mode == 'Strict':
                daily_uptrend = sma_pass_count == 3
                daily_downtrend = sma_pass_count == 0
            else:  # Flexible
                daily_uptrend = sma_pass_count >= 2
                daily_downtrend = sma_pass_count <= 1
        else:
            # If filter is disabled, always allow trades
            daily_uptrend = True
            daily_downtrend = True

        # --- Entry Trigger Logic ---
        trigger_long = False
        trigger_short = False
        if self.p.enable_entry_trigger:
            if self.p.entry_mode == 'Cross':
                trigger_long = self.crossover[0] > 0
                trigger_short = self.crossover[0] < 0
            else:  # Above/Below
                trigger_long = self.ma3[0] > self.ma8[0]
                trigger_short = self.ma3[0] < self.ma8[0]
        else:
            # If trigger is disabled, always allow
            trigger_long = True
            trigger_short = True

        # --- Final Setup Conditions ---
        long_conditions = daily_uptrend and trigger_long
        short_conditions = daily_downtrend and trigger_short

        # --- Strategy Execution ---
        if self.p.trade_direction in ['Long', 'Both'] and long_conditions:
            self.log(f'LONG SIGNAL: Close {self.dataclose[0]:.2f}')
            self.order = self.buy()

        elif self.p.trade_direction in ['Short', 'Both'] and short_conditions:
            self.log(f'SHORT SIGNAL: Close {self.dataclose[0]:.2f}')
            self.order = self.sell()

    def stop(self):
        self.log(f'(ATR Period {self.p.atr_length:2d}) Ending Value {self.broker.getvalue():.2f}', doprint=True)

# Example of how to run the strategy
if __name__ == '__main__':
    import pandas as pd

    cerebro = bt.Cerebro()

    # Add the strategy
    cerebro.addstrategy(DojiAshiV2, printlog=True)

    # --- Data Loading using Pandas ---
    # Define column names as per Binance API data format
    columns = ['datetime', 'open', 'high', 'low', 'close', 'volume', 
               'close_time', 'quote_asset_volume', 'number_of_trades', 
               'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore']

    # --- Load and prepare 4-hour data ---
    try:
        primary_df = pd.read_csv(
            'D:/BIGBOSS/claudecode/backtests/data/BTCUSDT/BTCUSDT_4h_merged.csv', 
            header=None, 
            names=columns
        )
        # Convert timestamp, coercing errors to NaT (Not a Time)
        primary_df['datetime'] = pd.to_datetime(primary_df['datetime'], unit='ms', errors='coerce')
        # Drop rows where the datetime conversion failed
        primary_df.dropna(subset=['datetime'], inplace=True)
        primary_df.set_index('datetime', inplace=True)
        for col in ['open', 'high', 'low', 'close', 'volume']:
            primary_df[col] = pd.to_numeric(primary_df[col])
        
        primary_data = bt.feeds.PandasData(
            dataname=primary_df,
            timeframe=bt.TimeFrame.Minutes,
            compression=240
        )
        cerebro.adddata(primary_data)
    except FileNotFoundError:
        print("Error: 4-hour data file 'BTCUSDT_4h_merged.csv' not found.")
        exit()

    # --- Load and prepare daily data ---
    try:
        daily_df = pd.read_csv(
            'D:/BIGBOSS/claudecode/backtests/data/BTCUSDT/BTCUSDT_1d_merged.csv',
            header=None,
            names=columns
        )
        # Convert timestamp, coercing errors to NaT (Not a Time)
        daily_df['datetime'] = pd.to_datetime(daily_df['datetime'], unit='ms', errors='coerce')
        # Drop rows where the datetime conversion failed
        daily_df.dropna(subset=['datetime'], inplace=True)
        daily_df.set_index('datetime', inplace=True)
        for col in ['open', 'high', 'low', 'close', 'volume']:
            daily_df[col] = pd.to_numeric(daily_df[col])

        daily_data = bt.feeds.PandasData(
            dataname=daily_df,
            timeframe=bt.TimeFrame.Days
        )
        cerebro.adddata(daily_data)
    except FileNotFoundError:
        print("Error: Daily data file 'BTCUSDT_1d_merged.csv' not found.")
        exit()


    # --- Broker Settings ---
    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0.001) # 0.1% commission
    cerebro.addsizer(bt.sizers.FixedSize, stake=10) # Trade a fixed size of 10 shares/contracts

    # --- Run the backtest ---
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # --- Plot the results ---
    cerebro.plot()
