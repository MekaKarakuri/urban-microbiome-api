import numpy as np
from datetime import datetime
from ..models import SampleData, AnalysisResult

def analyze_microbiome_sample(sample: SampleData) -> AnalysisResult:
    # Simulazione analisi
    biodiversity = np.random.uniform(0.5, 1.0)
    
    # Calcolo indicatori di salute basati su temperatura e umidità
    temp_factor = 1 - abs(sample.temperature - 20) / 30  # ottimale a 20°C
    humidity_factor = 1 - abs(sample.humidity - 60) / 60  # ottimale al 60%
    
    return AnalysisResult(
        sample_id=sample.sample_id,
        biodiversity_index=biodiversity,
        dominant_species=[
            "Lactobacillus",
            "Bifidobacterium",
            "Bacillus subtilis"
        ],
        health_indicators={
            "air_quality": np.random.uniform(60, 100) * temp_factor,
            "pathogen_risk": np.random.uniform(0, 10) * (1 - humidity_factor),
            "environmental_stress": np.random.uniform(0, 100) * (1 - biodiversity)
        },
        recommendations=[
            "Increase green spaces",
            "Improve ventilation",
            "Monitor humidity levels"
        ]
    )