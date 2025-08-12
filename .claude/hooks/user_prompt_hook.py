#!/usr/bin/env python3
"""
User Prompt Submit Hook - 捕获用户输入并检查触发关键词
"""
import json
import sys
import os
from datetime import datetime
from pathlib import Path

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

def check_trigger_keywords(user_input):
    """检查用户输入是否包含触发关键词"""
    settings = load_settings()
    trigger_keywords = settings.get('interception_config', {}).get('trigger_keywords', [])
    bypass_keywords = settings.get('interception_config', {}).get('bypass_keywords', [])
    
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

def main():
    """主要处理逻辑"""
    try:
        # 读取hook输入 - UserPromptSubmit格式
        stdin_input = sys.stdin.read().strip()
        if not stdin_input:
            sys.exit(0)  # 没有输入，继续
            
        hook_data = json.loads(stdin_input)
        user_prompt = hook_data.get('prompt', '')
        
        if not user_prompt:
            sys.exit(0)  # 没有用户输入，继续
        
        # 保存用户输入到临时文件供PostToolUse hook使用
        temp_input_file = Path(".claude/last_user_input.tmp")
        temp_input_file.parent.mkdir(exist_ok=True)
        temp_input_file.write_text(user_prompt, encoding='utf-8')
        
        # 处理控制命令
        if handle_control_commands(user_prompt):
            sys.exit(0)  # 控制命令已处理
        
        # 检查触发关键词
        trigger_detected, bypass_detected = check_trigger_keywords(user_prompt)
        
        if bypass_detected:
            # 明确要求绕过，确保规划模式关闭
            set_planning_mode_status(False)
            sys.exit(0)
        
        if trigger_detected:
            # 自动激活规划模式
            set_planning_mode_status(True)
            print("🎯 检测到复杂任务关键词 - 已激活规划模式")
            
            # 记录日志
            log_msg = f"[{datetime.now().strftime('%H:%M:%S')}] 触发词检测: {user_prompt[:50]}...\n"
            Path("logs").mkdir(exist_ok=True)
            with open("logs/trigger_detection.log", "a", encoding='utf-8') as f:
                f.write(log_msg)
        
        sys.exit(0)  # 允许继续
        
    except Exception as e:
        # 记录错误但不阻止执行
        Path("logs").mkdir(exist_ok=True)
        with open("logs/hook_errors.log", "a", encoding='utf-8') as f:
            f.write(f"[{datetime.now()}] UserPrompt Hook错误: {str(e)}\n")
        sys.exit(0)

if __name__ == "__main__":
    main()