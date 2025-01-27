import os
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security.api_key import APIKeyHeader, APIKey
from datetime import datetime
from .models import SampleData, AnalysisResult
from .utils.analysis import analyze_microbiome_sample

# Configurazione FastAPI
app = FastAPI(
    title="Urban Microbiome API",
    description="API for analyzing urban microbiome samples",
    version="1.0.0",
    contact={
        "name": "Support Team",
        "email": "support@example.com"
    }
)

# Variabili globali per le statistiche
stats = {
    "total_samples_analyzed": 0,
    "last_analysis": None
}

# Configurazione API Key
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
API_KEY = os.getenv("API_KEY", "test-key")

# Funzione di autenticazione
async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header != API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid API Key"
        )
    return api_key_header

@app.get("/")
async def root():
    return {
        "name": "Urban Microbiome API",
        "version": "1.0.0",
        "description": "API for analyzing urban microbiome samples",
        "endpoints": {
            "docs": "/docs",
            "health": "/api/v1/health",
            "analyze": "/api/v1/analyze",
            "stats": "/api/v1/stats"
        }
    }

@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }

@app.post("/api/v1/analyze", response_model=AnalysisResult)
async def analyze_sample(data: SampleData, api_key: APIKey = Depends(get_api_key)):
    try:
        result = analyze_microbiome_sample(data)
        # Aggiorna le statistiche
        stats["total_samples_analyzed"] += 1
        stats["last_analysis"] = datetime.utcnow()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.get("/api/v1/stats")
async def get_stats(api_key: APIKey = Depends(get_api_key)):
    return {
        "total_samples_analyzed": stats["total_samples_analyzed"],
        "last_analysis": stats["last_analysis"],
        "api_version": "1.0.0"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return {
        "error": "Internal Server Error",
        "detail": str(exc),
        "timestamp": datetime.utcnow()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)