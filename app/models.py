from pydantic import BaseModel, EmailStr
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum

# Enum per i piani di sottoscrizione
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

# Modelli per la sicurezza e autenticazione
class APIKeyModel(BaseModel):
    key: str
    user_id: str
    plan: PlanTier
    created_at: datetime
    is_active: bool
    last_used: Optional[datetime]
    requests_count: int = 0

class APIKeyResponse(BaseModel):
    key: str
    expires_at: datetime

class SecurityLog(BaseModel):
    timestamp: datetime
    event_type: str
    user_id: str
    ip_address: Optional[str]
    details: str