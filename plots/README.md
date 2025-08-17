# Plots Directory - Backtest Results & Visualization

## 📁 Directory Structure

### Four Swords Strategy Optimization Results
- **four_swords_optimization/baseline_tests/** - A0 configuration tests (no filters)
- **four_swords_optimization/ema_optimization/** - A1 configuration tests (EMA filters)
- **four_swords_optimization/volume_optimization/** - A2 configuration tests (EMA + Volume filters)
- **four_swords_optimization/bokeh_debug/** - Bokeh plotting system development

### Archive
- **archived_tests/** - Historical test results (for future use)

## 📊 File Naming Convention

### Test Configuration Codes
- **A0_*** - Baseline tests (no additional filters)
- **A1_*** - EMA filter optimization tests  
- **A2_*** - Combined EMA + Volume filter tests

### File Types
- **.html** - Interactive Bokeh visualization files
- **.meta.json** - Test metadata and performance metrics

## 🎯 Key Results Summary

| Configuration | Trade Count | Win Rate | Total Return | Max Drawdown |
|---------------|-------------|----------|--------------|--------------|
| A0 (Baseline) | 48 trades | 64.6% | +2.92% | 0.99% |
| A1 (EMA Opt) | 22 trades | 54.5% | +2.87% | 2.10% |
| A2 (Best) | 11 trades | 72.7% | +4.36% | 1.18% |

## 📚 Related Documentation
- Signal frequency analysis: `docs/troubleshooting/four_swords/four-swords-signal-frequency-analysis.md`
- Optimization results: `docs/troubleshooting/four_swords/four-swords-optimization-results.md`
- Signal funnel summary: `docs/troubleshooting/four_swords/signal-funnel-summary.md`