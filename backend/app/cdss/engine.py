import joblib
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID
from datetime import datetime, timezone
import os

from app.models.cdss import (
    CDSSEvaluation, RiskAssessment, ClinicalAlert, MedicationSafetyAlert, 
    ClinicalRule, GuidelineReference, AlertSeverityEnum, RiskCategoryEnum
)
from app.models.clinical import VitalSign, LabResult, Medication, Allergy, MedicalHistory
from app.models.patient import Patient

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models", "cdss_deterioration_xgboost.joblib")
try:
    xgb_model = joblib.load(MODEL_PATH)
except:
    xgb_model = None

def evaluate_patient(db: Session, patient_id: UUID, admission_id: UUID = None) -> CDSSEvaluation:
    # 1. Gather Data
    patient = db.get(Patient, patient_id)
    if not patient:
        return None
        
    vitals = db.execute(
        select(VitalSign).where(VitalSign.patient_id == patient_id).order_by(VitalSign.recorded_at.desc()).limit(1)
    ).scalars().first()
    
    labs = db.execute(
        select(LabResult).where(LabResult.patient_id == patient_id)
    ).scalars().all()
    
    medications = db.execute(
        select(Medication).where(Medication.patient_id == patient_id)
    ).scalars().all()
    
    allergies = db.execute(
        select(Allergy).where(Allergy.patient_id == patient_id)
    ).scalars().all()
    
    history = db.execute(
        select(MedicalHistory).where(MedicalHistory.patient_id == patient_id)
    ).scalars().all()
    
    # Create evaluation record
    eval_record = CDSSEvaluation(
        patient_id=patient_id,
        admission_id=admission_id,
        clinician_review_required=True
    )
    db.add(eval_record)
    db.flush() # get ID
    
    # 2. Evaluate ML Deterioration Risk
    risk_record = _predict_risk(db, eval_record.id, patient, vitals, labs, history)
    
    # 3. Evaluate Clinical Rules
    alerts = _evaluate_rules(db, eval_record.id, vitals, labs)
    
    # 4. Evaluate Medication Safety
    med_alerts = _evaluate_medications(db, eval_record.id, medications, allergies)
    
    # Commit all
    db.commit()
    db.refresh(eval_record)
    
    return eval_record

def _predict_risk(db, eval_id, patient, vitals, labs, history):
    if not xgb_model:
        return None
        
    # Build feature vector
    age = patient.age() if hasattr(patient, 'age') else 50
    hr = vitals.heart_rate if vitals and vitals.heart_rate else 80
    sbp = vitals.blood_pressure_systolic if vitals and vitals.blood_pressure_systolic else 120
    dbp = vitals.blood_pressure_diastolic if vitals and vitals.blood_pressure_diastolic else 80
    rr = 16 # Not in our original vitals schema, default to 16
    spo2 = vitals.spo2 if vitals and vitals.spo2 else 98
    temp = vitals.temperature if vitals and vitals.temperature else 37.0
    
    wbc, cr, bun = 7.5, 1.0, 15.0
    for lab in labs:
        try:
            if "WBC" in lab.test_name.upper():
                wbc = float(lab.result_value)
            if "CREATININE" in lab.test_name.upper():
                cr = float(lab.result_value)
            if "BUN" in lab.test_name.upper():
                bun = float(lab.result_value)
        except:
            pass
            
    diabetes = 1 if any("diabet" in h.condition_name.lower() for h in history) else 0
    htn = 1 if any("hypertens" in h.condition_name.lower() for h in history) else 0
    hf = 1 if any("heart fail" in h.condition_name.lower() for h in history) else 0
    
    features = pd.DataFrame([{
        'age': age,
        'heart_rate': hr,
        'systolic_bp': sbp,
        'diastolic_bp': dbp,
        'respiratory_rate': rr,
        'spo2': spo2,
        'temperature': temp,
        'wbc': wbc,
        'creatinine': cr,
        'bun': bun,
        'diabetes': diabetes,
        'hypertension': htn,
        'heart_failure': hf
    }])
    
    probs = xgb_model.predict_proba(features)[0]
    pred_class = int(np.argmax(probs))
    conf = float(probs[pred_class])
    
    cat_map = {0: RiskCategoryEnum.LOW, 1: RiskCategoryEnum.MODERATE, 2: RiskCategoryEnum.HIGH, 3: RiskCategoryEnum.CRITICAL}
    risk_cat = cat_map.get(pred_class, RiskCategoryEnum.LOW)
    
    # Calculate a rough continuous score for display (0-100) safely
    score = 0.0
    if len(probs) > 1:
        score += probs[1] * 33
    if len(probs) > 2:
        score += probs[2] * 66
    if len(probs) > 3:
        score += probs[3] * 100
        
    ra = RiskAssessment(
        evaluation_id=eval_id,
        patient_id=patient.id,
        risk_score=score,
        risk_category=risk_cat,
        confidence=conf,
        model_name="XGBoost_Deterioration_Synth",
        model_version="1.0",
        contributing_factors={"hr": hr, "spo2": spo2, "sbp": sbp}
    )
    db.add(ra)
    return ra

