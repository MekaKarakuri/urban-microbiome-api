import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from fastapi import HTTPException
from cryptography.fernet import Fernet
import os
from ..models import PlanTier, APIKeyModel

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityConfig:
    """Gestione della crittografia e sicurezza dei dati"""
    def __init__(self):
        self.encryption_key = os.getenv("ENCRYPTION_KEY", Fernet.generate_key())
        self.cipher_suite = Fernet(self.encryption_key)

    def encrypt_data(self, data: str) -> str:
        """Cripta i dati sensibili"""
        return self.cipher_suite.encrypt(data.encode()).decode()

    def decrypt_data(self, encrypted_data: str) -> str:
        """Decripta i dati sensibili"""
        return self.cipher_suite.decrypt(encrypted_data.encode()).decode()

class RateLimiter:
    """Gestione dei limiti di richieste per piano"""
    def __init__(self):
        self.requests: Dict[str, Dict] = {}
        self.limits = {
            PlanTier.BASIC: 1000,      # richieste al mese
            PlanTier.PRO: 5000,        # richieste al mese
            PlanTier.ENTERPRISE: 50000  # richieste al mese
        }

    async def check_rate_limit(self, api_key: str, api_keys: Dict) -> bool:
        """Verifica se l'API key ha superato il limite di richieste"""
        if api_key not in api_keys:
            return False
            
        user_data = api_keys[api_key]
        current_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
        
        if api_key not in self.requests:
            self.requests[api_key] = {"count": 0, "reset_time": current_month}
            
        if self.requests[api_key]["reset_time"] < current_month:
            self.requests[api_key] = {"count": 0, "reset_time": current_month}
            
        self.requests[api_key]["count"] += 1
        return self.requests[api_key]["count"] <= self.limits[user_data.plan]

class APIKeyManager:
    """Gestione delle API key"""
    def __init__(self):
        self.api_keys: Dict[str, APIKeyModel] = {}

    def generate_api_key(self, user_id: str, plan: PlanTier) -> str:
        """Genera una nuova API key per un utente"""
        from secrets import token_urlsafe
        
        api_key = f"umapi_{token_urlsafe(32)}"
        self.api_keys[api_key] = APIKeyModel(
            key=api_key,
            user_id=user_id,
            plan=plan,
            created_at=datetime.utcnow(),
            is_active=True,
            last_used=None
        )
        return api_key

    def validate_api_key(self, api_key: str) -> Optional[APIKeyModel]:
        """Valida un'API key"""
        if api_key not in self.api_keys:
            return None
        
        key_data = self.api_keys[api_key]
        if not key_data.is_active:
            return None
            
        key_data.last_used = datetime.utcnow()
        return key_data

    def deactivate_api_key(self, api_key: str) -> bool:
        """Disattiva un'API key"""
        if api_key in self.api_keys:
            self.api_keys[api_key].is_active = False
            return True
        return False