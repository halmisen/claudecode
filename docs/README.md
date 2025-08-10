# 交易策略开发文档索引

> 📍 **文档导航**: 这是项目的**文档索引页面**。如需项目概述和快速入门，请查看 [项目主页](../README.md)。

本文档提供了加密货币交易策略开发项目的完整文档索引，包含所有开发标准和指南。

## 📚 核心文档

### 1. [Pine Script 开发标准](./pine-script-standards.md)
- Pine Script v5 完整编码标准
- 最佳实践和黄金法则
- 代码组织和命名规范
- 性能优化指南

### 2. [Backtrader 快速入门](./backtrader-quickstart.md)
- **[Backtrader 核心架构指南](./backtrader-architecture-guide.md)**
- **[Backtrader 参数参考手册](./backtrader-parameter-reference.md)**

### 3. [Doji Ashi 策略指南](./strategies/)
- [v4 完整开发指南](./strategies/doji_ashi_strategy_v4_guide.md) - 最新版本，包含Plotly可视化
- [v3 开发计划](./strategies/doji_ashi_strategy_v3_plan.md) - 演进参考

### 4. [开发工作流程](./development-workflow.md)
- 文件操作命令
- 开发流程规范
- Git 工作流
- 测试和验证流程

### 5. [技术修复指南](./BACKTRADER_RETURNS_FIX.md)
- Backtrader Returns Analyzer 问题解决方案
- 手动收益计算方法

### 6. [上下文管理指南](./context-management-guide.md)
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
2. **Python 回测**：参考 [Backtrader 快速入门](./backtrader-quickstart.md)
3. **策略实现**：使用 [Doji Ashi v4 完整指南](./strategies/doji_ashi_strategy_v4_guide.md)
4. **环境搭建**：按照虚拟环境激活和依赖安装步骤
4. **开发流程**：遵循 [开发工作流程](./development-workflow.md)

### 文档查找
- 需要编码标准？→ [Pine Script 开发标准](./pine-script-standards.md)
- 需要框架帮助？→ [Backtrader 快速入门](./backtrader-quickstart.md)
- 需要策略开发？→ [Doji Ashi v4 指南](./strategies/doji_ashi_strategy_v4_guide.md)
- 需要操作命令？→ [开发工作流程](./development-workflow.md)
- 需要管理上下文？→ [上下文管理指南](./context-management-guide.md)
- 遇到返回值问题？→ [技术修复指南](./BACKTRADER_RETURNS_FIX.md)

### 兼容性说明
本文档结构设计为与所有支持 Markdown 的 CLI 工具兼容，包括：
- Claude Code
- Gemini CLI
- 其他基于 Markdown 的开发工具

## 🔄 文档更新
所有文档都会随着项目发展定期更新，确保信息的准确性和时效性。