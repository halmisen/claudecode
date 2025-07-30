# 框架迁移文件组织计划

## 📂 推荐目录结构

```
KFC/
├── program/                    # 保留，归档旧代码
│   ├── data/                  # 保留 - 数据文件通用
│   ├── indicators/            # 保留 - 技术指标兼容VectorBT
│   ├── utils/                 # 保留 - 工具函数通用
│   └── archive/               # 新建 - 归档backtesting.py文件
│       ├── strategies/
│       ├── validate_strategy.py
│       └── framework_*.py
│
├── vectorbt_backtest/         # 新建 - VectorBT框架
│   ├── strategies/            # VectorBT策略实现
│   ├── indicators/            # VectorBT专用指标
│   ├── utils/                 # VectorBT工具函数
│   ├── notebooks/            # Jupyter笔记本分析
│   ├── results/               # 回测结果
│   └── config/                # 配置文件
│
├── jesse_backtest/            # 新建 - JESSE框架
│   ├── strategies/            # JESSE策略实现
│   ├── indicators/            # JESSE专用指标
│   ├── utils/                 # JESSE工具函数
│   ├── config/                # JESSE配置
│   └── logs/                  # 日志文件
│
└── shared/                    # 新建 - 共享资源
    ├── data/                  # 共享数据文件
    └── common_utils/         # 通用工具函数
```

## 🔄 文件迁移计划

### Phase 1: 清理和归档
1. 将 `program/` 中的 backtesting.py 相关文件移至 `program/archive/`
2. 保留 `data/`, `indicators/`, `utils/` 目录

### Phase 2: 创建 VectorBT 环境
1. 创建 `vectorbt_backtest/` 目录结构
2. 将兼容的文件复制到相应位置
3. 实现 VectorBT 版本的 SQZMOM 策略

### Phase 3: 创建 JESSE 环境
1. 创建 `jesse_backtest/` 目录结构
2. 按照 JESSE 框架要求重构策略
3. 配置 JESSE 运行环境

## 📋 具体操作清单

### 立即可删除的文件：
- `debug_backtest.py`
- `extended_framework_analysis.py`
- `framework_analysis.py`
- `framework_final_analysis.py`
- `run_backtest.py`
- `run_real_sqzmom.py`
- `simplified_backtest.py`
- `validate_strategy.py`

### 需要归档的文件：
- `strategies/sqzmom_wavetrend_strategy.py`

### 可以保留的文件：
- `data/` 目录（全部）
- `indicators/technical_indicators.py`
- `utils/data_utils.py`
- `data/fetch_data.py`
- `requirements.txt`（需要更新依赖）

## 🎯 下一步行动

1. **立即清理** - 删除不需要的文件
2. **创建目录结构** - 按照推荐结构创建新目录
3. **安装 VectorBT** - 在新环境中安装框架
4. **迁移策略** - 将现有指标和策略逻辑迁移到 VectorBT

这样的组织结构能够：
- 保持代码整洁和模块化
- 避免框架之间的冲突
- 便于维护和扩展
- 支持多个框架并行开发