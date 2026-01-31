import os
import json
import numpy as np
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

# Enable CORS for POST from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

@app.post("/")
async def analytics(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold_ms = body.get("threshold_ms", 0)
    
    # Load and parse the sample data (q-vercel-latency.json)
    # In real use, this would be uploaded or from a URL; here we read locally for Vercel
    with open("q-vercel-latency.json", "r") as f:
        data = json.load(f)
    
    results = {}
    for region in regions:
        region_data = [r for r in data if r.get("region") == region]
        if not region_data:
            results[region] = {"avg_latency": 0, "p95_latency": 0, "avg_uptime": 0, "breaches": 0}
            continue
        
        latencies = np.array([r.get("latency_ms", 0) for r in region_data])
        avg_latency = np.mean(latencies)
        p95_latency = np.percentile(latencies, 95)
        breaches = np.sum(latencies > threshold_ms)
        avg_uptime = 100 * (1 - (breaches / len(latencies))) if len(latencies) > 0 else 0
        
        results[region] = {
            "avg_latency": round(avg_latency, 2),
            "p95_latency": round(p95_latency, 2),
            "avg_uptime": round(avg_uptime, 2),
            "breaches": int(breaches)
        }
    
    return JSONResponse(results)
