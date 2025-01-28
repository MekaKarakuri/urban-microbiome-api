import logging
from datetime import datetime
from typing import Dict, Optional
from fastapi import Request
from ..models import SecurityLog

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SecurityMonitor:
    """Sistema di monitoraggio per la sicurezza"""
    
    def __init__(self):
        self.security_logs: List[SecurityLog] = []
        self.suspicious_ips: Dict[str, int] = {}
        self.failed_attempts: Dict[str, int] = {}

    async def log_request(self, request: Request, user_id: str, event_type: str, details: str):
        """Registra una richiesta nel log di sicurezza"""
        client_ip = request.client.host if request.client else None
        
        log_entry = SecurityLog(
            timestamp=datetime.utcnow(),
            event_type=event_type,
            user_id=user_id,
            ip_address=client_ip,
            details=details
        )
        
        self.security_logs.append(log_entry)
        logger.info(f"Security Event: {event_type} - User: {user_id} - IP: {client_ip}")

    def check_suspicious_activity(self, ip_address: str) -> bool:
        """Verifica se un IP mostra attività sospetta"""
        if ip_address in self.suspicious_ips:
            return self.suspicious_ips[ip_address] > 100  # soglia di richieste sospette
        return False

    def record_failed_attempt(self, ip_address: str):
        """Registra un tentativo fallito di autenticazione"""
        if ip_address in self.failed_attempts:
            self.failed_attempts[ip_address] += 1
        else:
            self.failed_attempts[ip_address] = 1

class PerformanceMonitor:
    """Monitoraggio delle performance dell'API"""
    
    def __init__(self):
        self.response_times: List[float] = []
        self.error_counts: Dict[int, int] = {}  # status_code: count

    async def record_request(self, duration: float, status_code: int):
        """Registra i tempi di risposta e gli errori"""
        self.response_times.append(duration)
        
        if status_code >= 400:
            if status_code in self.error_counts:
                self.error_counts[status_code] += 1
            else:
                self.error_counts[status_code] = 1

    def get_average_response_time(self) -> float:
        """Calcola il tempo medio di risposta"""
        if not self.response_times:
            return 0.0
        return sum(self.response_times) / len(self.response_times)

    def get_error_rate(self) -> float:
        """Calcola il tasso di errore"""
        total_errors = sum(self.error_counts.values())
        total_requests = len(self.response_times)
        if total_requests == 0:
            return 0.0
        return (total_errors / total_requests) * 100