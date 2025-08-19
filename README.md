# 加密货币交易策略回测系统

基于 Backtrader 的多策略回测与可视化工具集，配套 TradingView Pine 脚本与数据下载工具。当前主力 Python 运行器为 Four Swords v1.7.4 与 Doji Ashi v5。

## 快速开始

- 创建虚拟环境: Windows `python -m venv .venv && .venv\Scripts\activate`，macOS/Linux `python3 -m venv .venv && source .venv/bin/activate`
- 安装依赖: `pip install -r config/requirements.txt`（可选本地增强 `pip install -r config/requirements-local.txt`）
- 下载数据: `python scripts/download_data.py --symbol BTCUSDT --interval 4h --merge-csv` → 生成 `backtester/data/<SYMBOL>/<INTERVAL>/`
- 冒烟测试: `python backtester/test_simple_strategy.py`（需要已合并 CSV）

## 运行示例

- Four Swords v1.7.4（Maker 基线）
  - `python backtester/run_four_swords_v1_7_4.py --data backtester/data/BTCUSDT/4h/BTCUSDT-4h-merged.csv --order_style maker --limit_offset 0.0`
  - 输出: 汇总 CSV 写入 `results/test_summary.csv`；若提供 `--html plots/xxx.html` 则保存交互图至 `plots/`

- Doji Ashi v5（内置绘图）
  - `python backtester/run_doji_ashi_strategy_v5.py --data backtester/data/ETHUSDT/2h/ETHUSDT-2h-merged.csv --market_type crypto --enable_backtrader_plot`
  - 若安装 `backtrader-plotting`，保存至 `plots/doji_ashi_v5_bokeh_*.html`

- 2h 批量回测脚本（并行）
  - `python scripts/batch_backtest_2h.py`
  - 该脚本以 `cwd="backtester"` 调用运行器，结果统一写至顶层 `results/2h_comprehensive_backtest/`

- SQZMOM 专项调试（安全）
  - `python backtester/run_sqzmom_debug.py`

## 输出与产物

- 汇总 CSV: 顶层 `results/`（默认 `results/test_summary.csv`）
- 交互图 HTML: 顶层 `plots/`（伴随生成 `.meta.json` 时保存在同一路径）
- 产物已经在 `.gitignore` 中忽略：`results/**` 与 `plots/**`（保留 `.gitkeep` 占位）

## 项目结构（要点）

- `backtester/`: 运行入口（`run_*.py`）、策略（`strategies/`）、指标（`indicators/`）、工具（`utils/`）、本地数据。
- `scripts/`: 数据工具与批量脚本（例如 `download_data.py`、`batch_backtest_2h.py`）。
- `config/`: 依赖清单（`requirements*.txt`）。
- `docs/`: 指南、工作流与标准；`docs/guides/backtrader-help.md` 等。
- `plots/`、`results/`: 运行产物目录（已忽略版本控制）。
- `pinescript/`: TradingView 脚本源文件。

## 开发与测试建议

- 使用 `argparse` + `pathlib` 管理路径；避免写入 `backtester/results/`，统一写顶层 `results/`。
- 指标与数学计算使用 `backtester/indicators/*_safe.py` 与 `backtester/utils/safe_math.py`，避免零除等错误。
- 最小验证：`python backtester/test_simple_strategy.py`；必要时补充小型 `test_*.py` 打印关键指标（收益、交易数、胜率）。

## 文档与资源

- `CLAUDE.md`、`AGENTS.md`：开发者与代理工作流指南。
- `docs/guides/backtrader-help.md`：Backtrader 逐仓杠杆与仓位实践。
- `docs/workflows/*.md`：多文件输出、任务统计、工具生成、监控等工作流文档。

—— 专注稳定、可复现实验与统一产出路径，便于持续评估与对比。
