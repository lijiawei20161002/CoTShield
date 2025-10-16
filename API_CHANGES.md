# CoTShield API Changes - Real Implementation

## Overview
Replaced all dummy placeholders with actual working API implementations, including persistent database storage and configurable parameters.

## Changes Made

### 1. Database Implementation (SQLite)

**Replaced:** In-memory dictionary (`traces_db = {}`)
**With:** SQLite database with persistent storage

**New Features:**
- `traces.db` - SQLite database file for persistent storage
- Proper schema with indexed fields for performance
- Transaction support with context managers
- Automatic database initialization on startup

**Schema:**
```sql
CREATE TABLE traces (
    id TEXT PRIMARY KEY,
    task TEXT NOT NULL,
    reasoning TEXT NOT NULL,
    output TEXT NOT NULL,
    model_name TEXT,
    context TEXT,
    sensitivity REAL,
    use_reconstructor INTEGER,
    risk_score REAL,
    flag_count INTEGER,
    created_at TEXT NOT NULL,
    analysis_json TEXT NOT NULL
)
```

**Indexes:**
- `idx_created_at` - For chronological ordering
- `idx_risk_score` - For risk-based filtering

### 2. Configurable Sensitivity Parameter

**Replaced:** Hardcoded `sensitivity=0.5`
**With:** User-configurable parameter from UI and API

**Changes:**
- Added `sensitivity` field to `TraceSubmission` model (default: 0.5)
- Added sensitivity input field in web UI (range: 0.0 - 1.0)
- JavaScript validation for sensitivity range
- Analysis endpoint now uses `submission.sensitivity` parameter

### 3. New API Endpoints

#### DELETE `/api/traces/{trace_id}`
Delete a specific trace from the database.

**Response:**
```json
{
  "message": "Trace deleted successfully",
  "trace_id": "trace_20250101_120000_123456"
}
```

#### GET `/api/traces/{trace_id}/export`
Export a single trace as downloadable JSON file.

**Response:** File download (`{trace_id}.json`)

#### POST `/api/traces/export-all`
Export all traces as a single JSON file.

**Response:** File download (`cotshield_traces_YYYYMMDD_HHMMSS.json`)

**Export Format:**
```json
{
  "export_date": "2025-01-15T12:00:00",
  "trace_count": 10,
  "traces": [...]
}
```

### 4. Updated Existing Endpoints

#### POST `/api/analyze`
**Changes:**
- Now accepts `sensitivity` parameter (optional, default: 0.5)
- Stores complete trace data in database
- Generates unique timestamp-based IDs
- Returns trace ID for future reference

**Request:**
```json
{
  "task": "...",
  "reasoning": "...",
  "output": "...",
  "model_name": "gpt-4",
  "sensitivity": 0.7
}
```

#### GET `/api/traces`
**Changes:**
- Queries database instead of in-memory dict
- Returns enhanced metadata (risk_score, flag_count, created_at)
- Orders by creation date (newest first)
- Truncates long task descriptions

**Response:**
```json
{
  "traces": [
    {
      "id": "trace_20250115_120000_123456",
      "task": "What is the capital of...",
      "model_name": "gpt-4",
      "risk_score": 0.85,
      "flag_count": 3,
      "created_at": "2025-01-15T12:00:00"
    }
  ],
  "count": 1
}
```

#### GET `/api/traces/{trace_id}`
**Changes:**
- Fetches from database
- Returns additional metadata (sensitivity, use_reconstructor, created_at)
- Parses stored JSON analysis data

## Usage Examples

### Analyze Trace with Custom Sensitivity
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Is Sydney the capital of Australia?",
    "reasoning": "Sydney is the largest city...",
    "output": "Yes, Sydney is the capital.",
    "model_name": "gpt-4",
    "sensitivity": 0.8
  }'
```

### Export Single Trace
```bash
curl -O http://localhost:8000/api/traces/trace_20250115_120000_123456/export
```

### Export All Traces
```bash
curl -X POST http://localhost:8000/api/traces/export-all -O
```

### Delete Trace
```bash
curl -X DELETE http://localhost:8000/api/traces/trace_20250115_120000_123456
```

## Migration Notes

### Backward Compatibility
- All existing API endpoints remain functional
- Default sensitivity value (0.5) maintains previous behavior
- No breaking changes to response formats

### Database Location
- Database file: `CoTShield/ui/traces.db`
- Automatically created on first run
- Can be backed up/restored by copying the file

### Data Persistence
- All traces now persist across server restarts
- No data loss when restarting the viewer
- Database grows with usage (consider cleanup strategy)

## Testing

Start the viewer:
```bash
cd /workspace/CoTShield
python -m ui.viewer
```

Or use the CLI:
```bash
python -m monitor.cli viewer --host 0.0.0.0 --port 8000
```

Then navigate to `http://localhost:8000` and test:
1. Submit a trace with custom sensitivity
2. View traces list
3. Export individual traces
4. Export all traces
5. Delete traces

## Future Enhancements

Consider adding:
1. Search/filter traces by risk score, date range, or model
2. Bulk delete operations
3. Database cleanup/archival utilities
4. Rate limiting for API endpoints
5. Authentication/authorization
6. Pagination for large trace lists
7. Real-time analysis progress updates
8. Comparison view for multiple traces
