from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from app.models.cdss import AlertSeverityEnum, RiskCategoryEnum

class CDSSBaseAlert(BaseModel):
    category: str
    severity: AlertSeverityEnum
    message: str
    
class CDSSClinicalAlertResponse(CDSSBaseAlert):
    id: UUID
    rule_id: Optional[UUID] = None
    supporting_value: Optional[str] = None
    is_acknowledged: bool
    created_at: datetime
    
class CDSSMedicationAlertResponse(BaseModel):
    id: UUID
    medication: str
    alert_type: str
    severity: AlertSeverityEnum
    explanation: str

class CDSSRiskAssessmentResponse(BaseModel):
    id: UUID
    risk_score: float
    risk_category: RiskCategoryEnum
    confidence: float
    model_name: str
    model_version: str
    contributing_factors: Optional[Dict[str, Any]] = None

class CDSSGuidelineReferenceResponse(BaseModel):
    title: str
    condition_category: str
    source: Optional[str]
    recommendation_mappings: Optional[Dict[str, Any]] = None

class CDSSEvaluationResponse(BaseModel):
    id: UUID
    patient_id: UUID
    admission_id: Optional[UUID] = None
    clinician_review_required: bool
    
    risk_assessment: Optional[CDSSRiskAssessmentResponse] = None
    clinical_alerts: List[CDSSClinicalAlertResponse] = []
    medication_alerts: List[CDSSMedicationAlertResponse] = []
    guideline_matches: List[CDSSGuidelineReferenceResponse] = []
    
    created_at: datetime

class AlertAcknowledgeRequest(BaseModel):
    reviewer_id: UUID
    review_note: Optional[str] = None

class CDSSRuleResponse(BaseModel):
    id: UUID
    rule_code: str
    name: str
    category: str
    severity: AlertSeverityEnum
    message: str
    recommended_action: Optional[str] = None
    is_active: bool
