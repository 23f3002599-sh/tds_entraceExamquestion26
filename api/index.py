import os
import json
import numpy as np
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

# Correct path: go one folder up from /api
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
FILE_PATH = os.path.join(BASE_DIR, "q-vercel-latency.json")

with open(FILE_PATH, "r") as f:
    DATA = json.load(f)


@app.post("/api")
async def analytics(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold_ms = body.get("threshold_ms", 0)

    results = {}

    for region in regions:
        region_data = [r for r in DATA if r.get("region") == region]

        latencies = np.array([r.get("latency_ms", 0) for r in region_data])

        avg_latency = np.mean(latencies)
        p95_latency = np.percentile(latencies, 95)
        breaches = np.sum(latencies > threshold_ms)
        avg_uptime = np.mean([r.get("uptime", 0) for r in region_data])

        results[region] = {
            "avg_latency": round(float(avg_latency), 2),
            "p95_latency": round(float(p95_latency), 2),
            "avg_uptime": round(float(avg_uptime), 2),
            "breaches": int(breaches),
        }

    return JSONResponse(
        content=results,
        headers={"Access-Control-Allow-Origin": "*"},
    )


