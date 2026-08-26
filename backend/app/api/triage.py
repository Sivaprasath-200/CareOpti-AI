from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Dict, Any
from uuid import UUID
from datetime import datetime, timezone
import json

from app.db.database import get_db
from app.models import AIPrediction, Patient
from app.schemas.triage import TriagePredictionRequest, TriagePredictionResponse
from app.ai.predictor import get_predictor

router = APIRouter(prefix="/api/v1/triage", tags=["Triage AI"])

@router.post("/predict", response_model=TriagePredictionResponse)
def predict_triage(request: TriagePredictionRequest, db: Session = Depends(get_db)):
    predictor = get_predictor()
    
    # 1. Run inference
    input_data = request.model_dump()
    severity, confidence, top_factors = predictor.predict(input_data)
    
    # 2. Optionally link to patient if provided
    if request.patient_id:
        patient = db.get(Patient, request.patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
    
    now = datetime.now(timezone.utc)
    
    # 3. Save prediction to DB (we just use the first patient if not provided for dummy saving, 
    # but the schema allows nullable in practice... wait, AIPrediction patient_id is not nullable in our DB schema)
    # Actually, in our schema `AIPrediction.patient_id` is nullable=False.
    # So if patient_id is not provided, we need a dummy patient or we must require it.
    # Let's require a valid patient_id, or if None, we just don't save to DB (return prediction only).
    db_prediction = None
    if request.patient_id:
        db_prediction = AIPrediction(
            patient_id=request.patient_id,
            model_name="xgboost_triage_v1",
            prediction_result=severity,
            confidence_score=confidence,
            explanation_json=top_factors
        )
        db.add(db_prediction)
        db.commit()
        db.refresh(db_prediction)

    return TriagePredictionResponse(
        prediction_id=db_prediction.id if db_prediction else UUID(int=0),
        severity=severity,
        confidence=confidence,
        contributing_factors=top_factors,
        model_version="xgboost_triage_v1",
        evaluation_timestamp=now
    )

@router.get("/{patient_id}/history")
def get_triage_history(patient_id: UUID, db: Session = Depends(get_db)):
    query = select(AIPrediction).where(
        AIPrediction.patient_id == patient_id,
        AIPrediction.model_name.like("%triage%")
    ).order_by(AIPrediction.created_at.desc())
    return db.scalars(query).all()

@router.get("/model-info")
def get_model_info():
    # In a real system, these would be loaded from a metadata file saved during training
    return {
        "model": "XGBoost Classifier",
        "version": "xgboost_triage_v1",
        "description": "AI-assisted triage severity predictor trained on synthetic clinical data.",
        "features_used": [
            'age', 'heart_rate', 'systolic_bp', 'diastolic_bp', 
            'respiratory_rate', 'oxygen_saturation', 'temperature', 
            'chest_pain', 'shortness_of_breath', 'fever', 
            'severe_bleeding', 'altered_consciousness'
        ],
        "warning": "This model is for demonstration purposes using synthetic data. It is not clinically validated."
    }
