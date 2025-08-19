# Task Statistics Output Directory

This directory contains standardized task performance statistics and cost analysis reports.

## File Naming Convention
- Format: `task_stats_{timestamp}_{session_id}.json`
- Example: `task_stats_20250819_143025_abcd1234.json`

## JSON Output Schema
```json
{
  "session_id": "string",
  "timestamp": "ISO 8601 timestamp",
  "tokens": {
    "input": "number",
    "output": "number", 
    "total": "number"
  },
  "duration": {
    "seconds": "number",
    "human_readable": "string"
  },
  "cost_breakdown": {
    "input_cost": "number",
    "output_cost": "number",
    "total_cost": "number",
    "currency": "USD"
  },
  "steps": [
    {
      "step_name": "string",
      "tokens_used": "number",
      "duration_seconds": "number",
      "status": "completed|failed|skipped"
    }
  ],
  "errors": [
    {
      "error_type": "string",
      "message": "string",
      "timestamp": "ISO 8601"
    }
  ],
  "summary": {
    "success_rate": "percentage",
    "efficiency_score": "number",
    "recommendations": ["string"]
  }
}
```

## CSV Summary Format
Companion CSV files provide tabular data for easy analysis:
- `task_stats_summary.csv` - Aggregated statistics
- Columns: session_id, timestamp, total_tokens, duration_seconds, total_cost, success_rate, efficiency_score