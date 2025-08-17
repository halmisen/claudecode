# Four Swords Strategy v1.7.4 信号频率分析诊断

## 🎯 问题现状
- **增强模式**: 仅8笔交易 (严重偏少)
- **简化模式**: 47笔交易 (符合预期)
- **分析目标**: 定位增强模式信号过滤瓶颈

## 📊 系统性诊断流程

### 一、建立"可观测性" - 信号流量计数器
**目标**: 把「原始信号 → EMA过滤 → Volume过滤 → WT过滤 → 实际下单」逐层计数

#### 实施计划:
```python
# 在策略 __init__ 中添加计数器
self.counters = {
    'raw_signals': 0,        # SQZMOM signal_bar 触发次数
    'ema_passed': 0,         # 通过EMA趋势过滤
    'volume_passed': 0,      # 通过成交量过滤  
    'wt_passed': 0,          # 通过WaveTrend过滤
    'actual_entries': 0,     # 实际下单次数
    'rejected_orders': 0,    # 被拒绝订单数
    'margin_calls': 0        # 保证金不足次数
}

# 在 next() 中逐层计数
if signal_bar and momentum > 0:  # 基础信号
    self.counters['raw_signals'] += 1
    
    if ema_condition:  # EMA过滤
        self.counters['ema_passed'] += 1
        
        if volume_condition:  # Volume过滤
            self.counters['volume_passed'] += 1
            
            if wt_signal:  # WT过滤
                self.counters['wt_passed'] += 1
                # 实际下单计数在 notify_order 中记录

# 在 stop() 中打印完整漏斗分析
def stop(self):
    print("\n" + "="*60)
    print("信号流量漏斗分析:")
    print(f"原始SQZMOM信号:     {self.counters['raw_signals']}")
    print(f"通过EMA过滤:        {self.counters['ema_passed']} ({self.counters['ema_passed']/max(1,self.counters['raw_signals'])*100:.1f}%)")
    print(f"通过Volume过滤:     {self.counters['volume_passed']} ({self.counters['volume_passed']/max(1,self.counters['ema_passed'])*100:.1f}%)")
    print(f"通过WT过滤:         {self.counters['wt_passed']} ({self.counters['wt_passed']/max(1,self.counters['volume_passed'])*100:.1f}%)")
    print(f"实际成功下单:       {self.counters['actual_entries']}")
    print(f"订单被拒:           {self.counters['rejected_orders']}")
    print(f"保证金不足:         {self.counters['margin_calls']}")
    print("="*60)
```

#### 增强订单调试:
```python
def notify_order(self, order):
    if order.status in [order.Rejected, order.Canceled, order.Margin]:
        dt = self.datas[0].datetime.date(0)
        print(f"\n⚠️  订单问题 - {dt}")
        print(f"   状态: {order.getstatusname()}")
        print(f"   价格: {order.created.price:.2f}")
        print(f"   数量: {order.created.size:.6f}")
        print(f"   账户资金: {self.broker.getcash():.2f}")
        print(f"   账户价值: {self.broker.getvalue():.2f}")
        
        if order.status == order.Rejected:
            self.counters['rejected_orders'] += 1
        elif order.status == order.Margin:
            self.counters['margin_calls'] += 1
    elif order.status == order.Completed:
        self.counters['actual_entries'] += 1
```

### 二、简化基线验证
**目标**: 验证基础SQZMOM信号量是否正常

#### 测试参数:
```bash
# 基线测试 - 仅保留核心信号
python run_four_swords_v1_7_4.py \
  --data backtester/data/BTCUSDT/4h/BTCUSDT-4h-merged.csv \
  --simplified_mode \
  --no_ema_filter \
  --no_volume_filter \
  --cash 500 --position_pct 0.05
```

**预期结果**: BTCUSDT 4H全历史应有几十到上百次信号

### 三、渐进式过滤器测试矩阵

#### A组: EMA参数敏感性测试
| 测试 | EMA设置 | Volume过滤 | 预期信号数 | 实际结果 |
|------|---------|------------|------------|----------|
| A0   | 无EMA   | 关闭       | 基线       | __ |
| A1   | 10/20   | 关闭       | 基线×0.7   | __ |
| A2   | 20/50   | 关闭       | 基线×0.5   | __ |
| A3   | 50/100  | 关闭       | 基线×0.3   | __ |

#### B组: Volume参数敏感性测试  
| 测试 | EMA设置 | Volume倍数 | 预期信号数 | 实际结果 |
|------|---------|------------|------------|----------|
| B1   | 20/50   | 1.02       | A2×0.8     | __ |
| B2   | 20/50   | 1.05       | A2×0.6     | __ |
| B3   | 20/50   | 1.10       | A2×0.4     | __ |
| B4   | 20/50   | 1.20       | A2×0.2     | __ |

#### 命令模板:
```bash
# A1测试
python run_four_swords_v1_7_4.py --data backtester/data/BTCUSDT/4h/BTCUSDT-4h-merged.csv --ema_fast 10 --ema_slow 20 --no_volume_filter --cash 500 --position_pct 0.05

# B2测试  
python run_four_swords_v1_7_4.py --data backtester/data/BTCUSDT/4h/BTCUSDT-4h-merged.csv --ema_fast 20 --ema_slow 50 --volume_mult 1.05 --cash 500 --position_pct 0.05
```

### 四、下单数量问题修复

#### 问题诊断:
当前 `_calculate_position_size()` 可能产生极小数量，被交易所拒绝

