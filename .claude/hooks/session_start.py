#!/usr/bin/env python3
"""
Session Start Hook - 会话开始时注入开发文档上下文
"""
import sys
import os
from pathlib import Path
import re

def extract_context():
    """从开发文档提取关键上下文"""
    try:
        dev_doc_path = Path("开发文档.md")
        if not dev_doc_path.exists():
            return "开发文档未找到，这是全新的会话。"
        
        content = dev_doc_path.read_text(encoding='utf-8')
        
        # 提取当前迭代状态
        status_match = re.search(r'## 📋 当前迭代状态\n\n(.*?)\n---', content, re.DOTALL)
        status = status_match.group(1) if status_match else "状态未知"
        
        # 提取plan概要
        plan_match = re.search(r'```yaml\nplan:(.*?)```', content, re.DOTALL)
        if plan_match:
            plan_content = plan_match.group(1)
            # 提取关键信息
            version_match = re.search(r'version:\s*"([^"]*)"', plan_content)
            context_match = re.search(r'context:\s*"([^"]*)"', plan_content)
            jobs_count = len(re.findall(r'- id:', plan_content))
            
            version = version_match.group(1) if version_match else "未知"
            context_desc = context_match.group(1) if context_match else "无描述"
            
            plan_summary = f"执行计划 v{version}: {context_desc}，共{jobs_count}个任务"
        else:
            plan_summary = "暂无执行计划"
        
        # 提取最近的会话记录
        session_match = re.search(r'## 📝 会话记录\n\n(.*?)(?:\n\n\*\*下一步\*\*|$)', content, re.DOTALL)
        if session_match:
            session_content = session_match.group(1)
            recent_entries = session_content.strip().split('\n\n**')[-3:]  # 最近3条
            recent_summary = "最近活动:\n" + '\n'.join([f"- {entry.split(' - ')[1] if ' - ' in entry else entry}" 
                                                      for entry in recent_entries if entry.strip()])
        else:
            recent_summary = "无会话历史"
        
        # 检查pending的errors
        errors_match = re.search(r'## ❌ 错误日志 \(errors\)\n\n(.*?)(?:\n\n---|$)', content, re.DOTALL)
        has_errors = errors_match and errors_match.group(1).strip() and "错误信息将由" not in errors_match.group(1)
        
        # 构建上下文消息
        context_msg = f"""
🔄 **会话恢复** - 基于开发文档状态

**当前状态**: {status.strip()}

**{plan_summary}**

{recent_summary}

{"⚠️ **注意**: 上次会话存在未解决的错误，请检查errors区块" if has_errors else "✅ 无未解决错误"}

---
💡 提示: 使用 `开发文档.md` 中的执行计划，通过Gemini CLI执行具体操作
        """.strip()
        
        return context_msg
        
    except Exception as e:
        return f"⚠️ 上下文加载失败: {str(e)}"

def main():
    """主要处理逻辑"""
    try:
        context = extract_context()
        print(context)
        
    except Exception as e:
        print(f"❌ Session Start Hook执行失败: {str(e)}")

if __name__ == "__main__":
    main()