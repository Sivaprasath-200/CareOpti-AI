from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List
from uuid import UUID
from datetime import datetime, timezone

from app.db.database import get_db
from app.models.cdss import (
    CDSSEvaluation, RiskAssessment, ClinicalAlert, MedicationSafetyAlert, 
    ClinicalRule, GuidelineReference
)
from app.schemas.cdss import (
    CDSSEvaluationResponse, CDSSRiskAssessmentResponse, CDSSClinicalAlertResponse, 
    CDSSMedicationAlertResponse, CDSSGuidelineReferenceResponse, AlertAcknowledgeRequest,
    CDSSRuleResponse
)
from app.cdss.engine import evaluate_patient, fetch_guidelines

router = APIRouter(prefix="/api/v1/cdss", tags=["Clinical Decision Support"])

@router.post("/evaluate", response_model=CDSSEvaluationResponse)
def run_cdss_evaluation(patient_id: UUID, admission_id: UUID = None, db: Session = Depends(get_db)):
    eval_record = evaluate_patient(db, patient_id, admission_id)
    if not eval_record:
        raise HTTPException(status_code=404, detail="Patient not found or insufficient data.")
        
    return _build_eval_response(db, eval_record)

@router.get("/patient/{patient_id}", response_model=CDSSEvaluationResponse)
def get_latest_cdss_evaluation(patient_id: UUID, db: Session = Depends(get_db)):
    eval_record = db.execute(
        select(CDSSEvaluation)
        .where(CDSSEvaluation.patient_id == patient_id)
        .order_by(CDSSEvaluation.created_at.desc())
    ).scalars().first()
    
    if not eval_record:
        raise HTTPException(status_code=404, detail="No CDSS evaluation found for this patient.")
        
    return _build_eval_response(db, eval_record)

@router.post("/alerts/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: UUID, request: AlertAcknowledgeRequest, db: Session = Depends(get_db)):
    alert = db.get(ClinicalAlert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found.")
        
    alert.is_acknowledged = True
    alert.acknowledged_by = request.reviewer_id
    alert.review_note = request.review_note
    alert.acknowledged_at = datetime.now(timezone.utc)
    
    db.commit()
    return {"message": "Alert acknowledged successfully."}

@router.get("/rules", response_model=List[CDSSRuleResponse])
def get_active_rules(db: Session = Depends(get_db)):
    rules = db.execute(select(ClinicalRule).where(ClinicalRule.is_active == True)).scalars().all()
    return rules
    
@router.get("/model-info")
def get_model_info():
    return {
        "model_name": "XGBoost_Deterioration_Synth",
        "version": "1.0",
        "description": "Predicts patient deterioration risk using synthetic data.",
        "metrics": {
            "Accuracy": "0.908",
            "Precision": "0.890",
            "Recall": "0.908",
            "F1-Score": "0.896",
            "ROC-AUC": "0.914"
        },
        "disclaimer": "Technical prototype trained on synthetic data. NOT clinically validated."
    }

def _build_eval_response(db, eval_record):
    ra = eval_record.risk_assessments[0] if eval_record.risk_assessments else None
    
    # Guidelines
    guidelines = fetch_guidelines(db, eval_record.clinical_alerts)
    
    return CDSSEvaluationResponse(
        id=eval_record.id,
        patient_id=eval_record.patient_id,
        admission_id=eval_record.admission_id,
        clinician_review_required=eval_record.clinician_review_required,
        created_at=eval_record.created_at,
        risk_assessment=CDSSRiskAssessmentResponse(
            id=ra.id,
            risk_score=ra.risk_score,
            risk_category=ra.risk_category,
            confidence=ra.confidence,
            model_name=ra.model_name,
            model_version=ra.model_version,
            contributing_factors=ra.contributing_factors
        ) if ra else None,
        clinical_alerts=[CDSSClinicalAlertResponse(
            id=a.id,
            rule_id=a.rule_id,
            category=a.category,
            severity=a.severity,
            message=a.message,
            supporting_value=a.supporting_value,
            is_acknowledged=a.is_acknowledged,
            created_at=a.created_at
        ) for a in eval_record.clinical_alerts],
        medication_alerts=[CDSSMedicationAlertResponse(
            id=m.id,
            medication=m.medication,
            alert_type=m.alert_type,
            severity=m.severity,
            explanation=m.explanation
        ) for m in eval_record.medication_alerts],
        guideline_matches=[CDSSGuidelineReferenceResponse(
            title=g.title,
            condition_category=g.condition_category,
            source=g.source,
            recommendation_mappings=g.recommendation_mappings
        ) for g in guidelines]
    )
