import io
import math
import pandas as pd
import numpy as np
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from engine.search import run_hypothesis_search

app = FastAPI(title="Neuro-Symbolic Hypothesis Engine")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

def sanitize_json(obj):
    """
    Recursively replaces NaN, Infinity, and -Infinity with None (JSON null)
    to prevent Safari/WebKit from failing on non-standard JSON tokens.
    """
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    elif isinstance(obj, list):
        return [sanitize_json(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: sanitize_json(val) for key, val in obj.items()}
    return obj

@app.get("/")
def read_root():
    return FileResponse("static/index.html")

@app.post("/api/analyze")
async def analyze_data(
    file: UploadFile = File(...),
    domain_context: str = Form(""),
    data_description: str = Form("")
):
    # 1. Read uploaded file
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV file: {str(e)}")
        
    # 2. Extract numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(numeric_cols) < 2:
        raise HTTPException(status_code=400, detail="CSV must contain at least 2 numeric columns.")
        
    # Smart detection of X and Y
    # Try to find a target column matching common names
    target_keywords = ['return', 'y', 'target', 'pnl', 'profit', 'exit_price']
    y_col = None
    for col in numeric_cols:
        if any(kw in col.lower() for kw in target_keywords):
            y_col = col
            break
            
    # If no keyword matches, default to the last numeric column
    if not y_col:
        y_col = numeric_cols[-1]
        
    # X is the first numeric column that is not Y
    x_col = [col for col in numeric_cols if col != y_col][0]
    
    # Drop rows with NaNs in these columns
    df_clean = df[[x_col, y_col]].dropna()
    x_data = df_clean[x_col].to_numpy()
    y_data = df_clean[y_col].to_numpy()
    
    if len(x_data) < 5:
        raise HTTPException(status_code=400, detail="At least 5 valid data points are required.")
        
    # 3. Create data summary for the LLM
    summary = f"""Columns: '{x_col}' (input) and '{y_col}' (target).
Data Points Count: {len(x_data)}
X Range: [{float(x_data.min())}, {float(x_data.max())}], Mean: {float(x_data.mean()):.4f}
Y Range: [{float(y_data.min())}, {float(y_data.max())}], Mean: {float(y_data.mean()):.4f}
User Description: {data_description if data_description else f'Fitting target {y_col} to inputs {x_col}.'}
"""
    
    # 4. Run the engine search loop
    search_res = run_hypothesis_search(x_data, y_data, summary, domain_context)
    
    # Inject column selection log
    column_log = f"Auto-detected columns for analysis: Input (X) = '{x_col}', Target (Y) = '{y_col}'"
    search_res["logs"].insert(0, column_log)
    
    response_data = {
        "x_col": x_col,
        "y_col": y_col,
        "x_data": x_data.tolist(),
        "y_data": y_data.tolist(),
        "leaderboard": search_res["leaderboard"],
        "logs": search_res["logs"]
    }
    return sanitize_json(response_data)

@app.post("/api/demo")
def run_demo(domain_context: str = Form(""), data_description: str = Form("")):
    """
    Runs a demo with synthetically generated noisy quadratic data.
    """
    np.random.seed(42)
    x_data = np.linspace(-5, 5, 50)
    # y = 2.5 * x^2 - 1.2 * x + 3.0 + noise
    y_data = 2.5 * x_data**2 - 1.2 * x_data + 3.0 + np.random.normal(0, 2.0, size=50)
    
    summary = f"""Columns: 'x' (input) and 'y' (target).
Data Points Count: 50
X Range: [-5.0, 5.0], Mean: 0.0
Y Range: [{float(y_data.min())}, {float(y_data.max())}], Mean: {float(y_data.mean()):.4f}
User Description: Demo fitting of noisy quadratic curve.
"""
    
    search_res = run_hypothesis_search(x_data, y_data, summary, domain_context)
    
    response_data = {
        "x_col": "x",
        "y_col": "y",
        "x_data": x_data.tolist(),
        "y_data": y_data.tolist(),
        "leaderboard": search_res["leaderboard"],
        "logs": search_res["logs"]
    }
    return sanitize_json(response_data)
