"""
CoT Reasoning Trace Viewer - Interactive web interface for reviewing reasoning chains.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
from pathlib import Path


class TraceSubmission(BaseModel):
    """Model for submitting a trace for analysis."""
    task: str
    reasoning: str
    output: str
    model_name: Optional[str] = "unknown"
    context: Optional[str] = None


class AnalysisRequest(BaseModel):
    """Model for requesting analysis."""
    trace_id: str
    sensitivity: Optional[float] = 0.5
    use_reconstructor: Optional[bool] = False


app = FastAPI(title="CoTShield Viewer", version="0.2.0")


# In-memory storage (in production, use a database)
traces_db = {}
trace_counter = 0


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the main viewer page."""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CoTShield - Reasoning Trace Viewer</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }

        .content {
            padding: 30px;
        }

        .section {
            margin-bottom: 30px;
        }

        .section h2 {
            color: #333;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }

        textarea, input[type="text"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 6px;
            font-family: inherit;
            font-size: 14px;
            transition: border-color 0.3s;
        }

        textarea:focus, input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
        }

        textarea {
            min-height: 150px;
            resize: vertical;
        }

        .input-label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: 500;
        }

        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 6px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        .btn:active {
            transform: translateY(0);
        }

        .results {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            display: none;
        }

        .results.visible {
            display: block;
        }

        .flag-item {
            background: white;
            padding: 15px;
            margin-bottom: 15px;
            border-left: 4px solid #667eea;
            border-radius: 4px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }

        .flag-item.high-severity {
            border-left-color: #e74c3c;
        }

        .flag-item.medium-severity {
            border-left-color: #f39c12;
        }

        .flag-item.low-severity {
            border-left-color: #3498db;
        }

        .flag-type {
            font-weight: 600;
            color: #667eea;
            margin-bottom: 5px;
        }

        .flag-severity {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 8px;
        }

        .severity-high {
            background: #e74c3c;
            color: white;
        }

        .severity-medium {
            background: #f39c12;
            color: white;
        }

        .severity-low {
            background: #3498db;
            color: white;
        }

        .snippet {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            overflow-x: auto;
        }

        .risk-score {
            font-size: 2em;
            font-weight: 700;
            text-align: center;
            margin: 20px 0;
        }

        .risk-low { color: #27ae60; }
        .risk-medium { color: #f39c12; }
        .risk-high { color: #e74c3c; }

        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }

        .stat-box {
            background: white;
            padding: 15px;
            border-radius: 6px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }

        .stat-value {
            font-size: 2em;
            font-weight: 700;
            color: #667eea;
        }

        .stat-label {
            color: #666;
            margin-top: 5px;
        }

        .loading {
            text-align: center;
            padding: 20px;
            color: #667eea;
            font-weight: 600;
        }

        .error {
            background: #fee;
            color: #c33;
            padding: 15px;
            border-radius: 6px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ CoTShield Viewer</h1>
            <p>Revealing AI's Hidden Reasoning to Defend Free Inquiry</p>
        </div>

        <div class="content">
            <div class="section">
                <h2>Submit Reasoning Trace</h2>
                <div style="margin-bottom: 15px;">
                    <label class="input-label">Task / Prompt</label>
                    <textarea id="task" placeholder="Enter the task or prompt given to the model..."></textarea>
                </div>
                <div style="margin-bottom: 15px;">
                    <label class="input-label">Chain-of-Thought Reasoning</label>
                    <textarea id="reasoning" placeholder="Enter the model's chain-of-thought reasoning..."></textarea>
                </div>
                <div style="margin-bottom: 15px;">
                    <label class="input-label">Final Output</label>
                    <textarea id="output" placeholder="Enter the model's final output..."></textarea>
                </div>
                <div style="margin-bottom: 15px;">
                    <label class="input-label">Model Name (optional)</label>
                    <input type="text" id="model_name" placeholder="e.g., gpt-4, claude-3">
                </div>
                <button class="btn" onclick="analyzeTrace()">🔍 Analyze Trace</button>
            </div>

            <div id="results" class="results">
                <h2>Analysis Results</h2>
                <div id="results-content"></div>
            </div>
        </div>
    </div>

    <script>
        async function analyzeTrace() {
            const task = document.getElementById('task').value;
            const reasoning = document.getElementById('reasoning').value;
            const output = document.getElementById('output').value;
            const model_name = document.getElementById('model_name').value || 'unknown';

            if (!task || !reasoning || !output) {
                alert('Please fill in all required fields (task, reasoning, and output)');
                return;
            }

            const resultsDiv = document.getElementById('results');
            const resultsContent = document.getElementById('results-content');

            resultsDiv.classList.add('visible');
            resultsContent.innerHTML = '<div class="loading">Analyzing reasoning trace...</div>';

            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        task,
                        reasoning,
                        output,
                        model_name
                    })
                });

                if (!response.ok) {
                    throw new Error('Analysis failed');
                }

                const data = await response.json();
                displayResults(data);
            } catch (error) {
                resultsContent.innerHTML = `<div class="error">Error: ${error.message}</div>`;
            }
        }

        function displayResults(data) {
            const resultsContent = document.getElementById('results-content');

            let riskClass = 'risk-low';
            if (data.risk_score > 0.7) riskClass = 'risk-high';
            else if (data.risk_score > 0.4) riskClass = 'risk-medium';

            let html = `
                <div class="risk-score ${riskClass}">
                    Risk Score: ${(data.risk_score * 100).toFixed(1)}%
                </div>

                <div class="stats">
                    <div class="stat-box">
                        <div class="stat-value">${data.flag_count}</div>
                        <div class="stat-label">Total Flags</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">${data.severity_distribution.high}</div>
                        <div class="stat-label">High Severity</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">${data.severity_distribution.medium}</div>
                        <div class="stat-label">Medium Severity</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">${data.severity_distribution.low}</div>
                        <div class="stat-label">Low Severity</div>
                    </div>
                </div>
            `;

            if (data.flags && data.flags.length > 0) {
                html += '<h3 style="margin-top: 30px; margin-bottom: 15px;">Detected Issues</h3>';

                data.flags.forEach(flag => {
                    let severityClass = 'low-severity';
                    let severityLabel = 'Low';
                    if (flag.severity > 0.7) {
                        severityClass = 'high-severity';
                        severityLabel = 'High';
                    } else if (flag.severity > 0.4) {
                        severityClass = 'medium-severity';
                        severityLabel = 'Medium';
                    }

                    html += `
                        <div class="flag-item ${severityClass}">
                            <div class="flag-type">${flag.type.toUpperCase().replace('_', ' ')}</div>
                            <div class="flag-severity severity-${severityLabel.toLowerCase()}">
                                ${severityLabel} Severity (${(flag.severity * 100).toFixed(0)}%)
                            </div>
                            <p style="margin: 10px 0;"><strong>Explanation:</strong> ${flag.explanation}</p>
                            <div>
                                <strong>Reasoning snippet:</strong>
                                <div class="snippet">${flag.reasoning_snippet}</div>
                            </div>
                            <div>
                                <strong>Output snippet:</strong>
                                <div class="snippet">${flag.output_snippet}</div>
                            </div>
                        </div>
                    `;
                });
            } else {
                html += '<p style="text-align: center; color: #27ae60; font-size: 1.2em; margin-top: 20px;">✓ No significant issues detected!</p>';
            }

            resultsContent.innerHTML = html;
        }
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


