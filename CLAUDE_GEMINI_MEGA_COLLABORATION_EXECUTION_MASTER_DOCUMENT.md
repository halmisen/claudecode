# 项目文件整理与文档更新执行文档

## 📋 当前项目状态

**当前主力**: Four Swords Swing Strategy v1.4  
**文件位置**: `pinescript/strategies/oscillator/Four_Swords_Swing_Strategy_v1_4.pine`  
**项目状态**: ✅ v1.4开发成功 - 需要整理文档结构  
**最后更新**: 2025-08-13  
**任务类型**: 🗂️ **文件整理与文档同步**

---

## 🎯 执行计划 (plan)

```yaml
plan:
  version: "2025-08-13-09"
  context: "Four Swords v1.4成功后的文件整理与文档更新"
  priority: "P1 - 文档结构优化"
  status: "待执行"
  jobs:
    - id: "create_archive_directories"
      desc: "创建归档和策略文档目录结构"
      cmd: |
        mkdir -p docs/archived docs/strategies
      requires: []
      produces: ["docs/archived/", "docs/strategies/"]
      
    - id: "move_vegas_tunnel_files"
      desc: "移动Vegas Tunnel相关文档到归档目录"
      cmd: |
        mv "CLAUDE_GEMINI_MEGA_COLLABORATION_EXECUTION_MASTER_DOCUMENT.md" "docs/archived/vegas_tunnel_collaboration.md" && \
        mv "Claude_Gemini_协作工作流说明书.md" "docs/archived/claude_gemini_workflow.md" && \
        mv "VEGAS_TUNNEL_ROADMAP.md" "docs/archived/vegas_tunnel_roadmap.md" && \
        mv "Vegas tunnel XZ plan.md" "docs/archived/vegas_tunnel_plan.md"
      requires: ["create_archive_directories"]
      produces: ["docs/archived/*.md"]
      
    - id: "organize_strategy_docs"
      desc: "整理四剑客策略文档到策略目录"
      cmd: |
        mv docs/四剑客波段策略*.md docs/strategies/
      requires: ["create_archive_directories"]
      produces: ["docs/strategies/四剑客*.md"]
      
    - id: "update_gemini_md"
      desc: "更新GEMINI.md反映v1.4状态和新项目结构"
      status: "需要手动更新"
      produces: ["GEMINI.md"]
      
    - id: "update_readme_md"
      desc: "更新README.md突出Four Swords v1.4为主力策略"
      status: "需要手动更新"
      produces: ["README.md"]
      
    - id: "verify_claude_md"
      desc: "验证CLAUDE.md的v1.4状态更新是否完整"
      cmd: |
        grep -n "v1.4" CLAUDE.md && \
        grep -n "Four_Swords_Swing_Strategy_v1_4" CLAUDE.md
      requires: []
      produces: ["验证报告"]
      
    - id: "clean_root_directory"
      desc: "清理根目录，移除剩余的临时文件"
      cmd: |
        ls -la | grep -E "\.tmp$|\.bak$|~$" | awk '{print $9}' | xargs -r rm -f
      requires: ["move_vegas_tunnel_files"]
      produces: ["清洁的根目录"]
      
    - id: "git_commit_changes"
      desc: "提交文件整理和文档更新结果"
      cmd: |
        git add . && \
        git commit -m "docs: Organize project files and update documentation for Four Swords v1.4 focus

- Archive Vegas Tunnel XZ collaboration documents to docs/archived/
- Move Four Swords strategy documentation to docs/strategies/
- Update project documentation to reflect v1.4 as current main strategy
- Clean up root directory structure for better organization

🤖 Generated with Claude Code and Gemini collaboration" && \
        git push
      requires: ["move_vegas_tunnel_files", "organize_strategy_docs", "clean_root_directory"]
      produces: ["Git commit"]
```

---

## 🎯 文档更新指引

