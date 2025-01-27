from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime

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