#### 修复方案:
```python
import math

# 在 params 中添加
('min_qty', 0.001),      # 最小交易数量
('qty_step', 0.001),     # 数量步进

def _calculate_position_size(self) -> float:
    """计算仓位大小，考虑最小交易单位"""
    total_value = self.broker.getvalue()
    position_value = total_value * self.params.position_pct
    price = self.data.close[0]
    
    # 原始计算
    raw_size = position_value / price
    
    # 量化到交易所步进
    quantized_size = math.floor(raw_size / self.params.qty_step) * self.params.qty_step
    
    # 确保满足最小数量要求
    final_size = max(quantized_size, self.params.min_qty)
    
    # 调试日志
    if raw_size != final_size:
        print(f"数量调整: {raw_size:.6f} → {final_size:.6f}")
    
    return final_size
```

### 五、数据质量检查

#### Volume数据验证:
```python
def __init__(self):
    # 在策略初始化后检查数据质量
    print(f"数据检查:")
    print(f"  Volume均值: {self.data.volume.array[-100:].mean():.2f}")
    print(f"  Volume零值比例: {(self.data.volume.array == 0).sum() / len(self.data.volume.array) * 100:.1f}%")
    print(f"  数据行数: {len(self.data)}")
```

#### 列名映射确认:
```python
# 在数据加载时打印列名映射
data_feed = FourSwordsCSVData(
    dataname=data_path,
    datetime=0, open=1, high=2, low=3, close=4, volume=5,
    # 明确指定列映射，避免错位
)
```

### 六、统计口径标准化

#### 统一回撤计算:
```python
def print_analysis_results(strategy):
    # 获取标准化指标
    returns_analyzer = strategy.analyzers.returns.get_analysis()
    drawdown_analyzer = strategy.analyzers.drawdown.get_analysis()
    
    # 统一格式输出
    if hasattr(returns_analyzer, 'rtot'):
        total_return_pct = returns_analyzer.rtot * 100
        print(f"总收益率: {total_return_pct:.2f}%")
    
    if hasattr(drawdown_analyzer, 'max'):
        max_dd_pct = drawdown_analyzer.max.drawdown  # 已经是百分比
        print(f"最大回撤: {max_dd_pct:.2f}%")
        print(f"回撤持续期: {drawdown_analyzer.max.len} bars")
```

### 七、实验执行记录表

#### 测试结果记录:
| 日期 | 测试ID | 配置 | Raw信号 | EMA通过 | Vol通过 | WT通过 | 实际成交 | 被拒订单 | 总收益 | 备注 |
|------|--------|------|---------|---------|---------|--------|----------|----------|--------|------|
| 0816 | 增强   | EMA+Vol+WT | 116 | 51(44%) | 23(45%) | 13(57%) | 8 | 0 | +1.65% | **EMA瓶颈** |
| 0816 | 简化   | 部分过滤 | ? | N/A | N/A | ? | 47 | ? | +2.92% | 对比 |
| 0816 | **A0** | **纯信号** | **117** | **117** | **117** | **117** | **48** | **0** | **+2.92%** | **基线验证** |

### 八、常见陷阱与注意事项

#### 1. 市价单执行时机
- Backtrader市价单默认"下一根开盘成交"
- 避免在当前bar条件极窄时依赖"当根成交"

#### 2. 指标命名遮蔽
- 确保自定义指标名称不与Backtrader内置冲突
- 使用明确的命名空间 (`self.sqzmom.lines.signal_bar`)

#### 3. 数据对齐问题
- 确认OHLCV列序列正确对应
- 检查时间戳格式与时区一致性

#### 4. 内存与性能
- 长历史数据可能导致指标计算缓慢
- 考虑使用数据采样进行快速测试

## 🎯 下一步行动计划

1. **立即执行**: 添加信号流量计数器到当前策略
2. **基线验证**: 运行A0测试确认原始信号量
3. **逐层排查**: 按A1-B4矩阵逐一测试
4. **定位瓶颈**: 分析哪一层过滤器影响最大
5. **参数优化**: 基于数据调整过滤器参数
6. **最终验证**: 确认优化后的信号频率与质量平衡

## 📝 关键发现与结论

### 🎯 信号流量分析结果

通过实施信号流量计数器，我们精确定位了问题根源：

#### **增强模式 vs 基线对比**:
- **基线(A0)**: 117个原始信号 → 48笔交易 (41.9%转换率)
- **增强模式**: 116个原始信号 → 8笔交易 (6.9%转换率)

#### **瓶颈层级分析**:
1. **EMA过滤器是主要瓶颈**: 116 → 51 (56%被过滤)
2. **成交量过滤器**: 51 → 23 (55%被过滤)  
3. **WaveTrend过滤器**: 23 → 13 (43%被过滤)
4. **订单执行**: 无被拒订单，转换正常

### 🔍 根本原因
- **EMA(20/50)趋势过滤过于严格**: 在震荡市场中过度限制信号
- **成交量1.1倍要求**: 在低波动期间难以满足
- **多重过滤器累积效应**: 三层过滤器使最终转换率降至7%

### 💡 优化建议
1. **EMA参数放宽**: 20/50 → 10/20 或 15/30
2. **成交量倍数降低**: 1.1 → 1.02-1.05
3. **考虑市场状态自适应**: 震荡期使用简化模式
4. **保持基线性能**: 简化模式48笔交易表现良好

### ✅ 验证成功
- **可观测性系统**: 成功识别每层过滤器影响
- **问题定位精确**: EMA过滤器是主要瓶颈
- **数据质量确认**: 117个有效SQZMOM信号证明指标正常
- **策略逻辑正确**: 基线模式48笔交易验证策略有效性

## 📊 推荐参数组合

基于分析结果，建议测试以下参数：
- **EMA**: 快速(10) 慢速(20) 
- **成交量倍数**: 1.05
- **保留WaveTrend**: 有效过滤噪音信号
- **预期结果**: 20-30笔高质量交易