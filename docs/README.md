# ABOARD 开发文档索引

本文档提供了ABOARD交易算法开发项目的完整文档索引，包含所有开发标准和指南。

## 📚 核心文档

### 1. [Pine Script 开发标准](./pine-script-standards.md)
- Pine Script v5 完整编码标准
- 最佳实践和黄金法则
- 代码组织和命名规范
- 性能优化指南

### 2. [Python 回测框架指南](./python-frameworks-guide.md)
- Jesse 框架使用指南
- VectorBT 框架使用指南
- 环境设置和依赖管理
- 策略实现模式

### 3. [策略转换指南](./strategy-conversion-guide.md)
- Pine Script 到 Python 的转换方法
- 框架间一致性验证
- 转换模板和示例
- 常见问题解决方案

### 4. [开发工作流程](./development-workflow.md)
- 文件操作命令
- 开发流程规范
- Git 工作流
- 测试和验证流程

### 5. [上下文管理指南](./context-management-guide.md)
- 对话长度管理
- 上下文清理时机
- 性能优化建议
- 最佳实践

## 🛠️ 代码模板

### Kelly 准则模板
- 文件：`./templates/kelly-criterion.pine`
- 用于添加凯利统计到策略中

### 策略配置模板
- 文件：`./templates/strategy-config.pine`
- 标准回测配置设置

## 📖 使用指南

### 快速开始
1. **Pine Script 开发**：先阅读 [Pine Script 开发标准](./pine-script-standards.md)
2. **Python 回测**：参考 [Python 回测框架指南](./python-frameworks-guide.md)
3. **策略转换**：使用 [策略转换指南](./strategy-conversion-guide.md)
4. **开发流程**：遵循 [开发工作流程](./development-workflow.md)

### 文档查找
- 需要编码标准？→ [Pine Script 开发标准](./pine-script-standards.md)
- 需要框架帮助？→ [Python 回测框架指南](./python-frameworks-guide.md)
- 需要转换策略？→ [策略转换指南](./strategy-conversion-guide.md)
- 需要操作命令？→ [开发工作流程](./development-workflow.md)
- 需要管理上下文？→ [上下文管理指南](./context-management-guide.md)

### 兼容性说明
本文档结构设计为与所有支持 Markdown 的 CLI 工具兼容，包括：
- Claude Code
- Gemini CLI
- 其他基于 Markdown 的开发工具

## 🔄 文档更新
所有文档都会随着项目发展定期更新，确保信息的准确性和时效性。