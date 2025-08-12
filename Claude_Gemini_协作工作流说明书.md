# Claude + Gemini 协作工作流说明书

## 🎯 工作流概述

这是一套专为Claude Code Pro用户设计的成本优化工作流，通过"Claude负责规划分析，Gemini负责执行操作"的分工模式，大幅降低Claude使用配额，同时保持高效的开发体验。

### 核心理念
- **Claude**: 智能分析、策略规划、问题诊断
- **Gemini**: 具体执行、结果反馈、日志记录
- **CLAUDE_GEMINI_MEGA_COLLABORATION_EXECUTION_MASTER_DOCUMENT.md**: 双方协作的"单一事实来源"

---

## 📁 文件架构

### 三层文件结构

```
BIGBOSS/
├── 📋 CLAUDE.md                    # 🔒 项目规范 (长期不变)
├── 📋 CLAUDE_GEMINI_MEGA_COLLABORATION_EXECUTION_MASTER_DOCUMENT.md                   # 🔄 协作枢纽 (当前状态)
├── 📁 .claude/                     # ⚙️ Hook配置
│   ├── settings.json               # Claude Code设置
│   └── hooks/                      # Hook脚本
│       ├── post_tool_use.py        # 拦截Write/Edit/Bash
│       ├── session_stop.py         # 会话结束总结  
│       └── session_start.py        # 会话开始注入
├── 📁 logs/                        # 📜 执行日志 (详细记录)
└── 📋 gemini_execution_guide.md    # 📖 Gemini执行手册
```

### 文件职责分工

