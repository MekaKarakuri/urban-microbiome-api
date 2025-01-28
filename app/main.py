import os
import stripe
from fastapi import FastAPI, HTTPException, Depends, Security, Request
from fastapi.security.api_key import APIKeyHeader, APIKey
from datetime import datetime, timedelta
from typing import Dict, Optional
from .models import (
   SampleData, 
   AnalysisResult, 
   PlanTier, 
   SubscriptionPlan, 
   PaymentIntent,
   SubscriptionResponse,
   APIKeyModel,
   APIKeyResponse,
   SecurityLog
)
from .utils.analysis import analyze_microbiome_sample
from .utils.security import SecurityConfig, RateLimiter, APIKeyManager
from .utils.monitoring import SecurityMonitor, PerformanceMonitor

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

# Inizializzazione componenti di sicurezza
security_config = SecurityConfig()
rate_limiter = RateLimiter()
api_key_manager = APIKeyManager()
security_monitor = SecurityMonitor()
performance_monitor = PerformanceMonitor()

# Configurazione Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# ID Prezzi Stripe
STRIPE_PRICE_IDS = {
   PlanTier.BASIC: "price_ID_basic",
   PlanTier.PRO: "price_ID_pro",
   PlanTier.ENTERPRISE: "price_ID_enterprise"
}

# Configurazione piani
PRICING_PLANS = {
   PlanTier.BASIC: SubscriptionPlan(
       tier=PlanTier.BASIC,
       price_monthly=29.99,
       requests_limit=1000,
       features=[
           "Basic microbiome analysis",
           "Daily statistics",
           "Standard support",
           "API access"
       ]
   ),
   PlanTier.PRO: SubscriptionPlan(
       tier=PlanTier.PRO,
       price_monthly=99.99,
       requests_limit=5000,
       features=[
           "Advanced microbiome analysis",
           "Real-time statistics",
           "Priority support",
           "Extended API access",
           "Custom reports"
       ]
   ),
   PlanTier.ENTERPRISE: SubscriptionPlan(
       tier=PlanTier.ENTERPRISE,
       price_monthly=299.99,
       requests_limit=50000,
       features=[
           "Full microbiome analysis",
           "Dedicated support",
           "Custom integration",
           "Unlimited API access",
           "Advanced analytics",
           "SLA guarantee"
       ]
   )
}

# Statistiche globali
stats = {
   "total_samples_analyzed": 0,
   "last_analysis": None
}

# Configurazione API Key
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Middleware per il monitoring
@app.middleware("http")
async def monitoring_middleware(request: Request, call_next):
   """Middleware per monitorare le performance e la sicurezza delle richieste"""
   start_time = datetime.utcnow()
   
   # Log della richiesta iniziale
   await security_monitor.log_request(
       request,
       "system",
       "request_started",
       f"Path: {request.url.path}"
   )
   
   response = await call_next(request)
   duration = (datetime.utcnow() - start_time).total_seconds()
   
   # Registra performance
   await performance_monitor.record_request(duration, response.status_code)
   
   return response

# Funzione di autenticazione
async def get_api_key(
   api_key_header: str = Security(api_key_header),
   request: Request = None
) -> APIKeyModel:
   """Valida l'API key e gestisce l'autenticazione"""
   if not api_key_header:
       await security_monitor.log_request(
           request, 
           "unknown", 
           "authentication_failed", 
           "No API key provided"
       )
       raise HTTPException(
           status_code=401,
           detail="API Key header is missing"
       )

   key_data = api_key_manager.validate_api_key(api_key_header)
   if not key_data:
       if request:
           security_monitor.record_failed_attempt(request.client.host)
       raise HTTPException(
           status_code=403,
           detail="Invalid API Key"
       )

   return key_data

# Endpoints
@app.get("/")
async def root():
   """Endpoint root con informazioni base dell'API"""
   return {
       "name": "Urban Microbiome API",
       "version": "1.0.0",
       "description": "Secure API for analyzing urban microbiome samples",
       "endpoints": {
           "docs": "/docs",
           "health": "/api/v1/health",
           "analyze": "/api/v1/analyze",
           "stats": "/api/v1/stats",
           "plans": "/api/v1/plans",
           "subscribe": "/api/v1/subscribe",
           "key": "/api/v1/key"
       }
   }

@app.get("/api/v1/health")
async def health_check():
   """Endpoint per verificare lo stato dell'API"""
   return {
       "status": "healthy",
       "timestamp": datetime.utcnow(),
       "version": "1.0.0",
       "performance": {
           "average_response_time": performance_monitor.get_average_response_time(),
           "error_rate": performance_monitor.get_error_rate()
       }
   }

