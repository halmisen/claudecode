"""
Safe Math Utilities for Backtrader
分母防守基础模块 - 解决ZeroDivisionError的工程级方案

不改变策略思想，仅在数学运算层面加入安全防护
"""
import backtrader as bt
import math

# 默认安全阈值 - 可参数化
DEFAULT_EPS = 1e-12


def safe_div_line(numerator, denominator, eps=DEFAULT_EPS):
    """
    Backtrader Lines安全除法
    对分母进行夹底保护：Max(denominator, eps)
    
    Args:
        numerator: Backtrader线或数值
        denominator: Backtrader线或数值 
        eps: 最小分母阈值
    
    Returns:
        Backtrader运算结果
    """
    safe_denominator = bt.Max(denominator, eps)
    return numerator / safe_denominator


def safe_max_eps(line, eps=DEFAULT_EPS):
    """
    将任意用于分母的Lines夹到不小于EPS
    
    Args:
        line: Backtrader线
        eps: 最小阈值
    
    Returns:
        经过夹底保护的Backtrader线
    """
    return bt.Max(line, eps)


def safe_div(numerator, denominator, eps=DEFAULT_EPS):
    """
    标量版安全除法，供非Lines计算使用
    
    Args:
        numerator: 分子（数值）
        denominator: 分母（数值）
        eps: 最小分母阈值
    
    Returns:
        安全的除法结果
    """
    if denominator is None:
        return 0.0
    
    # 检查无效值
    if math.isnan(denominator) or math.isinf(denominator):
        return 0.0
    
    # 分母夹底保护
    if abs(denominator) < eps:
        denominator = eps if denominator >= 0 else -eps
    
    try:
        result = numerator / denominator
        # 检查结果有效性
        if math.isnan(result) or math.isinf(result):
            return 0.0
        return result
    except (ZeroDivisionError, OverflowError):
        return 0.0


def check_denominator_health(value, name="denominator", eps=DEFAULT_EPS, debug=False):
    """
    检查分母健康度，可选打印SMOKE日志
    
    Args:
        value: 待检查的值
        name: 分母名称（用于日志）
        eps: 阈值
        debug: 是否开启调试日志
    
    Returns:
        bool: 分母是否健康
    """
    if value is None:
        if debug:
            print(f"SMOKE: {name} is None")
        return False
    
    if math.isnan(value) or math.isinf(value):
        if debug:
            print(f"SMOKE: {name} is NaN/Inf: {value}")
        return False
    
    if abs(value) < eps:
        if debug:
            print(f"SMOKE: {name} too small: {value} < {eps}")
        return False
    
    return True


class SafeMathMixin:
    """
    安全数学运算混入类
    可被策略或指标继承，提供统一的安全运算接口
    """
    
    def __init__(self, eps=DEFAULT_EPS, debug=False):
        self.eps = eps
        self.debug = debug
    
    def safe_divide(self, num, den, fallback=0.0):
        """安全除法（标量版）"""
        if not check_denominator_health(den, "denominator", self.eps, self.debug):
            return fallback
        return safe_div(num, den, self.eps)
    
    def safe_divide_lines(self, num, den):
        """安全除法（Lines版）"""
        return safe_div_line(num, den, self.eps)
    
    def protect_denominator(self, line):
        """保护分母Lines"""
        return safe_max_eps(line, self.eps)


# 预设的安全常量
SAFE_EPS_STANDARD = 1e-12      # 标准精度
SAFE_EPS_RELAXED = 1e-10       # 宽松精度
SAFE_EPS_STRICT = 1e-15        # 严格精度

# 导出接口
__all__ = [
    'safe_div_line',
    'safe_max_eps', 
    'safe_div',
    'check_denominator_health',
    'SafeMathMixin',
    'DEFAULT_EPS',
    'SAFE_EPS_STANDARD',
    'SAFE_EPS_RELAXED',
    'SAFE_EPS_STRICT'
]