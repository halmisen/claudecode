# 优化建议与项目结构建议（ChatGPT/Codex CLI 适配）

> 面向本仓库的结构盘点与可执行的改进建议，结合“Repository Guidelines”。本文件仅提供建议与迁移步骤，未实际移动文件或改代码。

## 进度更新（2025-08-19 晚）

已按“低风险、可回滚”的范围完成首轮整理：
- 移动脚本与重命名
  - `batch_backtest_2h.py` → `scripts/batch_backtest_2h.py`
  - `backtester/debug_sqzmom_only.py` → `backtester/run_sqzmom_debug.py`
- 文档归档与命名统一
  - `backtrader_HELP.MD` → `docs/guides/backtrader-help.md`
  - `test.Multi-File System.md` → `docs/workflows/multi-file-system.md`
  - `test.Task Stats.md` → `docs/workflows/task-stats.md`
  - `test.Tool Maker.md` → `docs/workflows/tool-maker.md`
  - `test.Watch Control.md` → `docs/workflows/watch-control.md`
- 产物与忽略策略
  - `.gitignore` 新增忽略顶层 `results/**`、`plots/**`（保留 `.gitkeep`）；同时忽略 `backtester/results/**`
  - 新增 `results/.gitkeep`、`plots/.gitkeep`
- 使用文档
  - 更新 `README.md`：统一使用示例与输出路径，补充冒烟测试与批量 2h 回测说明

待办与后续建议：
- 输出路径一致性确认（代码侧）
  - `backtester/run_four_swords_v1_7_4.py`：默认 `--summary_csv results/test_summary.csv`（已符合）
  - 其余 `run_*.py` 与 `test_*.py`：如有写入文件，确保统一至顶层 `results/` 与 `plots/`
- 数据策略：是否从版本控制移除 `backtester/data/**`（当前保持不动）。若决定移除，需：
  - 完善 `scripts/download_data.py` 文档与校验脚本
  - 在 `docs/` 补充数据获取与健康检查流程
- 可选：在 `docs/README.md` 增加“历史版本/弃用目录”说明，标注 `backtester/deprecated_v1_7_4/`
- 可选：增加一个最小化 CI 脚本（仅做路径与文件存在性检查，不跑重回测）

## 项目结构现状与建议（2025-08-19）

### 结构扫描（摘要）
- 顶层：`backtester/`、`scripts/`、`config/`、`docs/`、`pinescript/`、`plots/`、`results/`、`.claude/`、多份辅助文档与测试说明。
- 运行入口：`backtester/run_doji_ashi_strategy_v5.py`、`backtester/run_four_swords_v1_7_4.py`、`backtester/run_four_swords_simple_safe.py`（符合 `run_*.py`）。
- 策略/指标/工具：`backtester/strategies/`、`backtester/indicators/`、`backtester/utils/`（符合约定）。
- 历史/弃用：`backtester/deprecated_v1_7_4/`（含旧版 runner 与策略）。
- 数据：大量 CSV 存于 `backtester/data/**`（与“勿提交大型 CSV”规范冲突）。
- 结果：`results/**` 目录存在；另有 `backtester/results/test_summary.csv`（位置不规范）。
- 其他：顶层存在 `batch_backtest_2h.py`、`backtrader_HELP.MD`、`test.*.md`、`test_results/`；`backtester/venv/` 与 `__pycache__` 目录被纳入版本库（应忽略）。

### 发现问题
- 数据管理：已提交大量 `backtester/data/**` CSV 文件，建议改为本地生成并 `.gitignore` 忽略。
- 结果路径：`backtester/results/test_summary.csv` 不符合“输出统一到顶层 `results/`”的约定。
- 可执行入口分布：`batch_backtest_2h.py` 位于仓库根目录，建议统一到 `scripts/`（批量/工具）或 `backtester/`（单回测入口）。
- 文档分布：`backtrader_HELP.MD`、`test.*.md` 建议并入 `docs/`（如 `docs/guides/`、`docs/workflows/`）。
- 产物与环境：`backtester/venv/`、`__pycache__` 被纳入仓库，应从版本控制移除并在 `.gitignore` 忽略。
- 调试脚本命名：`backtester/debug_sqzmom_only.py` 命名不统一，建议 `run_sqzmom_debug.py` 或迁入 `backtester/test_*.py` 体系。

