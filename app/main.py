import os
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security.api_key import APIKeyHeader, APIKey
from datetime import datetime
from .models import SampleData, AnalysisResult
from .utils.analysis import analyze_microbiome_sample

app = FastAPI(
    title="Urban Microbiome API",
    description="API for analyzing urban microbiome samples",
    version="1.0.0"
)

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
API_KEY = os.getenv("API_KEY", "test-key")

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key_header

@app.post("/api/v1/analyze", response_model=AnalysisResult)
async def analyze_sample(data: SampleData, api_key: APIKey = Depends(get_api_key)):
    try:
        result = analyze_microbiome_sample(data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}