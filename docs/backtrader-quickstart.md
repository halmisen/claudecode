# Backtrader 回测环境快速入门

## 概述

本指南将帮助你快速搭建 Backtrader 回测环境，并在5分钟内成功运行第一次回测。

## 步骤一：检查并激活虚拟环境

首先，确保项目根目录下存在 `venv` 虚拟环境。

在 Windows 系统中，使用以下命令激活它：

```bash
# 激活虚拟环境
.\venv\Scripts\activate
```

激活成功后，你的命令行提示符前会显示 `(venv)`。

## 步骤二：安装依赖

如果这是你第一次运行，或者依赖不完整，请运行以下命令安装所需库：

```bash
# 在激活虚拟环境后运行
pip install -r requirements.txt
```

## 步骤三：运行简单回测

我们提供了一个开箱即用的简单回测脚本 `bt_simple.py`。

进入 `backtests` 目录并运行它：

```bash
# 进入回测脚本所在目录
cd backtests

# 运行回测
python bt_simple.py
```

**预期输出：**

你将看到类似以下的输出，表明回测已成功执行：

```
Starting Portfolio Value: 10000.00
Final Portfolio Value: 9855.62
```

## 常见问题

- **`ModuleNotFoundError: No module named 'backtrader'`**: 依赖未正确安装。请确保你已**激活虚拟环境**并运行了 `pip install -r requirements.txt`。
- **`FileNotFoundError`**: 找不到数据文件。请确保 `backtests/data` 目录下有 `.csv` 数据文件。

## 下一步

恭喜你成功运行了第一次回测！

现在，请阅读 **[Backtrader 核心架构指南](./backtrader-architecture-guide.md)**，学习如何利用本项目的配置驱动架构来开发和管理你自己的策略。