### 调整建议（不改逻辑，仅路径与命名）
- 数据与版本控制
  - 按当前需求：保留 `backtester/data/**` CSV 在版本控制中（不添加忽略）。
  - 建议：在 `scripts/` 增加数据校验/去重工具，控制仓库体积（如只保留合并文件与近年区间，或将月度明细放入 `data/<SYMBOL>/<INTERVAL>/csv/` 子目录，现状已符合）。
  - 如需差异同步：建议维护 `scripts/data_manifest.json` 作为数据索引（文件名、SHA256、行数、起止时间），提升可追溯性。
- 输出与结果
  - 将所有回测输出统一到顶层 `results/` 与 `plots/`，移除 `backtester/results/` 实际使用；代码层面将默认输出路径更改为 `results/test_summary.csv`。
- 入口与脚本
  - 将 `batch_backtest_2h.py` 移至 `scripts/` 并重命名为 `scripts/batch_backtest_2h.py`（保留名不变但归类到脚本目录）。
  - 将 `backtester/debug_sqzmom_only.py` 重命名为 `backtester/run_sqzmom_debug.py`（与 `run_*.py` 统一）。
- 文档归档
  - 将 `backtrader_HELP.MD` 移至 `docs/guides/backtrader-help.md`。
  - 将 `test.Multi-File System.md`、`test.Task Stats.md`、`test.Tool Maker.md`、`test.Watch Control.md` 移至 `docs/workflows/`，按主题重命名为更清晰的工作流文档。
- 弃用版本
  - 保留 `backtester/deprecated_v1_7_4/`，在 `docs/README.md` 添加“历史版本”说明与迁移指引链接。

### 迁移步骤（建议的安全顺序）
1) 清理并忽略非源码产物
   - 从版本控制移除：`backtester/venv/`、`**/__pycache__/`、`backtester/results/**`、所有 CSV（数据应由下载脚本重建）。
   - 更新 `.gitignore`，确保上述路径被忽略；保留 `.env.example`，避免提交真实 `.env`。
2) 统一输出路径
   - 搜索代码中写入 `backtester/results/` 的位置，改为写入顶层 `results/`。
   - 确保图表输出到 `plots/*.html`，并生成 `.meta.json` 伴随文件。
3) 归档脚本与文档
   - 移动 `batch_backtest_2h.py` → `scripts/batch_backtest_2h.py`。
   - 移动与重命名文档至 `docs/guides/` 或 `docs/workflows/`；更新 README 中的链接。
4) 命名统一
   - 将 `backtester/debug_sqzmom_only.py` → `backtester/run_sqzmom_debug.py`（或合并到 `test_*.py`）。
5) 历史版本标注
   - 在 `docs/` 添加“版本对照与迁移”小节，指明 `deprecated_v1_7_4` 与 `run_four_swords_v1_7_4.py` 的关系与当前推荐入口。

### 可能需修改的代码位置（待确认）
- 写路径的模块：`backtester/utils/plotly_bt.py`（图表输出）、各 `run_*.py`（CSV/结果路径）。
- 测试脚本：`backtester/test_*.py` 若写文件路径，应与新目录对齐。

### 不执行但可复制的辅助命令（示例）
- 移动批量回测脚本（Bash/PowerShell）：
  - Bash: `git mv batch_backtest_2h.py scripts/batch_backtest_2h.py`
  - PowerShell: `git mv .\batch_backtest_2h.py .\scripts\batch_backtest_2h.py`
- 移动与重命名帮助文档：
  - Bash: `git mv backtrader_HELP.MD docs/guides/backtrader-help.md`
  - PowerShell: `git mv .\backtrader_HELP.MD .\docs\guides\backtrader-help.md`
- 清理与忽略产物（示例 .gitignore 片段）：
  - `backtester/data/`
  - `results/*.csv`
  - `plots/**/*.html`
  - `**/__pycache__/`
  - `backtester/venv/`
  - `.venv/`

### 验证清单（迁移后快速自检）
- `python backtester/test_simple_strategy.py` 能在无数据时给出明确提示；下载后能成功跑通并将输出写入 `results/` 与 `plots/`。
- `python scripts/download_data.py --symbol BTCUSDT --interval 4h --merge-csv` 正确在 `backtester/data/<SYMBOL>/<INTERVAL>/` 生成合并文件（但不提交）。
- `python backtester/run_four_swords_v1_7_4.py --data backtester/data/BTCUSDT/4h/BTCUSDT-4h-merged.csv --order_style maker --limit_offset 0.0` 正常运行，生成统一位置的 CSV 与 HTML。
