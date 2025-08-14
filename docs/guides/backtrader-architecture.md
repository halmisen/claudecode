# Backtrader 核心架构指南

## 概述

欢迎来到本项目的核心开发工作流。本文档将介绍我们独特的**配置驱动**回测架构，它能让你无需为每个策略创建单独的Python文件，从而极大地提升开发效率�?

阅读本指南前，请确保你已完成 **[Backtrader 快速入门](./backtrader-quickstart.md)**�?

## 🏗�?系统架构

我们的回测系统由以下几个核心组件构成�?

```
backtester/
├── strategies/            # 单独策略文件（或统一策略库）
├── run_*.py               # 简单策略运行入口（示例�?
└── data/                  # CSV数据文件
```

- **`config.py`**: 所有策略的参数都在这里统一配置。我们通过修改这个文件来选择运行哪个策略、调整其参数�?
- **`strategies.py`**: 所有策略的逻辑代码都存放在这个文件中。每个策略都是一个独立的Python类�?
- **`main.py`**: 这是回测的入口点。它会读取配置，加载相应的策略和数据，然后执行回测�?

## 🚀 如何添加并运行一个新策略

这是你最常用的开发流程。按照以下四步操作：

### 第一步：�?`strategies.py` 中定义策略逻辑

�?`backtester/strategies/` 下新增策略类文件（或集中到一个库文件）。它必须继承�?`backtrader.Strategy`�?

**示例：添加一个RSI策略**
```python
# backtester/strategies/your_strategy.py

# ... (已有代码) ...

class RSIStrategy(bt.Strategy):
    """RSI策略示例"""
    params = (
        ('rsi_period', 14),
        ('upper_band', 70),
        ('lower_band', 30),
    )

    def __init__(self):
        self.rsi = bt.indicators.RSI_SMA(self.data.close, period=self.p.rsi_period)

    def next(self):
        if not self.position:
            if self.rsi < self.p.lower_band:
                self.buy()
        else:
            if self.rsi > self.p.upper_band:
                self.sell()
```

### 第二步：�?`config.py` 中添加策略配�?

（若采用集中式配置）打开对应配置文件，添加你的新策略配置；或在运行脚本里直接传参�?

- `key` (例如 `'rsi_70_30'`) 是你将用来调用该策略的唯一ID�?
- `'class'` 的值必须与你在 `strategies.py` 中定义的类名完全一致�?
- `'params'` 字典用于覆盖策略中定义的默认参数�?

**示例：配置RSI策略**
```python
# backtester/config/config.py (可�?

STRATEGY_CONFIGS = {
    # ... (已有配置) ...
    'rsi_70_30': {
        'class': 'RSIStrategy',
        'params': {
            'rsi_period': 14,
            'upper_band': 70,
            'lower_band': 30,
        },
        'description': '一个标准的RSI策略'
    },
}
```

### 第三步：�?`main.py` 中指定要运行的策�?

在运行脚�?`run_*.py` 中选择要运行的策略类，或通过命令行参数指定�?

```python
# backtester/run_your_strategy.py

# ... (已有代码) ...

# ==================================================
# 1. 选择要运行的策略ID
# ==================================================
STRATEGY_TO_RUN = 'rsi_70_30'

# ... (其余代码) ...
```

### 第四步：运行回测

回到命令行，确保你位于项目根目录下，然后运行示例回测脚本�?

```bash
python claudecode/backtester/run_doji_ashi_strategy_v2.py
```

系统将自动加�?`RSIStrategy`，应�?`rsi_70_30` 配置，并输出回测结果�?

## ⚙️ 参数与高级配�?

本架构支持丰富的参数配置。关于每个参数（如手续费、数据时间框架、分析器等）的详细用法，请查阅我们的 **[Backtrader 参数参考手册](./backtrader-parameters.md)**�?

通过组合 `config.py` 中的不同参数，你可以轻松实现�?
- **批量运行和比较策�?*
- **参数优化**
- **使用不同的经纪商和数据配�?*

## 总结

这个架构的优势在于：
- **关注点分�?*: 策略逻辑 (`strategies.py`) 和参数配�?(`config.py`) 完全分开�?
- **易于管理**: 所有策略和配置都在固定的地方，一目了然�?
- **高效迭代**: 你可以通过修改配置，快速测试同一策略的不同参数版本，而无需改动任何逻辑代码�?

