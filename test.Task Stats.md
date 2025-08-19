# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this repository.

## Important
- ALL instructions within this document MUST BE FOLLOWED, these are not optional unless explicitly stated.
- ASK FOR CLARIFICATION If you are uncertain of any of thing within the document.
- DO NOT edit more code than you have to.
- DO NOT WASTE TOKENS, be succinct and concise.

## Task Cost and Usage Information Retrieval
- IMPERATIVE: ANY time the user mentions "task stats", "get task stats", "last task stats", or similar variations, IMMEDIATELY use the automated task stats script without question.

### Task Stats Script Usage:
**Primary Command**: `bash "/path/to/project/.claude/functions/task/task_stats.sh"`

**Script Options:**
- `bash .claude/functions/task/task_stats.sh` - Auto-detects and analyzes most recent Task session
- `bash .claude/functions/task/task_stats.sh session_id.jsonl` - Analyzes specific session file

### IMPORTANT RULES:
- Execute the task_stats.sh script immediately when task stats are requested
- The script auto-detects the most recent Task session or accepts a specific session file

Script Implementation

Customization Required
You must update the CLAUDE_DIR path in the script below to match your project's Claude directory structure.

#!/bin/bash

# Task Stats Script - Extracts Claude Code Task operation breakdowns
# Usage: ./task_stats.sh [session_file.jsonl]

# CUSTOMIZE THIS PATH for your project
CLAUDE_DIR="$HOME/.claude/projects/your-project-name-here"

