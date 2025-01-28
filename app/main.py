import os
import stripe
from fastapi import FastAPI, HTTPException, Depends, Security, Request
from fastapi.security.api_key import APIKeyHeader, APIKey
from datetime import datetime, timedelta
from typing import Dict
from .models import (
    SampleData, 
    AnalysisResult, 
    PlanTier, 
    SubscriptionPlan, 
    PaymentIntent,
    SubscriptionResponse,
    UserSubscription,
    SubscriptionUsage
)
from .utils.analysis import analyze_microbiome_sample
from .utils.subscription import check_subscription_limits, get_subscription_usage

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

# Configurazione Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Prezzi Stripe
STRIPE_PRICE_IDS = {
    PlanTier.BASIC: "price_1QmAryGr3bQE4NuNAelsEEaB",
    PlanTier.PRO: "price_1QmAryGr3bQE4NuNaVAobSy8",
    PlanTier.ENTERPRISE: "price_1QmAryGr3bQE4NuN0E14ssyM"
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

# Storage simulato (in produzione usare un database)
active_subscriptions: Dict[str, UserSubscription] = {}

# Configurazione API Key
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
API_KEY = os.getenv("API_KEY", "test-key")

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
            "stats": "/api/v1/stats",
            "plans": "/api/v1/plans",
            "subscribe": "/api/v1/subscribe",
            "usage": "/api/v1/usage/{user_id}"
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
async def analyze_sample(
    data: SampleData,
    api_key: APIKey = Depends(get_api_key),
    user_id: str = None  # In produzione, ricavare l'user_id dall'API key
):
    if user_id and user_id in active_subscriptions:
        subscription = active_subscriptions[user_id]
        if not check_subscription_limits(subscription):
            raise HTTPException(
                status_code=429,
                detail="Request limit exceeded"
            )
        subscription.requests_used += 1
    
    try:
        result = analyze_microbiome_sample(data)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.get("/api/v1/usage/{user_id}", response_model=SubscriptionUsage)
async def get_usage(user_id: str, api_key: APIKey = Depends(get_api_key)):
    if user_id not in active_subscriptions:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found"
        )
    return get_subscription_usage(active_subscriptions[user_id])

@app.get("/api/v1/plans")
async def get_plans():
    return {"plans": PRICING_PLANS}

@app.post("/api/v1/subscribe", response_model=SubscriptionResponse)
async def create_subscription(payment: PaymentIntent):
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': STRIPE_PRICE_IDS[payment.plan],
                'quantity': 1,
            }],
            mode='subscription',
            customer_email=payment.customer_email,
            success_url='https://your-domain.com/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='https://your-domain.com/cancel'
        )
        
        return SubscriptionResponse(
            checkout_url=session.url,
            session_id=session.id
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.post("/api/v1/webhook")
async def stripe_webhook(request: Request):
    try:
        event = stripe.Webhook.construct_event(
            payload=await request.body(),
            sig_header=request.headers.get('stripe-signature'),
            secret=os.getenv("STRIPE_WEBHOOK_SECRET")
        )
        
        if event.type == 'checkout.session.completed':
            session = event.data.object
            # Creare una nuova sottoscrizione
            subscription = UserSubscription(
                user_id=session.client_reference_id,
                plan=PlanTier.BASIC,  # Default, aggiornare in base al piano acquistato
                stripe_customer_id=session.customer,
                stripe_subscription_id=session.subscription,
                status="active",
                current_period_end=datetime.utcnow() + timedelta(days=30),
                requests_used=0
            )
            active_subscriptions[subscription.user_id] = subscription
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

# Dopo gli altri endpoint aggiungi:
@app.get("/api/v1/stats")
async def get_stats(api_key: APIKey = Depends(get_api_key)):
    try:
        # Recupera i dati da Stripe
        stripe_data = stripe.PaymentIntent.list(limit=100)
        total_payments = len(stripe_data.data)
        
        return {
            "total_subscriptions": total_payments,
            "last_payment": datetime.utcnow(),
            "api_version": "1.0.0"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)