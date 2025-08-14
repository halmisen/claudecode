# Pine Script v5 Syntax Fixes - Four Swords Strategy Experience

## 🚨 实际遇到的语法错误与解决方案

本文档记录了在开发Four Swords Swing Strategy v1.5过程中遇到的Pine Script v5语法错误及其解决方案。

## 错误1: Series vs Simple Type冲突

### 错误信息
```
Cannot call 'ta.ema' with argument 'length'='int_adaptiveWT_n1'. 
An argument of 'series int' type was used but a 'simple int' is expected.
```

### 问题代码
```pinescript
// 错误的自适应参数实现
int_adaptiveWT_n1 = bool_trendingMarket ? math.max(5, int_n1 - 2) : math.min(20, int_n1 + 2)
float_esa = ta.ema(float_ap, int_adaptiveWT_n1)  // ERROR!
```

### 解决方案
```pinescript
// ✅ 修复：直接使用输入参数
float_esa = ta.ema(float_ap, int_n1)  // 使用原始simple int参数
```

### 经验教训
- Pine Script v5的TA函数严格要求`simple int`类型参数
- 动态计算的参数会变成`series int`类型，不能用于TA函数
- 如需自适应行为，应在TA函数计算后进行条件选择

## 错误2: 未声明变量

### 错误信息
```
Undeclared identifier 'bool_waitLongExitBySqueeze'
Undeclared identifier 'confirmationScore'
```

### 问题代码
```pinescript
// 错误：使用了未声明的变量
if (bool_longSignalFiltered and strategy.position_size == 0)
    bool_waitLongExitBySqueeze := true  // ERROR: 未声明

confirmationScore += 30.0  // ERROR: 变量名不符合规范且未声明
```

### 解决方案
```pinescript
// ✅ 修复：正确声明状态变量
var bool bool_waitLongExitBySqueeze = false
var bool bool_waitShortExitBySqueeze = false
var float float_longStopPrice = na
var float float_shortStopPrice = na
var float float_entryPrice = na

// ✅ 修复：使用正确的变量名和初始化
float_confirmationScore = 0.0
if (bool_signalBar)
    float_confirmationScore += 30.0
```

### 经验教训
- 所有状态变量必须用`var`关键字预先声明
- 变量名必须遵循类型前缀规范（`float_`, `bool_`, `int_`等）
- 在使用`+=`操作符之前必须先初始化变量

## 错误3: Strategy.entry()参数错误

### 错误信息
```
The 'strategy.entry' function does not have an argument with the name 'qty_percent'
```

### 问题代码
```pinescript
// 错误：使用了不存在的参数
strategy.entry("Long", strategy.long, qty_percent=float_positionSize)  // ERROR!
```

### 解决方案
```pinescript
// ✅ 修复：使用正确的参数配合策略设置
strategy("...", default_qty_type=strategy.percent_of_equity, default_qty_value=15)
strategy.entry("Long", strategy.long, qty=float_positionSize)

// 或者使用标准参数
strategy.entry("Long", strategy.long)  // 使用默认仓位大小
```

### 经验教训
- Pine Script v5的`strategy.entry()`没有`qty_percent`参数
- 应在策略声明中设置`default_qty_type=strategy.percent_of_equity`
- 然后使用`qty`参数传递百分比值

## 错误4: 多行三元运算符

### 错误信息
```
Syntax error at input 'end of line without line continuation'
```

### 问题代码
```pinescript
// 错误：多行三元运算符
bool_momentumAccelerating = bool_useEnhancedMomentum ? 
    (float_momentum > float_momentumSMA3 and float_momentumRate > 0.05) : 
    (float_momentum > float_momentum[1])  // ERROR!
```

### 解决方案
```pinescript
// ✅ 修复：单行三元运算符
bool_momentumAccelerating = bool_useEnhancedMomentum ? (float_momentum > float_momentumSMA3 and float_momentumRate > 0.05) : (float_momentum > float_momentum[1])
```

### 经验教训
- Pine Script v5严格要求三元运算符在单行内完成
- 不允许使用反斜杠换行或多行格式
- 复杂逻辑应拆分为多个变量或使用if-else结构

