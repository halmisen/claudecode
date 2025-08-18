"""
WaveTrend Safe Indicator
安全版WaveTrend指标 - 保持原有语义，仅加入分母防护

基于原始实现，只在计算ci时对0.015*d进行夹底保护
"""
import backtrader as bt
import backtrader.indicators as btind
try:
    from utils.safe_math import safe_div_line, DEFAULT_EPS
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from utils.safe_math import safe_div_line, DEFAULT_EPS


class WaveTrendSafe(bt.Indicator):
    """
    WaveTrend Oscillator - Safe Version
    
    与原版完全相同的语义和参数，仅在分母计算中加入EPS保护
    """
    lines = ('wt1', 'wt2', 'wt_signal')
    
    params = (
        ('n1', 10),  # Channel Length
        ('n2', 21),  # Average Length
        ('eps', DEFAULT_EPS),  # 分母保护阈值
        ('debug', False),  # 调试日志开关
    )
    
    plotinfo = dict(subplot=True, plotname='WaveTrend Safe')
    plotlines = dict(
        wt1=dict(color='blue'),
        wt2=dict(color='red'), 
        wt_signal=dict(color='green', _method='bar')
    )
    
    def __init__(self):
        # Typical price - 与原版相同
        self.ap = (self.data.high + self.data.low + self.data.close) / 3.0
        
        # EMA calculations - 与原版相同
        self.esa = btind.ExponentialMovingAverage(self.ap, period=self.params.n1)
        
        # Custom absolute value calculation - 与原版相同
        diff = self.ap - self.esa
        abs_diff = bt.If(diff >= 0, diff, -diff)
        self.d = btind.ExponentialMovingAverage(abs_diff, period=self.params.n1)
        
        # 关键改进：CI计算时对分母进行安全保护
        # 原版: self.ci = (self.ap - self.esa) / (0.015 * self.d)
        # 安全版: 使用safe_div_line对分母夹底
        numerator = self.ap - self.esa
        denominator = 0.015 * self.d
        self.ci = safe_div_line(numerator, denominator, self.params.eps)
        
        # TCI (True Commodity Index) - 与原版相同
        self.tci = btind.ExponentialMovingAverage(self.ci, period=self.params.n2)
        
        # WaveTrend lines - 与原版相同
        self.wt1 = self.tci
        self.wt2 = btind.SimpleMovingAverage(self.wt1, period=4)
        
        # WaveTrend signal (wt1 > wt2) - 与原版相同
        self.wt_signal = self.wt1 > self.wt2
        
        # 设置合理的warmup期 - 用户建议的n1*2+n2+5
        warmup = self.params.n1 * 2 + self.params.n2 + 5
        self.addminperiod(warmup)
        
        if self.params.debug:
            print(f"WaveTrend Safe initialized: n1={self.params.n1}, n2={self.params.n2}, "
                  f"eps={self.params.eps}, warmup={warmup}")
    
    def next(self):
        # 与原版相同的逻辑，只是使用安全计算的结果
        self.lines.wt1[0] = self.wt1[0]
        self.lines.wt2[0] = self.wt2[0]
        self.lines.wt_signal[0] = float(self.wt_signal[0])
        
        # 可选的SMOKE日志
        if self.params.debug and len(self) > self.params.n1 + 5:
            d_value = self.d[0]
            if abs(d_value) < self.params.eps * 10:  # 接近阈值时记录
                print(f"SMOKE: WaveTrend d={d_value:.2e} at bar {len(self)}")


# 兼容性别名
WaveTrendIndicator = WaveTrendSafe