### **GEMINI.md 需要更新的内容**

1. **项目状态更新**:
   ```markdown
   ## 🎯 核心职责
   
   当前主力项目: **Four Swords Swing Strategy v1.4**
   项目类型: 高胜率波段交易策略 (基于SQZMOM+WaveTrend)
   开发状态: ✅ v1.4核心功能完成，持续优化中
   ```

2. **移除Vegas Tunnel引用**:
   - 删除所有Vegas Tunnel相关的执行示例
   - 更新执行参考为Four Swords v1.4相关任务

3. **添加v1.4支持任务**:
   ```markdown
   ## 📋 支持的任务类型
   
   - Four Swords v1.4策略参数优化
   - Pine Script波段策略开发
   - SQZMOM+WaveTrend指标集成
   - 策略回测和性能分析
   ```

### **README.md 需要更新的内容**

1. **主要特性更新**:
   ```markdown
   ## ⭐ 主要特性
   
   - **🎯 专业策略**: Four Swords v1.4波段策略 (基于SQZMOM+WaveTrend)
   - **📊 高胜率系统**: 适合INFP性格的波段交易，目标胜率75%+
   - **🛡️ 智能状态管理**: 动量加速等待压缩 vs 动量衰竭直接退出
   - **⚙️ 灵活配置**: EMA趋势过滤+成交量确认可独立开关
   ```

2. **快速开始更新**:
   ```markdown
   ### 2. 主力策略: Four Swords v1.4 ⭐推荐
   
   ```bash
   # 加载v1.4策略到TradingView
   # 文件: pinescript/strategies/oscillator/Four_Swords_Swing_Strategy_v1_4.pine
   # 建议时间框架: 4H或1D波段交易
   # 推荐配置: 保持默认设置(初学者)或开启所有过滤器(进阶)
   ```

3. **项目结构更新**:
   ```markdown
   ## 📁 项目结构
   
   ```
   BIGBOSS/claudecode/
   ├── 📋 CLAUDE.md                    # Claude Code项目指南  
   ├── 📋 GEMINI.md                    # Gemini执行官手册
   ├── 📋 README.md                    # 项目概览
   ├── 📁 pinescript/strategies/oscillator/
   │   └── ⭐ Four_Swords_Swing_Strategy_v1_4.pine  # 当前主力策略
   ├── 📁 docs/
   │   ├── 📁 strategies/              # 策略开发文档
   │   ├── 📁 archived/               # 归档文档  
   │   └── 📄 *.md                    # 技术文档
   └── 📁 backtester/                 # Python回测系统
   ```

---

## 📋 手动更新检查清单

**Gemini完成文件移动后，需要手动更新的内容**:

- [ ] **GEMINI.md**: 更新核心职责和支持任务  
- [ ] **README.md**: 更新主要特性和快速开始
- [ ] **验证CLAUDE.md**: 确认v1.4状态完整
- [ ] **检查链接**: 确保文档内部链接更新正确

---

## ✅ 执行结果 (results)

*Gemini执行任务后，结果将记录在此处*

---

## ❌ 错误日志 (errors)

*如有执行错误，详细信息将记录在此处*

---

## 🎯 预期成果

**整理后的项目结构**:
- 📁 **根目录清洁**: 移除Vegas Tunnel相关文档
- 📁 **docs/archived/**: Vegas Tunnel项目完整归档
- 📁 **docs/strategies/**: 四剑客策略文档集中管理
- 📄 **文档同步**: 三大核心文档反映v1.4状态

**改进效果**:
- ✅ **结构清晰**: 当前项目vs归档项目分离
- ✅ **易于维护**: 按功能分类的文档结构  
- ✅ **信息同步**: 所有文档反映最新项目状态
- ✅ **协作友好**: Gemini可以清晰找到执行任务

**下一步行动**:
项目文件整理完成后，可以专注于Four Swords v1.4的进一步优化和Python回测实现。