def _evaluate_rules(db, eval_id, vitals, labs):
    rules = db.execute(select(ClinicalRule).where(ClinicalRule.is_active == True)).scalars().all()
    patient_id = None
    if vitals:
        patient_id = vitals.patient_id
    elif labs:
        patient_id = labs[0].patient_id
        
    if not patient_id:
        return []
        
    env = {
        "hr": vitals.heart_rate if vitals else 80,
        "sbp": vitals.blood_pressure_systolic if vitals else 120,
        "spo2": vitals.spo2 if vitals else 98,
        "temp": vitals.temperature if vitals else 37.0
    }
    
    # Extract labs into env
    for lab in labs:
        try:
            env[lab.test_name.lower()] = float(lab.result_value)
        except:
            pass
            
    alerts = []
    for r in rules:
        try:
            # Dangerous in prod without sandboxing, but acceptable for prototype safe deterministic rules
            # "hr > 120"
            if eval(r.condition_logic, {"__builtins__": None}, env):
                alert = ClinicalAlert(
                    evaluation_id=eval_id,
                    patient_id=patient_id,
                    rule_id=r.id,
                    category=r.category,
                    severity=r.severity,
                    message=r.message,
                    supporting_value=str(env.get(r.condition_logic.split()[0], "N/A")),
                    rule_version=r.version
                )
                db.add(alert)
                alerts.append(alert)
        except Exception as e:
            # Rule parsing failed or var missing
            pass
            
    return alerts

def _evaluate_medications(db, eval_id, medications, allergies):
    alerts = []
    if not medications:
        return alerts
        
    patient_id = medications[0].patient_id
    med_names = [m.name.lower() for m in medications]
    allergen_names = [a.allergen.lower() for a in allergies]
    
    # 1. Allergy conflict
    for med in med_names:
        for allergen in allergen_names:
            if allergen in med or med in allergen:
                a = MedicationSafetyAlert(
                    evaluation_id=eval_id,
                    patient_id=patient_id,
                    medication=med,
                    alert_type="ALLERGY_CONFLICT",
                    severity=AlertSeverityEnum.CRITICAL,
                    explanation=f"Patient has known allergy to {allergen}, which conflicts with {med}."
                )
                db.add(a)
                alerts.append(a)
                
    # 2. Duplication
    seen = set()
    for med in med_names:
        if med in seen:
            a = MedicationSafetyAlert(
                evaluation_id=eval_id,
                patient_id=patient_id,
                medication=med,
                alert_type="DUPLICATION",
                severity=AlertSeverityEnum.MODERATE,
                explanation=f"Potential duplicate prescription of {med}."
            )
            db.add(a)
            alerts.append(a)
        seen.add(med)
        
    # 3. Synthetic interaction (Warfarin + Aspirin)
    if "warfarin" in med_names and "aspirin" in med_names:
        a = MedicationSafetyAlert(
            evaluation_id=eval_id,
            patient_id=patient_id,
            medication="warfarin",
            alert_type="DRUG_INTERACTION",
            severity=AlertSeverityEnum.HIGH,
            explanation="Major interaction: Warfarin and Aspirin increase bleeding risk."
        )
        db.add(a)
        alerts.append(a)
        
    return alerts

def fetch_guidelines(db, alerts):
    if not alerts:
        return []
    
    # Simple matching based on alert categories
    categories = list(set([a.category for a in alerts]))
    guidelines = db.execute(
        select(GuidelineReference).where(GuidelineReference.condition_category.in_(categories))
    ).scalars().all()
    
    return guidelines
