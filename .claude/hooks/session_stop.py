#!/usr/bin/env python3
"""
Session Stop Hook - 会话结束时自动总结并更新开发文档
"""
import sys
import os
from datetime import datetime
from pathlib import Path

def update_session_log():
    """更新会话记录到开发文档"""
    try:
        dev_doc_path = Path("开发文档.md")
        if not dev_doc_path.exists():
            return
        
        content = dev_doc_path.read_text(encoding='utf-8')
        
        # 查找会话记录区域
        session_start = content.find("## 📝 会话记录")
        if session_start == -1:
            return
        
        # 生成时间戳和总结
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # 读取本次会话的拦截日志来生成总结
        summary = generate_session_summary()
        
        # 在会话记录区域添加新条目
        session_section = content[session_start:]
        next_section = session_section.find("\n\n**下一步**")
        
        if next_section != -1:
            current_log = session_section[:next_section]
            next_step = session_section[next_section:]
            
            new_entry = f"\n\n**{timestamp}** - 会话结束总结  \n{summary}"
            
            updated_session = current_log + new_entry + next_step
            new_content = content[:session_start] + updated_session
        else:
            new_entry = f"\n\n**{timestamp}** - 会话结束总结  \n{summary}"
            new_content = content + new_entry
        
        dev_doc_path.write_text(new_content, encoding='utf-8')
        
        # 记录到单独的日志文件
        log_path = Path("logs") / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        log_path.parent.mkdir(exist_ok=True)
        
        with open(log_path, "w", encoding='utf-8') as f:
            f.write(f"会话结束时间: {timestamp}\n")
            f.write(f"总结: {summary}\n")
            
    except Exception as e:
        # 错误记录但不影响主流程
        error_log = Path("logs/hook_errors.log")
        error_log.parent.mkdir(exist_ok=True)
        with open(error_log, "a", encoding='utf-8') as f:
            f.write(f"[{datetime.now()}] Session Stop Hook错误: {str(e)}\n")

def generate_session_summary():
    """基于拦截日志生成会话总结"""
    try:
        intercept_log = Path("logs/claude_intercepted.log")
        if not intercept_log.exists():
            return "- 无拦截操作记录"
        
        lines = intercept_log.read_text(encoding='utf-8').strip().split('\n')
        recent_lines = lines[-10:]  # 最近10条记录
        
        if not recent_lines or recent_lines == ['']:
            return "- 无拦截操作记录"
        
        summary = "- 本次会话拦截操作:\n"
        for line in recent_lines:
            if line.strip():
                # 提取操作描述
                if "已拦截" in line:
                    parts = line.split("已拦截")
                    if len(parts) > 1:
                        operation = parts[1].strip()
                        summary += f"  - {operation}\n"
        
        return summary.rstrip()
        
    except Exception:
        return "- 总结生成失败"

def main():
    """主要处理逻辑"""
    try:
        # 更新开发文档
        update_session_log()
        
        print("✅ 会话总结已更新到开发文档")
        
    except Exception as e:
        print(f"❌ Session Stop Hook执行失败: {str(e)}")

if __name__ == "__main__":
    main()