from pydantic import BaseModel, EmailStr
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum

# Enum per i piani
class PlanTier(str, Enum):
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"

# Modelli base per l'analisi
class Location(BaseModel):
    latitude: float
    longitude: float
    altitude: float
    location_type: str

class SampleData(BaseModel):
    sample_id: str
    timestamp: datetime
    location: Location
    temperature: float
    humidity: float
    metadata: Dict[str, str]

class AnalysisResult(BaseModel):
    sample_id: str
    biodiversity_index: float
    dominant_species: List[str]
    health_indicators: Dict[str, float]
    recommendations: List[str]

# Modelli per la gestione dei pagamenti
class SubscriptionPlan(BaseModel):
    tier: PlanTier
    price_monthly: float
    requests_limit: int
    features: List[str]

class PaymentIntent(BaseModel):
    plan: PlanTier
    customer_email: EmailStr

class SubscriptionResponse(BaseModel):
    checkout_url: str
    session_id: str

# Modelli per la gestione degli utenti
class UserSubscription(BaseModel):
    user_id: str
    plan: PlanTier
    stripe_customer_id: str
    stripe_subscription_id: str
    status: str
    current_period_end: datetime
    requests_used: int = 0

class SubscriptionUsage(BaseModel):
    requests_used: int
    requests_limit: int
    remaining_requests: int
    days_until_renewal: int

class UserAPIKey(BaseModel):
    key: str
    user_id: str
    created_at: datetime
    last_used: Optional[datetime] = None
    is_active: bool = True