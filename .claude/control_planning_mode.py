#!/usr/bin/env python3
"""
规划模式控制脚本 - 手动管理Claude+Gemini协作工作流
"""
import sys
from pathlib import Path
import json

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

def show_status():
    """显示当前状态"""
    status = get_planning_mode_status()
    settings = load_settings()
    
    print("=" * 50)
    print("Claude+Gemini 协作工作流状态")
    print("=" * 50)
    
    mode = "[规划模式] 拦截操作" if status else "[正常模式] 直接执行"
    print(f"当前模式: {mode}")
    
    print(f"\n状态文件: .claude/planning_mode.state")
    print(f"开发文档: 开发文档.md")
    print(f"执行日志: logs/")
    
    # 显示触发关键词
    trigger_keywords = settings.get('interception_config', {}).get('trigger_keywords', [])
    if trigger_keywords:
        print(f"\n触发关键词 (自动激活规划模式):")
        for keyword in trigger_keywords[:5]:  # 显示前5个
            print(f"  - {keyword}")
        if len(trigger_keywords) > 5:
            print(f"  ... 及其他 {len(trigger_keywords) - 5} 个")
    
    # 显示绕过关键词
    bypass_keywords = settings.get('interception_config', {}).get('bypass_keywords', [])
    if bypass_keywords:
        print(f"\n绕过关键词 (强制正常执行):")
        for keyword in bypass_keywords:
            print(f"  - {keyword}")
    
    print(f"\n控制命令:")
    control_commands = settings.get('interception_config', {}).get('control_commands', {})
    for cmd, desc in control_commands.items():
        print(f"  {cmd}: {desc}")
    
    print("=" * 50)

def main():
    """主要控制逻辑"""
    if len(sys.argv) < 2:
        print("Claude+Gemini 协作工作流控制工具")
        print("\n用法:")
        print("  python .claude/control_planning_mode.py <command>")
        print("\n可用命令:")
        print("  status    - 显示当前状态")
        print("  on        - 激活规划模式")
        print("  off       - 关闭规划模式")
        print("  toggle    - 切换模式")
        print("  test      - 测试Hook系统")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "status":
        show_status()
    
    elif command == "on":
        if set_planning_mode_status(True):
            print("[SUCCESS] Planning mode activated")
            print("   - Claude Write/Edit/Bash operations will be intercepted")
            print("   - Operations will be recorded in dev doc execution plan") 
            print("   - Use Gemini CLI to execute specific operations")
        else:
            print("[ERROR] Failed to activate planning mode")
    
    elif command == "off":
        if set_planning_mode_status(False):
            print("[SUCCESS] Planning mode deactivated")
            print("   - Claude will execute all operations normally")
            print("   - No interception of Write/Edit/Bash operations")
        else:
            print("[ERROR] Failed to deactivate planning mode")
    
    elif command == "toggle":
        current_status = get_planning_mode_status()
        new_status = not current_status
        
        if set_planning_mode_status(new_status):
            mode = "Planning Mode" if new_status else "Normal Mode" 
            print(f"[SUCCESS] Switched to {mode}")
        else:
            print("[ERROR] Mode switch failed")
    
    elif command == "test":
        print("[TEST] Testing Hook system...")
        
        # 检查配置文件
        settings = load_settings()
        if not settings:
            print("[ERROR] Cannot load Hook configuration file")
            return
        
        print("[OK] Hook configuration file loaded")
        
        # 检查Hook脚本
        hook_script = Path(".claude/hooks/post_tool_use.py")
        if not hook_script.exists():
            print("[ERROR] Hook script does not exist")
            return
        
        print("[OK] Hook script exists")
        
        # 测试Python语法
        try:
            import subprocess
            result = subprocess.run([
                sys.executable, "-m", "py_compile", str(hook_script)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("[OK] Hook script syntax is correct")
            else:
                print(f"[ERROR] Hook script syntax error: {result.stderr}")
                return
        except:
            print("[WARNING] Cannot verify Hook script syntax")
        
        # 检查状态文件
        status = get_planning_mode_status()
        mode_name = "Planning Mode" if status else "Normal Mode"
        print(f"[OK] Current mode: {mode_name}")
        
        print("[COMPLETE] Hook system test finished")
    
    else:
        print(f"[ERROR] Unknown command: {command}")
        print("Use 'python .claude/control_planning_mode.py' to see help")

if __name__ == "__main__":
    main()