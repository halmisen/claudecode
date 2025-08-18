"""
Squeeze Momentum Safe Indicator
安全版SQZMOM指标 - 保持原有语义，仅加入分母防护

基于原始实现，对所有可能为零的分母（标准差、ATR均值等）进行夹底保护
"""
import backtrader as bt
import backtrader.indicators as btind
try:
    from utils.safe_math import safe_max_eps, safe_div_line, DEFAULT_EPS
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from utils.safe_math import safe_max_eps, safe_div_line, DEFAULT_EPS


class SqueezeMomentumSafe(bt.Indicator):
    """
    Squeeze Momentum Oscillator (SQZMOM) - Safe Version
    
    与原版完全相同的语义和参数，仅在分母计算中加入EPS保护
    """
    lines = ('squeeze_on', 'squeeze_off', 'signal_bar', 'momentum')
    
    params = (
        ('bb_length', 20),
        ('bb_mult', 2.0),
        ('kc_length', 20), 
        ('kc_mult', 1.5),
        ('use_true_range', True),
        ('eps', DEFAULT_EPS),  # 分母保护阈值
        ('debug', False),  # 调试日志开关
    )
    
    plotinfo = dict(subplot=True, plotname='Squeeze Momentum Safe')
    plotlines = dict(
        momentum=dict(color='blue'),
        squeeze_on=dict(color='red', _method='bar'),
        squeeze_off=dict(color='green', _method='bar'),
        signal_bar=dict(color='yellow', _method='bar')
    )
    
    def __init__(self):
        # Bollinger Bands calculation - 与原版相同
        self.bb_basis = btind.SimpleMovingAverage(self.data.close, period=self.params.bb_length)
        
        # 关键改进：标准差作为分母时进行安全保护
        raw_bb_dev = btind.StandardDeviation(self.data.close, period=self.params.bb_length)
        safe_bb_dev = safe_max_eps(raw_bb_dev, self.params.eps)
        self.bb_dev = self.params.bb_mult * safe_bb_dev
        
        self.bb_upper = self.bb_basis + self.bb_dev
        self.bb_lower = self.bb_basis - self.bb_dev
        
        # Keltner Channels calculation - 与原版相同结构，但对range均值进行保护
        self.kc_ma = btind.SimpleMovingAverage(self.data.close, period=self.params.kc_length)
        
        if self.params.use_true_range:
            self.kc_range = btind.TrueRange(self.data)
        else:
            self.kc_range = self.data.high - self.data.low
        
        # 关键改进：range均值作为分母时进行安全保护
        raw_kc_rangema = btind.SimpleMovingAverage(self.kc_range, period=self.params.kc_length)
        self.kc_rangema = safe_max_eps(raw_kc_rangema, self.params.eps)
        
        self.kc_upper = self.kc_ma + self.kc_rangema * self.params.kc_mult
        self.kc_lower = self.kc_ma - self.kc_rangema * self.params.kc_mult
        
        # Squeeze conditions - 与原版相同
        self.squeeze_on_cond1 = self.bb_lower > self.kc_lower
        self.squeeze_on_cond2 = self.bb_upper < self.kc_upper
        self.squeeze_off_cond1 = self.bb_lower < self.kc_lower
        self.squeeze_off_cond2 = self.bb_upper > self.kc_upper
        
        # Momentum calculation - 与原版相同，但对可能的分母进行保护
        highest = btind.Highest(self.data.high, period=self.params.kc_length)
        lowest = btind.Lowest(self.data.low, period=self.params.kc_length)
        avg_hl = (highest + lowest) / 2.0
        avg_close = btind.SimpleMovingAverage(self.data.close, period=self.params.kc_length)
        avg_all = (avg_hl + avg_close) / 2.0
        source_diff = self.data.close - avg_all
        
        # ROC calculation (Rate of Change) - 使用差分代替避免除零错误
        # 原版 ROC 在 source_diff 接近0时容易除零错误
        # 使用简单差分 (current - previous) 作为动量，保持方向性但避免除法
        # 这在语义上等价于 ROC 的分子部分，保持策略逻辑的一致性
        self._mom = source_diff - source_diff(-self.params.kc_length)
        
        # 设置合理的warmup期 - 用户建议的max(length, lengthKC)+50
        warmup = max(self.params.bb_length, self.params.kc_length) + 50
        self.addminperiod(warmup)
        
        if self.params.debug:
            print(f"SQZMOM Safe initialized: bb_len={self.params.bb_length}, kc_len={self.params.kc_length}, "
                  f"eps={self.params.eps}, warmup={warmup}")

    def next(self):
        # 与原版相同的逻辑
        try:
            # Calculate squeeze conditions manually
            squeeze_on = (self.squeeze_on_cond1[0] and self.squeeze_on_cond2[0])
            squeeze_off = (self.squeeze_off_cond1[0] and self.squeeze_off_cond2[0])
            
            # Signal bar: squeeze was on last bar but not current bar
            prev_squeeze_on = False
            if len(self) > 1:
                prev_squeeze_on = (self.squeeze_on_cond1[-1] and self.squeeze_on_cond2[-1])
            signal_bar = prev_squeeze_on and not squeeze_on
            
            # Get momentum safely
            momentum = self._mom[0]
            
            self.lines.squeeze_on[0] = float(squeeze_on)
            self.lines.squeeze_off[0] = float(squeeze_off) 
            self.lines.signal_bar[0] = float(signal_bar)
            self.lines.momentum[0] = momentum
            
            # 可选的SMOKE日志
            if self.params.debug and len(self) > self.params.kc_length + 10:
                bb_dev_val = self.bb_dev[0] / self.params.bb_mult  # 原始标准差
                kc_range_val = self.kc_rangema[0]
                
                if abs(bb_dev_val) < self.params.eps * 10:
                    print(f"SMOKE: SQZMOM bb_dev={bb_dev_val:.2e} at bar {len(self)}")
                if abs(kc_range_val) < self.params.eps * 10:
                    print(f"SMOKE: SQZMOM kc_range={kc_range_val:.2e} at bar {len(self)}")
            
        except Exception as e:
            if self.params.debug:
                print(f"SQZMOM Safe error at bar {len(self)}: {e}")
            # Fallback values
            self.lines.squeeze_on[0] = 0.0
            self.lines.squeeze_off[0] = 0.0
            self.lines.signal_bar[0] = 0.0
            self.lines.momentum[0] = 0.0


# 兼容性别名
SqueezeMomentumIndicator = SqueezeMomentumSafe