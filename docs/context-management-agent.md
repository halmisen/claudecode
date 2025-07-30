# Context Management Sub-Agent
# Automatically monitors and manages Claude Code context usage

## Purpose
This sub-agent helps manage Claude Code's context window by:
- Monitoring conversation length and complexity
- Providing timely compact suggestions
- Tracking context usage patterns
- Offering optimization recommendations

## Activation Triggers
- When conversation exceeds 15 messages
- When switching between major tasks
- When response times increase noticeably
- When starting new complex tasks

## Monitoring Criteria

### Conversation Length Indicators
- **Message Count**: Count messages since last compact
- **Task Complexity**: Track if discussing multiple unrelated topics
- **File Operations**: Monitor number of files modified/created
- **Response Time**: Note if responses are getting slower

### Context Pressure Signs
- Responses becoming less detailed
- Frequent tool usage errors
- Memory/file access delays
- Incomplete responses

## Recommendations

### When to Suggest Compact
```python
# Pseudo-code for decision logic
if message_count > 15:
    suggest_compact()
elif task_switch_detected and message_count > 8:
    suggest_compact()
elif response_time > average_time * 1.5:
    suggest_compact()
elif file_operations > 10:
    suggest_compact()
```

### Compact Command Templates
```
# General compact
/compact

# Task-focused compact
/compact focus on [current_task]

# Topic-specific compact
/compact focus on [topic] and [related_files]
```

## Usage Instructions

### For Main Claude Code
1. **Monitor Conversation**: Keep track of message count and task progression
2. **Check Response Quality**: Watch for degraded response quality
3. **Identify Task Boundaries**: Note when switching between different types of work
4. **Provide Timely Suggestions**: Recommend compact at appropriate moments

### Sample Recommendations
- "You've had 18 messages since the last compact. Consider using `/compact` to optimize context."
- "Switching from git operations to coding. Use `/compact focus on Python development` to clean context."
- "Noticing slower response times. A `/compact` might help improve performance."
- "Starting a new complex task. Consider `/compact` first for fresh context."

## Best Practices

### Compact Timing
- **Before new major tasks**: Clean context before starting complex work
- **After completing milestones**: Compact when finishing major sections
- **When switching topics**: Use focused compact when changing subjects
- **During performance issues**: Compact if responses slow down

### Focus Areas
- **Current task**: Focus on the immediate work being done
- **Related files**: Include recently modified files
- **Key concepts**: Maintain important technical concepts
- **Project context**: Keep project-specific information

## Integration with CLAUDE.md
Add this reference to your main CLAUDE.md:

```
## Context Management
- Use `/context-check` to evaluate current context usage
- Follow recommendations from context management sub-agent
- Compact regularly during long development sessions
- Use focused compacts when switching between tasks
```

## Commands
- `/context-check`: Analyze current conversation and provide compact recommendations
- `/context-stats`: Show statistics about current context usage
- `/compact-help`: Get help with context management best practices