# Find latest session with Task operations
find_task_session() {
    # Get sessions sorted by modification time (newest first)
    for session in $(ls -t "$CLAUDE_DIR"/*.jsonl 2>/dev/null); do
        # Check if this session has sidechain operations AND recent timestamps
        if grep -q '"isSidechain":true' "$session" 2>/dev/null; then
            # Get the newest timestamp from this session
            local newest_timestamp=$(grep '"isSidechain":true' "$session" | tail -1 | grep -o '"timestamp":"[^"]*"' | cut -d'"' -f4)
            if [[ -n "$newest_timestamp" ]]; then
                # Check if the timestamp is recent (within last hour)
                local timestamp_epoch=$(date -d "$newest_timestamp" +%s 2>/dev/null || echo "0")
                local current_epoch=$(date +%s)
                local time_diff=$((current_epoch - timestamp_epoch))
                
                # If within last hour (3600 seconds), this is likely the current session
                if [[ $time_diff -lt 3600 ]]; then
                    echo "$session"
                    return 0
                fi
            fi
        fi
    done
    
    # Fallback: return the most recent session with sidechain operations
    for session in $(ls -t "$CLAUDE_DIR"/*.jsonl 2>/dev/null); do
        if grep -q '"isSidechain":true' "$session" 2>/dev/null; then
            echo "$session"
            return 0
        fi
    done
    return 1
}

# Display task breakdown
show_breakdown() {
    local session="$1"
    local basename_session=$(basename "$session")
    
    echo "Analyzing: $basename_session"
    echo ""
    
    # Get task description from the most recent Task call
    local last_task_line=$(grep -n '"name":"Task"' "$session" | tail -1 | cut -d: -f1)
    local task_desc=$(tail -n +$((last_task_line)) "$session" | head -1 | grep -o '"description":"[^"]*"' | sed 's/"description":"\([^"]*\)"/\1/')
    [[ -z "$task_desc" ]] && task_desc="Task Operation"
    
    # Get tokens and tool count from ALL sidechain operations in this session
    local all_sidechain_ops=$(grep '"isSidechain":true' "$session")
    local input_tokens=$(echo "$all_sidechain_ops" | grep -o '"input_tokens":[0-9]*' | grep -o '[0-9]*' | awk '{sum += $1} END {print sum}')
    local cache_creation_tokens=$(echo "$all_sidechain_ops" | grep -o '"cache_creation_input_tokens":[0-9]*' | grep -o '[0-9]*' | awk '{sum += $1} END {print sum}')
    local cache_read_tokens=$(echo "$all_sidechain_ops" | grep -o '"cache_read_input_tokens":[0-9]*' | grep -o '[0-9]*' | awk '{sum += $1} END {print sum}')
    local output_tokens=$(echo "$all_sidechain_ops" | grep -o '"output_tokens":[0-9]*' | grep -o '[0-9]*' | awk '{sum += $1} END {print sum}')
    local tokens=$((${input_tokens:-0} + ${cache_creation_tokens:-0} + ${cache_read_tokens:-0} + ${output_tokens:-0}))
    local tool_count=$(echo "$all_sidechain_ops" | wc -l)
    
    # Get the most recent Task operation block by looking for Task tool calls
    local last_task_line=$(grep -n '"name":"Task"' "$session" | tail -1 | cut -d: -f1)
    local recent_operations=$(tail -n +$((last_task_line)) "$session" | grep '"isSidechain":true')
    
    # Calculate total cost and duration from recent sidechain operations only
    local total_cost=$(echo "$recent_operations" | grep -o '"costUSD":[0-9.]*' | cut -d: -f2 | awk '{sum += $1} END {printf "%.4f", sum}')
    local total_duration_ms=$(echo "$recent_operations" | grep -o '"durationMs":[0-9]*' | cut -d: -f2 | awk '{sum += $1} END {print sum}')
    
    # Get first and last timestamps for elapsed time calculation from recent operations
    local first_timestamp=$(echo "$recent_operations" | head -1 | grep -o '"timestamp":"[^"]*"' | cut -d'"' -f4)
    local last_timestamp=$(echo "$recent_operations" | tail -1 | grep -o '"timestamp":"[^"]*"' | cut -d'"' -f4)
    
    # Convert timestamps to epoch and calculate elapsed time
    local first_epoch=$(date -d "$first_timestamp" +%s 2>/dev/null || echo "0")
    local last_epoch=$(date -d "$last_timestamp" +%s 2>/dev/null || echo "0")
    local elapsed_sec=$((last_epoch - first_epoch))
    
    # Convert durations
    local duration_sec=$(echo "scale=1; ${total_duration_ms:-0} / 1000" | bc -l 2>/dev/null || echo "0.0")
    local efficiency="0.0"
    if [[ $elapsed_sec -gt 0 ]]; then
        efficiency=$(echo "scale=1; ($duration_sec / $elapsed_sec) * 100" | bc -l 2>/dev/null || echo "0.0")
    fi
    
    echo "=== TASK AGENT INTERNAL BREAKDOWN ==="
    echo "Task: \"$task_desc\""
    echo "Total Cost: \${total_cost:-0.0000} | Sequential Duration: ${duration_sec}s | Actual Elapsed: ${elapsed_sec}s | Agent: claude-sonnet-4-20250514"
    echo "Efficiency: ${efficiency}% (${duration_sec}s/${elapsed_sec}s)"
    echo ""
    echo "┌─ OPERATION TIMELINE ──────────────────────────────────────────────────────────┐"
    
    # Find max duration for relative bar chart scaling
    local max_duration=$(echo "$recent_operations" | grep -o '"durationMs":[0-9]*' | cut -d: -f2 | sort -nr | head -1)
    local max_dur_sec=$(echo "scale=1; ${max_duration:-0} / 1000" | bc -l 2>/dev/null || echo "0.0")
    
    # Get all sidechain operations from the most recent Task operation
    echo "$recent_operations" | while IFS= read -r line; do
        # Extract fields
        local timestamp=$(echo "$line" | grep -o '"timestamp":"[^"]*"' | cut -d'"' -f4)
        local cost=$(echo "$line" | grep -o '"costUSD":[0-9.]*' | cut -d: -f2)
        local duration=$(echo "$line" | grep -o '"durationMs":[0-9]*' | cut -d: -f2)
        
        # Format time
        local time_str=$(date -d "$timestamp" '+%H:%M:%S' 2>/dev/null || echo "XX:XX:XX")
        local dur_sec=$(echo "scale=1; ${duration:-0} / 1000" | bc -l 2>/dev/null || echo "0.0")
        
        # Determine operation
        local operation="Agent Operation"
        if echo "$line" | grep -q '"name":"Write"'; then
            local filepath=$(echo "$line" | grep -o '"file_path":"[^"]*"' | cut -d'"' -f4)
            operation="Write $(basename "$filepath" 2>/dev/null || echo "file")"
        elif echo "$line" | grep -q '"name":"Bash"'; then
            operation="Bash Command"
        elif echo "$line" | grep -q '"name":"LS"'; then
            operation="List Directory"
        elif echo "$line" | grep -q '"name":"Read"'; then
            local filepath=$(echo "$line" | grep -o '"file_path":"[^"]*"' | cut -d'"' -f4)
            operation="Read $(basename "$filepath" 2>/dev/null || echo "file")"
        elif echo "$line" | grep -q '"name":"Edit"'; then
            local filepath=$(echo "$line" | grep -o '"file_path":"[^"]*"' | cut -d'"' -f4)
            operation="Edit $(basename "$filepath" 2>/dev/null || echo "file")"
        elif echo "$line" | grep -q '"name":"MultiEdit"'; then
            local filepath=$(echo "$line" | grep -o '"file_path":"[^"]*"' | cut -d'"' -f4)
            operation="MultiEdit $(basename "$filepath" 2>/dev/null || echo "file")"
        elif echo "$line" | grep -q '"name":"Glob"'; then
            operation="Search Files"
        elif echo "$line" | grep -q '"name":"Grep"'; then
            operation="Search Content"
        elif echo "$line" | grep -q '"name":"Task"'; then
            operation="Task Launch"
        elif echo "$line" | grep -q 'Summary.*Created.*Files'; then
            operation="Task Summary"
        else
            # Try to extract any tool name
            local tool_name=$(echo "$line" | grep -o '"name":"[^"]*"' | cut -d'"' -f4)
            if [[ -n "$tool_name" ]]; then
                operation="$tool_name Tool"
            else
                # Look for text content to infer operation
                if echo "$line" | grep -q '"I'\''ll create"'; then
                    operation="Task Planning"
                elif echo "$line" | grep -q '"Successfully created"'; then
                    operation="Task Summary"
                elif echo "$line" | grep -q '"Now I'\''ll"'; then
                    operation="Task Progress"
                elif echo "$line" | grep -q '"Let me"'; then
                    operation="Task Processing"
                elif echo "$line" | grep -q '"All.*demo files"'; then
                    operation="Task Completion"
                else
                    operation="Task Reasoning"
                fi
            fi
        fi
        
        # Calculate relative progress bar (14 chars max)
        local bars=1
        if [[ $(echo "${max_dur_sec} > 0" | bc -l 2>/dev/null) -eq 1 ]]; then
            bars=$(echo "scale=1; (${dur_sec:-0} / ${max_dur_sec}) * 14 + 0.5" | bc -l 2>/dev/null)
            bars=$(echo "scale=0; $bars / 1" | bc -l 2>/dev/null)  # Convert to integer
            [[ -z "$bars" || "$bars" -eq 0 ]] && bars=1
            [[ "$bars" -gt 14 ]] && bars=14
        fi
        local progress=$(printf "█%.0s" $(seq 1 $bars))
        if [[ $bars -lt 14 ]]; then
            progress="$progress$(printf ".%.0s" $(seq 1 $((14 - bars))))"
        fi
        
        # Only show operations with non-zero cost
        if [[ $(echo "${cost:-0} > 0" | bc -l 2>/dev/null) -eq 1 ]]; then
            # Format output with clipped operation name
            printf "│ %s | %-28s | \$%6.4f | %5.1fs | %s\n" \
                "$time_str" "${operation:0:28}" "${cost:-0}" "$dur_sec" "$progress"
        fi
    done
    
    echo "└───────────────────────────────────────────────────────────────────────────────┘"
    echo ""
    echo "TOTALS: $(printf "%'d" ${tokens:-0} 2>/dev/null || echo ${tokens:-0}) tokens | ${tool_count:-0} tool uses | Sidechain: Yes"
}

# Main execution
if [[ $# -eq 1 ]]; then
    session_file="$CLAUDE_DIR/$1"
    [[ ! -f "$session_file" ]] && { echo "Error: File not found: $1"; exit 1; }
else
    session_file=$(find_task_session)
    [[ $? -ne 0 ]] && { echo "No Task sessions found"; exit 1; }
fi

show_breakdown "$session_file"