## 完整的修复方案模板

### 1. 正确的变量声明模式
```pinescript
// ✅ 状态变量声明模板
var bool bool_waitLongExitBySqueeze = false
var bool bool_waitShortExitBySqueeze = false
var float float_longStopPrice = na
var float float_shortStopPrice = na
var float float_entryPrice = na
var int int_barsInTrade = 0
var float float_peakEquity = strategy.initial_capital
var int int_consecutiveLosses = 0
```

### 2. 正确的确认评分计算
```pinescript
// ✅ 确认评分计算模板
float_confirmationScore = 0.0
if (bool_signalBar)
    float_confirmationScore += 30.0
if (float_momentum > 0)
    float_confirmationScore += 25.0
if (float_wt1 > float_wt2)
    float_confirmationScore += 20.0
if (bool_emaBullTrend)
    float_confirmationScore += 15.0
if (bool_volumeConfirm)
    float_confirmationScore += 10.0
```

### 3. 正确的策略入场模式
```pinescript
// ✅ 策略声明和入场模板
strategy("Strategy Name", 
         initial_capital=500, 
         default_qty_type=strategy.percent_of_equity, 
         default_qty_value=15,
         commission_type=strategy.commission.percent, 
         commission_value=0.02)

// 入场执行
if (bool_longSignalFiltered)
    strategy.entry("Long", strategy.long, qty=float_positionSize, comment="Entry Comment")
```

### 4. 正确的自适应逻辑模式
```pinescript
// ✅ 自适应逻辑模板（避免series int问题）
float_ema_fast = ta.ema(close, 15)
float_ema_slow = ta.ema(close, 25)
float_adaptive_ema = bool_trendingMarket ? float_ema_fast : float_ema_slow

// 而不是：
// int_adaptiveLength = bool_trendingMarket ? 15 : 25  // 会产生series int
// float_ema = ta.ema(close, int_adaptiveLength)  // ERROR!
```

## 调试检查清单

### 编译前检查
- [ ] 所有变量名使用类型前缀（`float_`, `bool_`, `int_`, `string_`）
- [ ] 所有状态变量使用`var`关键字声明
- [ ] 三元运算符都在单行内
- [ ] TA函数使用fixed `simple int`参数
- [ ] `strategy.entry()`使用正确的参数名
- [ ] 没有在条件块内定义函数
- [ ] 所有变量在使用前已声明和初始化

### 常见错误排查
1. **"series int was used but simple int is expected"**
   → 检查TA函数的length参数，确保使用input参数而非计算值

2. **"Undeclared identifier"**
   → 检查变量声明，确保使用正确的类型前缀

3. **"function does not have an argument"**
   → 检查Pine Script v5文档，确认函数参数名

4. **"Syntax error at input"**
   → 检查多行语句，确保三元运算符和函数声明在单行

## 性能优化建议

### 内存优化
- 只对需要跨K线保持状态的变量使用`var`
- 避免创建不必要的series变量
- 缓存昂贵的计算结果

### 执行优化
- 将复杂条件逻辑拆分为简单的布尔变量
- 使用内置函数而非自定义实现
- 避免在同一K线内重复计算

## 版本兼容性注意事项

### Pine Script v5特性
- 更严格的类型检查
- series/simple类型区分更严格
- 多行语法限制更严格
- 更好的错误提示但编译更严格

### 从v4迁移到v5
- 审查所有动态参数使用
- 更新strategy函数调用
- 确保变量作用域正确
- 彻底测试所有功能

## 总结

通过修复Four Swords Strategy v1.5的语法错误，我们学到了Pine Script v5的严格要求：

1. **类型安全优先**: series vs simple类型区分严格
2. **变量声明规范**: 必须预先声明并遵循命名规范  
3. **语法简洁要求**: 单行语句，避免复杂的多行结构
4. **函数参数准确**: 使用正确的Pine Script v5 API

这些经验将帮助我们在未来的Pine Script开发中避免类似问题，写出更稳定、更高效的交易策略代码。