# Repository Guidelines

## Project Structure & Module Organization
- `backtester/`: runnable entry points (`run_four_swords_v1_7_4.py`, `run_doji_ashi_strategy_v5.py`), strategies (`strategies/`), safe indicators (`indicators/`), utilities (`utils/`), data and local results.
- `scripts/`: data tools (e.g., `download_data.py`).
- `config/`: dependency lists (`requirements.txt`, `requirements-local.txt`).
- `docs/`: strategy notes and guides.  `plots/` and `results/`: generated HTML charts and CSV summaries.
- `pinescript/`: source TradingView scripts that inform Python strategies.

## Build, Test, and Development Commands
- Create venv: Windows `python -m venv .venv && .venv\Scripts\activate`, macOS/Linux `python3 -m venv .venv && source .venv/bin/activate`.
- Install deps: `pip install -r config/requirements.txt` (optional extras: `pip install -r config/requirements-local.txt`).
- Download data: `python scripts/download_data.py --symbol BTCUSDT --interval 4h --merge-csv` → writes under `backtester/data/<SYMBOL>/<INTERVAL>/`.
- Quick smoke test: `python backtester/test_simple_strategy.py`.
- Four Swords run (maker baseline):
  `python backtester/run_four_swords_v1_7_4.py --data backtester/data/BTCUSDT/4h/BTCUSDT-4h-merged.csv --order_style maker --limit_offset 0.0`
- Outputs: CSV summaries in `results/test_summary.csv`; charts in `plots/*.html` (+ sidecar `.meta.json`).

## Coding Style & Naming Conventions
- Python 3.x, 4‑space indentation; prefer type hints where helpful.
- Names: modules/files `snake_case.py`, functions/vars `snake_case`, classes `PascalCase`.
- Runners follow `run_*.py`; tests `test_*.py`. Keep strategy logic in `backtester/strategies`, reusable math in `backtester/utils` and indicators in `backtester/indicators`.
- Use `argparse`, `pathlib`, and safe math helpers (`utils/safe_math.py`) to avoid divide‑by‑zero.

## Testing Guidelines
- Minimal: run `backtester/test_simple_strategy.py` with a merged CSV to validate environment and data feed.
- Add small runnable `test_*.py` scripts near the code they validate; print key metrics (final equity, trades, win rate). Ensure warmup periods and zero‑division protections are respected.

## Commit & Pull Request Guidelines
- Commits: imperative, concise; English or Chinese is fine. Common prefixes: Add/Update/Fix/Refactor/Delete. Example: `Add batch backtesting for 2h and CSV summary`.
- PRs: include what/why, commands used, data path(s), before/after metrics, and a sample plot or `results` row. Link related issues. Touch only the scope you change.

## Security & Configuration Tips
- Do not commit large CSVs, credentials, or OS‑specific paths. Place raw data under `backtester/data/` (git‑ignored) and verify with `backtester/data_health_check.py`.
- Prefer safe indicators (`indicators/*_safe.py`) and `utils/safe_math.py` when adding calculations.

