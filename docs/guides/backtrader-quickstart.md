# Backtrader 回测环境快速入�?

## 概述

本指南将帮助你快速搭�?Backtrader 回测环境，并�?分钟内成功运行第一次回测�?

## 步骤一：检查并激活虚拟环�?

首先，确保项�?`claudecode` 目录下存�?`venv` 虚拟环境�?

�?Windows 系统中，使用以下命令激活它�?

```bash
# 激活虚拟环�?
.\claudecode\venv\Scripts\activate
```

激活成功后，你的命令行提示符前会显�?`(venv)`�?

## 步骤二：安装依赖

如果这是你第一次运行，或者依赖不完整，请运行以下命令安装所需库：

```bash
# 在激活虚拟环境后运行
pip install -r claudecode/requirements.txt
```

## 步骤三：运行 Doji Ashi 策略回测

我们提供了最新的 Doji Ashi v4 策略，具有完整的 Plotly 可视化功能�?

运行 v4 策略回测�?

```bash
# 运行最新的 Doji Ashi v4 策略
python claudecode/backtester/run_doji_ashi_strategy_v4.py \
  --data claudecode/backtester/data/ETHUSDT/2h/ETHUSDT-2h-merged.csv \
  --market_type crypto \
  --enable_plotly
```

**预期输出�?*

你将看到策略回测结果和性能指标，并在浏览器中自动打开交互式图表：

```
Strategy completed successfully
Total Return: 15.34%
Sharpe Ratio: 0.87
Max Drawdown: -8.23%
Plot saved to: claudecode/backtester/plots/doji_ashi_v4_crypto_*.html
```

## 常见问题

- **`ModuleNotFoundError: No module named 'backtrader'`**: 依赖未正确安装。请确保你已**激活虚拟环�?*并运行了 `pip install -r claudecode/requirements.txt`�?
- **`FileNotFoundError`**: 找不到数据文件。请确保 `claudecode/backtester/data/` 目录下有对应�?`.csv` 数据文件�?
- **Plotly 图表无法打开**: 检查是否安装了 `plotly` 依赖，或尝试禁用 `--enable_plotly` 参数�?

## 下一�?

恭喜你成功运行了第一次策略回测！

接下来你可以�?
1. 阅读 [Doji Ashi v4 完整指南](./strategies/dojo_ashi_strategy_v4_guide.md) 了解策略详细配置
2. 尝试不同的市场数�?(BTC, SOL �?
3. 调整策略参数进行优化
4. 学习 [Pine Script 开发标准](../standards/pine-script-standards.md) 开发自己的策略

现在，请阅读 **[Backtrader 核心架构指南](./backtrader-architecture.md)**，学习如何利用本项目的配置驱动架构来开发和管理你自己的策略�?