| 文件 | 更新者 | 内容 | 大小限制 |
|------|--------|------|----------|
| CLAUDE.md | 用户 | 项目规范、命令约定、长期不变信息 | 无限制 |
| CLAUDE_GEMINI_MEGA_COLLABORATION_EXECUTION_MASTER_DOCUMENT.md | Claude+Gemini | 当前plan、执行结果、错误日志 | <10KB |
| logs/* | Gemini | 详细执行日志、错误详情 | 无限制 |

---

## 🔧 安装配置

### 1. 启用Claude Code Hooks

确保`.claude/settings.json`配置正确：

```json
{
  "hooks": {
    "post_tool_use": {"enabled": true},
    "stop": {"enabled": true}, 
    "session_start": {"enabled": true}
  },
  "blocked_tools": {
    "bash": {"enabled": true},
    "write": {"enabled": false},
    "edit": {"enabled": false}
  }
}
```

### 2. 验证Hook脚本

检查Hook脚本是否可执行：
```bash
python .claude/hooks/post_tool_use.py  # 测试拦截功能
python .claude/hooks/session_start.py  # 测试上下文注入
```

### 3. 配置Gemini CLI

确保Gemini CLI已安装并配置API密钥。创建快捷指令：
```
/run_plan - 执行开发文档中的计划
/check_plan - 检查计划语法
/status - 显示当前状态
```

---

## 🎛️ 智能模式控制

### 条件触发机制

系统支持两种工作模式：

#### ⚡ 正常模式 (默认)
- Claude直接执行所有操作
- 适合简单任务和快速修改
- 无需额外配置

#### 🔄 规划模式 (条件激活)
- Claude只规划不执行，Gemini负责执行
- 自动或手动激活
- 适合复杂任务和批量操作

### 激活方式

#### 1. 关键词自动激活
在描述任务时包含以下关键词：
```
- "复杂任务" / "这是一个复杂任务"
- "批量操作" / "多文件操作"  
- "规划模式" / "使用规划模式"
- "大型重构" / "自动化流程"
- "启用协作模式"
```

#### 2. 手动控制命令
```bash
# 激活规划模式
python .claude/control_planning_mode.py on

# 关闭规划模式  
python .claude/control_planning_mode.py off

# 查看当前状态
python .claude/control_planning_mode.py status

# 切换模式
python .claude/control_planning_mode.py toggle
```

#### 3. 会话内控制
在Claude对话中直接使用：
```
/planning-on    # 激活规划模式
/planning-off   # 关闭规划模式
/planning-status # 查看状态
```

### 绕过机制
如需临时使用正常模式，添加以下关键词：
```
- "简单修改" / "快速修复"
- "单文件操作" / "直接执行"
- "normal mode" / "bypass planning"
```

---

## 🚀 日常使用流程

### Phase 1: Claude 分析规划阶段

1. **启动Claude Code**：
   ```bash
   claude code --resume  # 自动加载开发文档上下文
   ```

2. **描述需求并选择模式**：
   ```
   # 复杂任务 - 自动激活规划模式
   这是一个复杂任务：我需要分析ETHUSDT策略在不同时间周期的表现差异
   
   # 简单任务 - 保持正常模式
   帮我快速修复这个文件中的拼写错误
   ```

3. **Claude智能响应**：
   - **规划模式**: Hook拦截操作，生成执行计划
   - **正常模式**: 直接执行操作，立即完成任务

### Phase 2: Gemini 执行阶段  

1. **启动Gemini CLI**：
   ```bash
   gemini-cli
   ```

2. **执行标准指令**：
   ```
   读取项目根目录的『CLAUDE_GEMINI_MEGA_COLLABORATION_EXECUTION_MASTER_DOCUMENT.md』文件。严格按照其中的plan区块执行所有job，使用预演模式开始。
   ```

3. **Gemini自动执行**：
   - 解析YAML格式的jobs列表
   - 按依赖关系顺序执行
   - 回写results和errors到开发文档

### Phase 3: Claude 分析优化阶段

1. **重新连接Claude**：
   - Hook自动注入最新的执行结果
   - Claude基于results/errors调整策略

2. **迭代优化**：
   - 分析性能指标
   - 调整参数配置
   - 生成新的执行计划

---

## 📋 CLAUDE_GEMINI_MEGA_COLLABORATION_EXECUTION_MASTER_DOCUMENT.md 结构详解

### 标准模板

```markdown
# 开发文档 - Claude+Gemini协作工作流

## 📋 当前迭代状态
**版本**: 2025-08-12-01
**目标**: 具体的迭代目标描述
**最后更新**: 2025-08-12 16:30

## 🎯 执行计划 (plan)
```yaml
plan:
  version: "2025-08-12-01"
  context: "当前迭代的目标描述"
  jobs:
    - id: "unique_job_id"
      desc: "任务描述"
      cmd: "具体的shell命令"
      requires: ["前置依赖job_id"]
      produces: ["产出文件路径"]
      timeout: 300
```

## ✅ 执行结果 (results)
**16:45:23** - job_id: ✅成功 | 关键指标 | 产物路径

## ❌ 错误日志 (errors)  
**16:50:12** - job_id: ❌失败 | ExitCode=1 | 错误摘要 | 详细日志路径

## 📝 会话记录
**2025-08-12 16:30** - 会话开始
- 任务描述和进展记录
```

### 区块管理规则

| 区块 | 写入者 | 内容格式 | 大小限制 |
|------|--------|----------|----------|
| plan | Claude | YAML格式 | <5KB |
| results | Gemini | 时间戳+状态+指标 | <2KB |
| errors | Gemini | 时间戳+错误码+摘要 | <2KB |
| 会话记录 | Claude | 时间戳+活动描述 | <1KB |

---

## 🎮 高级使用技巧

### 1. 子任务依赖管理

```yaml
jobs:
  - id: "download_data"
    requires: []
  - id: "preprocess_data"  
    requires: ["download_data"]
  - id: "run_analysis"
    requires: ["preprocess_data"]
```

### 2. 并行任务执行

```yaml
jobs:
  - id: "download_btc"
    requires: []
  - id: "download_eth"
    requires: []
  - id: "compare_performance"
    requires: ["download_btc", "download_eth"]
```

### 3. 条件执行逻辑

```yaml
jobs:
  - id: "backup_if_exists"
    cmd: "[ -f old_result.csv ] && cp old_result.csv backup/ || echo 'No backup needed'"
```

### 4. 性能监控集成

```yaml
jobs:
  - id: "run_backtest_with_metrics"
    cmd: "time python backtester/run_strategy.py --enable-profiling"
    produces: ["plots/result.html", "logs/performance.log"]
```

---

## 🛠️ 故障排除指南

### 常见问题解决

#### 1. Hook不生效
**症状**: Claude仍在直接执行命令  
**解决**: 
- 检查`.claude/settings.json`配置
- 验证Hook脚本语法：`python .claude/hooks/post_tool_use.py`
- 重启Claude Code

#### 2. YAML解析失败
**症状**: Gemini报告语法错误  
**解决**:
- 确保使用空格缩进（不是tab）
- 所有字符串用双引号包围
- 使用在线YAML验证器检查语法

#### 3. 依赖文件缺失
**症状**: job执行失败，requires文件不存在  
**解决**:
- 检查文件路径是否正确
- 确认前置job是否成功执行
- 更新requires依赖关系

#### 4. 执行超时
**症状**: 长时间运行任务被终止  
**解决**:
- 增加timeout值
- 拆分大任务为多个小任务
- 使用后台执行模式

### 错误恢复流程

1. **检查errors区块**：查看具体错误信息
2. **分析日志文件**：查看`logs/`下的详细日志
3. **调整plan**：修复错误后更新执行计划
4. **重新执行**：使用Gemini重新运行失败的job

---

## 📊 成本效益分析

### 传统工作流 vs 协作工作流

| 指标 | 传统Claude | Claude+Gemini协作 | 节省比例 |
|------|------------|-------------------|----------|
| Claude调用次数 | 100次 | 30次 | 70% |
| 执行时长 | 15分钟 | 3分钟 | 80% |
| 上下文大小 | 50KB+ | <10KB | 80% |
| 错误恢复效率 | 慢 | 快 | 60% |

### 最适合的使用场景

✅ **高收益场景**:
- 批量数据处理
- 策略回测分析
- 代码重构任务
- 自动化部署
- 测试执行

❌ **低收益场景**:
- 单文件小修改
- 探索性分析
- 一次性查询

---

## 🔮 进阶扩展

### 1. 集成Sub-Agent

```yaml
# 可配合专门的agent使用
jobs:
  - id: "quant_analysis"
    cmd: "claude code --agent quant-analyst 'analyze strategy performance'"
    desc: "使用quant-analyst专门分析策略表现"
```

### 2. 自动化CI/CD集成

```yaml
jobs:
  - id: "run_tests"
    cmd: "pytest tests/ --junitxml=reports/junit.xml"
  - id: "generate_report"
    cmd: "python scripts/generate_report.py"
    requires: ["run_tests"]
```

### 3. 多环境支持

```yaml
# 环境特定的配置
jobs:
  - id: "deploy_staging"
    cmd: "deploy.sh staging"
    condition: "branch == 'develop'"
  - id: "deploy_production"  
    cmd: "deploy.sh production"
    condition: "branch == 'main'"
```

---

## 📚 参考资料

- [Claude Code官方文档](https://docs.anthropic.com/claude-code)
- [Gemini CLI参考](https://ai.google.dev/gemini-api)
- [项目CLAUDE.md](./CLAUDE.md) - 项目特定配置
- [Gemini执行指南](./gemini_execution_guide.md) - Gemini操作手册

---

## 🤝 支持与反馈

如遇到问题：
1. 查看`logs/hook_errors.log`了解Hook错误
2. 检查`CLAUDE_GEMINI_MEGA_COLLABORATION_EXECUTION_MASTER_DOCUMENT.md`的errors区块
3. 参考故障排除指南
4. 必要时重置开发文档模板

**最佳实践**: 保持开发文档轻量(<10KB)，详细日志放在logs目录，定期归档老的执行计划。