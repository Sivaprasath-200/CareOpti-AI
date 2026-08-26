from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime
from uuid import UUID

class TriagePredictionRequest(BaseModel):
    patient_id: Optional[UUID] = None
    age: float = Field(..., description="Age of the patient")
    heart_rate: float = Field(..., description="Heart rate in BPM")
    systolic_bp: float = Field(..., description="Systolic blood pressure")
    diastolic_bp: float = Field(..., description="Diastolic blood pressure")
    respiratory_rate: float = Field(..., description="Respiratory rate")
    oxygen_saturation: float = Field(..., description="SpO2 percentage")
    temperature: float = Field(..., description="Temperature in Celsius")
    
    chest_pain: int = Field(0, description="1 if present, 0 otherwise")
    shortness_of_breath: int = Field(0, description="1 if present, 0 otherwise")
    fever: int = Field(0, description="1 if present, 0 otherwise")
    severe_bleeding: int = Field(0, description="1 if present, 0 otherwise")
    altered_consciousness: int = Field(0, description="1 if present, 0 otherwise")

class FeatureImpact(BaseModel):
    feature: str
    value: float
    impact: float

class TriagePredictionResponse(BaseModel):
    prediction_id: UUID
    severity: str
    confidence: float
    contributing_factors: List[FeatureImpact]
    model_version: str
    requires_clinical_review: bool = True
    warning: str = "AI-assisted triage recommendation \u2014 requires qualified clinical review."
    evaluation_timestamp: datetime
