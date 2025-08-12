# Gemini CLI 执行指南

## 🎯 核心功能

这是专为Gemini CLI设计的执行指南，用于配合Claude Code实现"Claude规划+Gemini执行"的成本优化工作流。

## 📋 标准执行模板

将以下模板保存为快捷指令，或直接复制给Gemini CLI使用：

```
读取项目根目录的『CLAUDE_GEMINI_MEGA_COLLABORATION_EXECUTION_MASTER_DOCUMENT.md』文件。严格按以下步骤执行：

1. **解析执行计划**：
   - 找到『## 🎯 执行计划 (plan)』区块
   - 解析其中的YAML格式jobs列表
   - 按照requires依赖关系确定执行顺序

2. **执行前检查**：
   - 验证所有requires的文件/目录是否存在
   - 检查timeout设置是否合理
   - 确认produces路径是否可写

3. **逐步执行**：
   - 按顺序执行每个job的cmd命令
   - 执行前回显: `[执行] job_id: 命令内容`
   - 执行后记录结果到『## ✅ 执行结果 (results)』区块

4. **结果格式**：
   每个job执行完成后，在results区块追加一行：
   ```
   **时间戳** - job_id: 状态 | 关键指标 | 产物路径
   ```

5. **错误处理**：
   如执行失败，在『## ❌ 错误日志 (errors)』区块追加：
   ```
   **时间戳** - job_id: ExitCode=N | 错误摘要(≤180字) | 详细日志路径
   ```

6. **安全限制**：
   - 禁止修改CLAUDE.md、源代码文件
   - 只允许写入logs/、reports/、data/、plots/目录
   - 只允许修改CLAUDE_GEMINI_MEGA_COLLABORATION_EXECUTION_MASTER_DOCUMENT.md的指定区块

7. **执行模式选择**：
   开始前询问执行模式：
   - [D] 直接执行 (推荐)
   - [P] 预演模式 (只显示将执行的命令)
   - [S] 逐步确认 (每步询问是否继续)

默认选择预演模式以确保安全。请问选择哪种模式？
```

## 🔧 快捷指令示例

为方便使用，可设置以下快捷指令：

### /run_plan (主要指令)
```
/run_plan - 执行开发文档中的plan，默认预演模式
```

### /run_plan_direct  
```
/run_plan --mode=direct - 直接执行所有计划任务
```

### /check_plan
```
仅检查CLAUDE_GEMINI_MEGA_COLLABORATION_EXECUTION_MASTER_DOCUMENT.md中的plan语法和依赖关系，不执行任何命令
```

### /status
```
显示CLAUDE_GEMINI_MEGA_COLLABORATION_EXECUTION_MASTER_DOCUMENT.md的当前状态：plan版本、待执行任务数、最近错误等
```

## 📊 执行结果示例

### Results区块示例：
```
**16:45:23** - create_logs_directory: ✅成功 | 目录已创建 | logs/
**16:45:24** - download_data: ✅成功 | 2.3MB下载 | data/ETHUSDT-2h-merged.csv  
**16:45:45** - run_backtest: ✅成功 | 收益率103.2% | plots/doji_ashi_v5_bokeh_crypto_20250812_164545.html
```

### Errors区块示例：
```
**16:50:12** - run_backtest: ❌失败 | ExitCode=1 | 缺少依赖文件data/BTCUSDT-2h-merged.csv | logs/error_20250812_165012.log
```

## ⚙️ 高级配置

### 自定义超时设置：
```yaml
jobs:
  - id: "long_backtest"
    timeout: 1800  # 30分钟
```

### 并行执行支持：
```yaml
jobs:
  - id: "download_btc"
    requires: []
  - id: "download_eth" 
    requires: []
  - id: "merge_data"
    requires: ["download_btc", "download_eth"]
```

### 条件执行：
```yaml
jobs:
  - id: "backup_old_results"
    cmd: "if [ -f plots/old_result.html ]; then mv plots/old_result.html archive/; fi"
```

## 🚨 故障排除

### 常见问题：

1. **YAML解析失败**：
   - 检查缩进是否正确（必须用空格，不能用tab）
   - 确认所有字符串都用双引号包围

2. **依赖文件不存在**：
   - 在errors区块记录详细的缺失文件路径
   - 不要自动创建缺失文件，而是报告给Claude处理

3. **权限拒绝**：
   - 确认目标目录可写
   - 检查是否在安全限制的目录范围内

4. **命令执行超时**：
   - 记录超时信息到errors区块
   - 考虑增加timeout值或拆分任务

### 错误恢复：
- 发生错误时，停止后续依赖该job的任务
- 在errors区块详细记录错误信息
- 不要尝试自动修复，交由Claude重新规划

## 📝 日志管理

所有详细日志保存到 `logs/` 目录：
- `logs/execution_YYYYMMDD_HHMMSS.log` - 完整执行日志
- `logs/error_YYYYMMDD_HHMMSS.log` - 错误详情
- `logs/performance_YYYYMMDD.log` - 性能指标记录

开发文档中只保留关键摘要信息，避免文件过大影响Claude上下文加载。

---

## 🔧 Hook白名单机制测试

**测试时间**: 2025-08-12  
**测试目的**: 验证planning mode下的.md文件写入功能

### 白名单配置
- ✅ 文件类型: .md, .txt, .log, .json, .yaml, .yml, .py
- ✅ 工具类型: TodoWrite, Read, LS, Glob, Grep, WebFetch, WebSearch  
- ✅ 文件模式: claude-task-, gemini_, GEMINI.md, docs/, .claude/, logs/

### 解决方案效果
通过在 `pre_tool_use.py` 中添加 `should_allow_operation()` 函数，现在可以：
- ✅ 在planning mode下写入文档和任务文件
- ✅ 正常使用读取和搜索工具  
- ✅ 更新任务追踪和执行指南
- ❌ 仍然阻止潜在危险的代码修改操作

**结论**: Claude现在能在规划模式下更新开发文档并传递任务给Gemini CLI了！