@app.post("/api/v1/analyze", response_model=AnalysisResult)
async def analyze_sample(
   data: SampleData,
   api_key: APIKeyModel = Depends(get_api_key),
   request: Request = None
):
   """Endpoint principale per l'analisi dei campioni"""
   # Verifica rate limit
   if not await rate_limiter.check_rate_limit(api_key.key, api_key_manager.api_keys):
       await security_monitor.log_request(
           request,
           api_key.user_id,
           "rate_limit_exceeded",
           f"Plan: {api_key.plan}"
       )
       raise HTTPException(
           status_code=429,
           detail="Rate limit exceeded"
       )

   try:
       # Cripta dati sensibili
       encrypted_location = security_config.encrypt_data(data.location.json())
       
       result = analyze_microbiome_sample(data)
       
       # Aggiorna statistiche
       stats["total_samples_analyzed"] += 1
       stats["last_analysis"] = datetime.utcnow()
       
       await security_monitor.log_request(
           request,
           api_key.user_id,
           "analysis_success",
           f"Sample: {data.sample_id}"
       )
       
       return result
   except Exception as e:
       await security_monitor.log_request(
           request,
           api_key.user_id,
           "analysis_error",
           str(e)
       )
       raise HTTPException(
           status_code=500,
           detail=str(e)
       )

@app.get("/api/v1/stats")
async def get_stats(api_key: APIKeyModel = Depends(get_api_key)):
   """Endpoint per le statistiche di utilizzo"""
   return {
       "total_samples_analyzed": stats["total_samples_analyzed"],
       "last_analysis": stats["last_analysis"],
       "api_version": "1.0.0",
       "performance_metrics": {
           "average_response_time": performance_monitor.get_average_response_time(),
           "error_rate": performance_monitor.get_error_rate()
       }
   }

@app.get("/api/v1/plans")
async def get_plans():
   """Endpoint per visualizzare i piani disponibili"""
   return {"plans": PRICING_PLANS}

@app.post("/api/v1/subscribe", response_model=SubscriptionResponse)
async def create_subscription(
   payment: PaymentIntent,
   request: Request
):
   """Endpoint per la creazione di nuove sottoscrizioni"""
   try:
       session = stripe.checkout.Session.create(
           payment_method_types=['card'],
           line_items=[{
               'price': STRIPE_PRICE_IDS[payment.plan],
               'quantity': 1,
           }],
           mode='subscription',
           customer_email=payment.customer_email,
           success_url=f"{request.base_url}api/v1/success?session_id={{CHECKOUT_SESSION_ID}}",
           cancel_url=f"{request.base_url}api/v1/cancel"
       )
       
       await security_monitor.log_request(
           request,
           "system",
           "subscription_created",
           f"Plan: {payment.plan}"
       )
       
       return SubscriptionResponse(
           checkout_url=session.url,
           session_id=session.id
       )
   except Exception as e:
       await security_monitor.log_request(
           request,
           "system",
           "subscription_error",
           str(e)
       )
       raise HTTPException(
           status_code=500,
           detail=str(e)
       )

@app.post("/api/v1/key/generate", response_model=APIKeyResponse)
async def generate_key(
   user_id: str,
   plan: PlanTier,
   request: Request
):
   """Endpoint per la generazione di nuove API key"""
   try:
       api_key = api_key_manager.generate_api_key(user_id, plan)
       await security_monitor.log_request(
           request,
           user_id,
           "api_key_generated",
           f"Plan: {plan}"
       )
       return APIKeyResponse(
           key=api_key,
           expires_at=datetime.utcnow().replace(year=datetime.utcnow().year + 1)
       )
   except Exception as e:
       await security_monitor.log_request(
           request,
           user_id,
           "api_key_generation_error",
           str(e)
       )
       raise HTTPException(
           status_code=500,
           detail="Error generating API key"
       )

@app.post("/api/v1/webhook")
async def stripe_webhook(request: Request):
   """Webhook per gestire gli eventi Stripe"""
   try:
       event = stripe.Webhook.construct_event(
           payload=await request.body(),
           sig_header=request.headers.get('stripe-signature'),
           secret=os.getenv("STRIPE_WEBHOOK_SECRET")
       )
       
       if event.type == 'checkout.session.completed':
           session = event.data.object
           await security_monitor.log_request(
               request,
               session.customer_email,
               "payment_completed",
               f"Session: {session.id}"
           )
       
       return {"status": "success"}
   except Exception as e:
       await security_monitor.log_request(
           request,
           "system",
           "webhook_error",
           str(e)
       )
       raise HTTPException(
           status_code=400,
           detail=str(e)
       )

@app.get("/api/v1/success")
async def payment_success(session_id: str):
   """Endpoint per gestire il successo del pagamento"""
   return {
       "status": "success",
       "message": "Payment completed successfully",
       "session_id": session_id
   }

@app.get("/api/v1/cancel")
async def payment_cancel():
   """Endpoint per gestire la cancellazione del pagamento"""
   return {
       "status": "cancelled",
       "message": "Payment was cancelled"
   }

# Gestione errori globale
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
   """Handler globale per le eccezioni"""
   await security_monitor.log_request(
       request,
       "system",
       "global_error",
       str(exc)
   )
   return {
       "error": "Internal Server Error",
       "detail": str(exc),
       "timestamp": datetime.utcnow()
   }

if __name__ == "__main__":
   import uvicorn
   uvicorn.run(app, host="0.0.0.0", port=8000)