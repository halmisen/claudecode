#!/usr/bin/env python3
"""
Post Tool Use Hook - 条件拦截Write/Edit/Bash操作
支持关键词触发和手动控制的智能拦截系统
"""
import json
import sys
import os
import yaml
from datetime import datetime
from pathlib import Path

# 配置加载
def load_settings():
    """加载Hook配置"""
    try:
        settings_path = Path(".claude/settings.json")
        if settings_path.exists():
            with open(settings_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return {}

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

def set_planning_mode_status(enabled):
    """设置规划模式状态"""
    try:
        state_file = Path(".claude/planning_mode.state")
        state_file.parent.mkdir(exist_ok=True)
        state_file.write_text("enabled" if enabled else "disabled")
        return True
    except:
        return False

def check_user_input_for_triggers():
    """检查最近的用户输入是否包含触发关键词"""
    settings = load_settings()
    trigger_keywords = settings.get('interception_config', {}).get('trigger_keywords', [])
    bypass_keywords = settings.get('interception_config', {}).get('bypass_keywords', [])
    
    # 尝试从环境变量或临时文件获取用户输入
    user_input = ""
    
    # 方法1: 检查环境变量
    user_input = os.environ.get('CLAUDE_USER_INPUT', '')
    
    # 方法2: 检查临时输入文件
    if not user_input:
        temp_input_file = Path(".claude/last_user_input.tmp")
        if temp_input_file.exists():
            try:
                user_input = temp_input_file.read_text(encoding='utf-8')
            except:
                pass
    
    # 方法3: 检查开发文档中的会话记录
    if not user_input:
        try:
            dev_doc = Path("开发文档.md")
            if dev_doc.exists():
                content = dev_doc.read_text(encoding='utf-8')
                # 查找最近的会话记录
                import re
                recent_entries = re.findall(r'\*\*([\d-]+\s+[\d:]+)\*\*\s*-\s*([^\n]+)', content)
                if recent_entries:
                    user_input = recent_entries[-1][1]  # 最近一条记录
        except:
            pass
    
    if not user_input:
        return False, False
    
    user_input_lower = user_input.lower()
    
    # 检查绕过关键词（优先级更高）
    for bypass_word in bypass_keywords:
        if bypass_word.lower() in user_input_lower:
            return False, True  # 明确要求绕过
    
    # 检查触发关键词
    for trigger_word in trigger_keywords:
        if trigger_word.lower() in user_input_lower:
            return True, False  # 触发规划模式
    
    return False, False

def handle_control_commands(user_input):
    """处理规划模式控制命令"""
    settings = load_settings()
    control_commands = settings.get('interception_config', {}).get('control_commands', {})
    
    for command, description in control_commands.items():
        if command in user_input:
            if command == "/planning-on":
                set_planning_mode_status(True)
                print(f"✅ 规划模式已激活 - {description}")
                return True
            elif command == "/planning-off":
                set_planning_mode_status(False)
                print(f"✅ 规划模式已关闭 - {description}")
                return True
            elif command == "/planning-status":
                status = get_planning_mode_status()
                mode = "规划模式" if status else "正常模式"
                print(f"📋 当前状态: {mode}")
                return True
    
    return False

def should_intercept_operation():
    """判断是否应该拦截操作"""
    # 1. 检查手动设置的规划模式状态
    if get_planning_mode_status():
        return True
    
    # 2. 检查用户输入中的触发关键词
    trigger_detected, bypass_detected = check_user_input_for_triggers()
    
    if bypass_detected:
        return False  # 明确要求绕过
    
    if trigger_detected:
        # 自动激活规划模式
        set_planning_mode_status(True)
        return True
    
    # 3. 默认不拦截
    return False

def get_daily_task_file():
    """获取今日任务文件路径"""
    today = datetime.now().strftime("%y%m%d")
    return f"claude-task-{today}.md"

def load_daily_task_file():
    """加载今日任务文件内容"""
    task_file_path = Path(get_daily_task_file())
    
    if not task_file_path.exists():
        # 创建今日任务文件模板
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

**{datetime.now().strftime('%H:%M:%S')}** - 创建今日任务文件
"""
        task_file_path.write_text(template, encoding='utf-8')
        content = template
    else:
        content = task_file_path.read_text(encoding='utf-8')
    
    # 解析YAML plan区块
    plan_start = content.find("```yaml\nplan:")
    plan_end = content.find("```", plan_start + 7)
    
    if plan_start == -1 or plan_end == -1:
        return content, {}
    
    yaml_content = content[plan_start + 7:plan_end]
    try:
        plan = yaml.safe_load(yaml_content)
        return content, plan
    except:
        return content, {}

def save_daily_task_file(content, plan):
    """保存更新后的今日任务文件"""
    # 更新版本号
    current_version = plan.get('plan', {}).get('version', '2025-08-12-01')
    version_parts = current_version.split('-')
    if len(version_parts) == 3:
        seq = int(version_parts[2]) + 1
        new_version = f"{version_parts[0]}-{version_parts[1]}-{seq:02d}"
    else:
        today_str = datetime.now().strftime("%Y-%m-%d")
        new_version = f"{today_str}-02"
    
    plan['plan']['version'] = new_version
    
    # 重建YAML区块
    yaml_str = yaml.dump(plan, allow_unicode=True, default_flow_style=False)
    
    # 查找并替换plan区块
    plan_start = content.find("```yaml\nplan:")
    plan_end = content.find("```", plan_start + 7)
    
    if plan_start != -1 and plan_end != -1:
        new_content = (content[:plan_start + 7] + 
                      yaml_str + 
                      content[plan_end:])
    else:
        # 如果没找到plan区块，在适当位置插入
        insert_pos = content.find("## ✅ 执行结果 (results)")
        if insert_pos != -1:
            yaml_block = f"```yaml\n{yaml_str}```\n\n---\n\n"
            new_content = content[:insert_pos] + yaml_block + content[insert_pos:]
        else:
            new_content = content
    
    task_file_path = Path(get_daily_task_file())
    task_file_path.write_text(new_content, encoding='utf-8')

def generate_job_id(desc):
    """基于描述生成job ID"""
    import re
    # 移除特殊字符，保留中英文和数字
    clean_desc = re.sub(r'[^\w\u4e00-\u9fff]', '_', desc)
    return clean_desc[:20].lower()

def main():
    """主要处理逻辑"""
    try:
        # 读取hook输入 - Claude Code格式
        stdin_input = sys.stdin.read().strip()
        if not stdin_input:
            sys.exit(0)  # 没有输入，允许继续
            
        hook_data = json.loads(stdin_input)
        tool_name = hook_data.get('tool_name', '')
        tool_input = hook_data.get('tool_input', {})
        
        # 从tool_input中提取参数
        tool_params = tool_input
        
        # 用户输入需要从其他地方获取（UserPromptSubmit hook）
        user_input = ""
        if user_input:
            # 保存用户输入到临时文件供后续分析
            temp_input_file = Path(".claude/last_user_input.tmp")
            temp_input_file.parent.mkdir(exist_ok=True)
            temp_input_file.write_text(user_input, encoding='utf-8')
            
            # 处理控制命令
            if handle_control_commands(user_input):
                sys.exit(0)  # 控制命令已处理，允许继续
        
        # 只处理特定工具
        if tool_name not in ['Write', 'Edit', 'Bash', 'MultiEdit']:
            sys.exit(0)  # 允许其他工具正常执行
        
        # 检查是否应该拦截
        if not should_intercept_operation():
            # 记录正常执行的操作
            log_msg = f"[{datetime.now().strftime('%H:%M:%S')}] 正常执行 {tool_name}: {tool_params.get('command', tool_params.get('file_path', 'unknown'))}\n"
            Path("logs").mkdir(exist_ok=True)
            with open("logs/claude_normal.log", "a", encoding='utf-8') as f:
                f.write(log_msg)
            sys.exit(0)  # 允许正常执行
        
        # 检查是否在白名单中的bash命令
        if tool_name == 'Bash':
            cmd = tool_params.get('command', '')
            whitelist = ['git status', 'git diff', 'git log', 'ls', 'dir', 'pwd']
            if any(cmd.startswith(white_cmd) for white_cmd in whitelist):
                sys.exit(0)  # 允许白名单命令执行
        
        # 执行拦截操作
        print("🔄 检测到规划模式 - 操作已拦截并记录到执行计划")
        
        # 加载当前任务文件
        content, plan_data = load_daily_task_file()
        
        if not plan_data:
            today_str = datetime.now().strftime("%Y-%m-%d")
            plan_data = {
                'plan': {
                    'version': f'{today_str}-01',
                    'context': 'Claude规划模式任务记录',
                    'jobs': []
                }
            }
        
        # 生成新的job条目
        if tool_name == 'Write':
            file_path = tool_params.get('file_path', '')
            desc = f"创建文件 {os.path.basename(file_path)}"
            cmd = f"echo 'Creating file {file_path}' && touch \"{file_path}\""
            produces = [file_path]
            
        elif tool_name == 'Edit' or tool_name == 'MultiEdit':
            file_path = tool_params.get('file_path', '')
            desc = f"编辑文件 {os.path.basename(file_path)}"
            cmd = f"echo 'Editing file {file_path}'"
            produces = [file_path]
            
        elif tool_name == 'Bash':
            cmd = tool_params.get('command', '')
            desc = tool_params.get('description', f"执行命令: {cmd[:30]}...")
            produces = ["logs/bash_output.log"]
        
        job_id = generate_job_id(desc)
        
        # 检查是否已存在相同job
        jobs = plan_data['plan'].get('jobs', [])
        existing_job = None
        for job in jobs:
            if job.get('id') == job_id:
                existing_job = job
                break
        
        if existing_job:
            # 更新existing job
            existing_job['desc'] = desc
            existing_job['cmd'] = cmd
            existing_job['produces'] = produces
        else:
            # 添加新job
            new_job = {
                'id': job_id,
                'desc': desc,
                'cmd': cmd,
                'requires': [],
                'produces': produces,
                'timeout': 300
            }
            jobs.append(new_job)
            plan_data['plan']['jobs'] = jobs
        
        # 保存更新后的任务文件
        save_daily_task_file(content, plan_data)
        
        # 记录日志
        log_msg = f"[{datetime.now().strftime('%H:%M:%S')}] 已拦截 {tool_name}: {desc}\n"
        Path("logs").mkdir(exist_ok=True)
        with open("logs/claude_intercepted.log", "a", encoding='utf-8') as f:
            f.write(log_msg)
        
        # 返回拦截消息
        print(f"✅ 已记录到执行计划: {desc}")
        sys.exit(1)  # 阻止工具执行
        
    except Exception as e:
        # 记录错误但不阻止执行
        Path("logs").mkdir(exist_ok=True)
        with open("logs/hook_errors.log", "a", encoding='utf-8') as f:
            f.write(f"[{datetime.now()}] PostToolUse Hook错误: {str(e)}\n")
            f.write(f"输入内容: {stdin_input[:200]}...\n")
        sys.exit(0)

if __name__ == "__main__":
    main()