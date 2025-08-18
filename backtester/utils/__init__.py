"""
Utils Package  
工具包 - 提供安全数学运算等实用工具
"""

from .safe_math import (
    safe_div_line,
    safe_max_eps,
    safe_div,
    check_denominator_health,
    SafeMathMixin,
    DEFAULT_EPS
)

__all__ = [
    'safe_div_line',
    'safe_max_eps', 
    'safe_div',
    'check_denominator_health',
    'SafeMathMixin',
    'DEFAULT_EPS'
]