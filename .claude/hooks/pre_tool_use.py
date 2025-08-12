#!/usr/bin/env python3
"""
PreToolUse Hook - 在工具执行前检查planning mode并拦截
"""
import json
import sys
import os
from datetime import datetime
from pathlib import Path

def get_planning_mode_status():
    """获取当前规划模式状态"""
    try:
        state_file = Path(".claude/planning_mode.state")
        if state_file.exists():
            content = state_file.read_text().strip()
            return content == "enabled"
    except:
        pass
    return False

def check_user_input_for_triggers():
    """检查最近的用户输入是否包含触发关键词"""
    try:
        # 检查临时输入文件
        temp_input_file = Path(".claude/last_user_input.tmp")
        if temp_input_file.exists():
            user_input = temp_input_file.read_text(encoding='utf-8')
            
            # 触发关键词
            trigger_keywords = [
                "复杂任务", "批量操作", "规划模式", "planning mode",
                "大型重构", "多文件操作", "自动化流程", 
                "这是一个复杂任务", "使用规划模式", "启用协作模式"
            ]
            
            user_input_lower = user_input.lower()
            for trigger_word in trigger_keywords:
                if trigger_word.lower() in user_input_lower:
                    return True
    except:
        pass
    return False

def get_daily_task_file():
    """获取今日任务文件路径"""
    today = datetime.now().strftime("%y%m%d")
    return f"claude-task-{today}.md"

def create_daily_task_file():
    """创建今日任务文件"""
    task_file_path = Path(get_daily_task_file())
    
    if not task_file_path.exists():
        today_str = datetime.now().strftime("%Y-%m-%d")
        template = f"""# Claude任务计划 - {today_str}

## 🎯 执行计划

```yaml
plan:
  version: "{today_str}-01"
  context: "Claude规划模式任务记录"
  jobs: []
```

---

## ✅ 执行结果 (results)

*待Gemini执行*

---

## ❌ 错误日志 (errors)

*无*

---

## 📝 会话记录

**{datetime.now().strftime('%H:%M:%S')}** - 自动创建今日任务文件
"""
        task_file_path.write_text(template, encoding='utf-8')
        print(f"✅ 已创建今日任务文件: {get_daily_task_file()}")

def should_allow_operation():
    """检查是否应该允许操作（白名单机制）"""
    try:
        # 读取当前工具调用的上下文信息（如果存在）
        tool_context_file = Path(".claude/current_tool_context.json")
        tool_name = ""
        tool_args = ""
        
        if tool_context_file.exists():
            try:
                with open(tool_context_file, 'r', encoding='utf-8') as f:
                    context = json.load(f)
                    tool_name = context.get('tool_name', '')
                    tool_args = json.dumps(context.get('args', {}))
            except:
                pass
        
        # 备用：从环境变量获取
        if not tool_name:
            tool_name = os.environ.get('CLAUDE_TOOL_NAME', '')
            tool_args = os.environ.get('CLAUDE_TOOL_ARGS', '')
        
        # 白名单：总是允许的工具
        always_allowed_tools = ['TodoWrite', 'Read', 'LS', 'Glob', 'Grep', 'WebFetch', 'WebSearch']
        
        # 白名单：允许的文件扩展名（用于Write/Edit工具）
        allowed_extensions = ['.md', '.txt', '.log', '.json', '.yaml', '.yml', '.py']
        
        # 白名单：允许的文件和目录模式
        allowed_patterns = [
            'claude-task-', 'gemini_execution_guide', 'GEMINI.md',
            'claude-gemini-', 'task_plan', 'execution_plan',
            '.claude/', 'logs/', 'docs/', 'gemini_'
        ]
        
        # 检查工具类型
        if tool_name in always_allowed_tools:
            return True
            
        # 对于Write/Edit工具，检查文件路径
        if tool_name in ['Write', 'Edit', 'MultiEdit']:
            # 检查文件扩展名
            for ext in allowed_extensions:
                if ext in tool_args.lower():
                    # 进一步检查是否是允许的文件模式
                    for pattern in allowed_patterns:
                        if pattern in tool_args.lower():
                            return True
                    # 如果是.md文件，默认允许
                    if '.md' in tool_args.lower():
                        return True
        
        return False
        
    except Exception as e:
        # 记录错误但默认拒绝
        try:
            Path("logs").mkdir(exist_ok=True)
            with open("logs/hook_whitelist_errors.log", "a", encoding='utf-8') as f:
                f.write(f"[{datetime.now()}] 白名单检查错误: {str(e)}\n")
        except:
            pass
        return False

def main():
    """主要处理逻辑"""
    try:
        # 如果检测到触发关键词，自动激活planning mode
        if check_user_input_for_triggers():
            state_file = Path(".claude/planning_mode.state")
            state_file.parent.mkdir(exist_ok=True)
            state_file.write_text("enabled")
            print("🎯 检测到复杂任务关键词 - 已激活规划模式")
            create_daily_task_file()
        
        # 检查是否应该拦截
        if get_planning_mode_status():
            # 检查白名单
            if should_allow_operation():
                print("✅ 规划模式 - 允许白名单操作")
                sys.exit(0)  # 允许执行
            
            print("🔄 检测到规划模式 - 操作已拦截并记录到执行计划")
            
            # 记录拦截日志
            log_msg = f"[{datetime.now().strftime('%H:%M:%S')}] 已拦截工具操作\n"
            Path("logs").mkdir(exist_ok=True)
            with open("logs/claude_intercepted.log", "a", encoding='utf-8') as f:
                f.write(log_msg)
            
            sys.exit(1)  # 阻止工具执行
        
        # 允许正常执行
        sys.exit(0)
        
    except Exception as e:
        # 记录错误但不阻止执行
        Path("logs").mkdir(exist_ok=True)
        with open("logs/hook_errors.log", "a", encoding='utf-8') as f:
            f.write(f"[{datetime.now()}] PreToolUse Hook错误: {str(e)}\n")
        sys.exit(0)

if __name__ == "__main__":
    main()