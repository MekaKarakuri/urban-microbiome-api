import numpy as np
from ..models import SampleData, AnalysisResult

def analyze_microbiome_sample(sample: SampleData) -> AnalysisResult:
    biodiversity = np.random.uniform(0.5, 1.0)
    
    return AnalysisResult(
        sample_id=sample.sample_id,
        biodiversity_index=biodiversity,
        dominant_species=["Lactobacillus", "Bifidobacterium"],
        health_indicators={
            "air_quality": np.random.uniform(0, 100),
            "pathogen_risk": np.random.uniform(0, 10)
        },
        recommendations=[
            "Increase green spaces",
            "Improve ventilation"
        ]
    )