# GEMINI_NOTES — gemini酱的小本本 ✨

> 这里是 gemini酱的专属笔记，用于记录会话要点、决定、默认参数与 TODO。
> 存放于仓库根目录，方便同步到 GitHub。

---

## 2025-08-14
- 心情：元气满满！(๑•̀ㅂ•́)و✧
- 主题：初始化专属笔记与持久化约定

### TODO
- [ ] 与主人确认：默认执行模式为 预演(P) / 步进(S) / 直接(D)
- [x] 约定：每次会话结束时把摘要自动追加到这里
- [ ] 如果需要长期结构化状态，考虑在 `logs/gemini_state.json` 保留偏好项（仅在你同意时创建）

### 决定(Decisions)
- 在你的授权下，gemini酱可以向根目录的本文件追加会话记录，不触碰核心源码与关键文档。
- 默认执行模式：预演 (P)。如需切换，支持步进 (S) 或 直接 (D)。

### 默认参数(Defaults)
- 待定（按照你的喜好填写：常用数据路径、默认回测参数、可视化开关…）

### CLAUDE.md 精华摘记 (Brief)
- 平台与命令：Windows 11 优先；使用 PowerShell/CMD；Python 采用 venv。
- 当前主力：Four Swords Swing Strategy v1.4 → `pinescript/strategies/oscillator/Four_Swords_Swing_Strategy_v1_4.pine`。
- 推荐执行：V5 Backtrader + Bokeh 可视化；V4 Plotly 已归档参考。
- 开发流水线：Pine Script → Python 策略 `backtester/strategies/` → 运行器 `backtester/run_*.py`。
- 数据规范：`backtester/data/[SYMBOL]/[INTERVAL]/{zips,csv,merged}`；OHLCV 完整；时间索引标准化、去重排序。
- 依赖分层：必需 backtrader/pandas/numpy；可选 TA-Lib/plotly-resampler；策略内以 `HAS_*` 守卫降级。
- 常用命令：激活 venv、安装依赖、运行 `backtester/run_doji_ashi_strategy_v5.py`、用 `scripts/download_data.py` 拉取与合并数据。

### 今日会话摘要
- 创建根目录专属笔记 `GEMINI_NOTES.md` 并启用“自动追加会话摘要”。
- 记录默认执行模式为 预演(P)；可随时切换 S/D。
- 已添加 `CLAUDE.md` 的精华摘记，后续可按需扩展。

### 参考(References)
- `CLAUDE_GEMINI_MEGA_COLLABORATION_EXECUTION_MASTER_DOCUMENT.md`
- `GEMINI.md`
- `CLAUDE.md`

---

## 使用约定
- 本笔记用于轻量记录与 TODO，不代替权威执行记录；正式结果仍追加到 `CLAUDE_GEMINI_...md` 的 `results/errors` 区块。
- 若你说“记一下”，gemini酱会把要点追加到当天块的【决定】或【TODO】中。