@app.post("/api/analyze")
async def analyze_trace(submission: TraceSubmission):
    """Analyze a reasoning trace and return results."""
    global trace_counter

    try:
        # Import detector
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))

        from monitor.detector import analyze_cot_trace

        # Perform analysis
        result = analyze_cot_trace(
            reasoning=submission.reasoning,
            output=submission.output,
            sensitivity=0.5
        )

        # Store trace
        trace_id = f"trace_{trace_counter}"
        trace_counter += 1

        traces_db[trace_id] = {
            "id": trace_id,
            "task": submission.task,
            "reasoning": submission.reasoning,
            "output": submission.output,
            "model_name": submission.model_name,
            "context": submission.context,
            "analysis": result
        }

        # Format flags for JSON serialization
        formatted_flags = []
        for flag in result["flags"]:
            formatted_flags.append({
                "type": flag.type.value,
                "severity": flag.severity,
                "reasoning_snippet": flag.reasoning_snippet,
                "output_snippet": flag.output_snippet,
                "explanation": flag.explanation,
                "line_number": flag.line_number
            })

        return JSONResponse({
            "trace_id": trace_id,
            "risk_score": result["risk_score"],
            "flag_count": result["flag_count"],
            "severity_distribution": result["severity_distribution"],
            "divergence_types": result["divergence_types"],
            "flags": formatted_flags
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/traces")
async def list_traces():
    """List all stored traces."""
    return JSONResponse({"traces": list(traces_db.keys()), "count": len(traces_db)})


@app.get("/api/traces/{trace_id}")
async def get_trace(trace_id: str):
    """Get a specific trace by ID."""
    if trace_id not in traces_db:
        raise HTTPException(status_code=404, detail="Trace not found")

    trace = traces_db[trace_id]

    # Format flags
    formatted_flags = []
    for flag in trace["analysis"]["flags"]:
        formatted_flags.append({
            "type": flag.type.value,
            "severity": flag.severity,
            "reasoning_snippet": flag.reasoning_snippet,
            "output_snippet": flag.output_snippet,
            "explanation": flag.explanation,
            "line_number": flag.line_number
        })

    return JSONResponse({
        "trace_id": trace["id"],
        "task": trace["task"],
        "reasoning": trace["reasoning"],
        "output": trace["output"],
        "model_name": trace["model_name"],
        "analysis": {
            "risk_score": trace["analysis"]["risk_score"],
            "flag_count": trace["analysis"]["flag_count"],
            "severity_distribution": trace["analysis"]["severity_distribution"],
            "divergence_types": trace["analysis"]["divergence_types"],
            "flags": formatted_flags
        }
    })


def start_viewer(host: str = "0.0.0.0", port: int = 8000):
    """Start the viewer server."""
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start_viewer()
