from fastapi.testclient import TestClient
from app.main import app
from app.db.database import SessionLocal
from app.models.clinical import VitalSign, LabResult, Medication, Allergy, MedicalHistory
from app.models.patient import Patient
from datetime import datetime, timezone
import uuid
import time

client = TestClient(app)

def run_cdss_tests():
    db = SessionLocal()
    
    # Need a dummy patient
    patient = db.query(Patient).first()
    if not patient:
        patient = Patient(first_name="CDSS", last_name="Test", gender="F")
        db.add(patient)
        db.commit()
        db.refresh(patient)
        
    print("--- CDSS Engine Tests ---")
    
    # Clean previous clinical data for this patient
    db.query(VitalSign).filter(VitalSign.patient_id == patient.id).delete()
    db.query(LabResult).filter(LabResult.patient_id == patient.id).delete()
    db.query(Medication).filter(Medication.patient_id == patient.id).delete()
    db.query(Allergy).filter(Allergy.patient_id == patient.id).delete()
    db.commit()

    now = datetime.now(timezone.utc)
    
    # Base Vitals & Labs
    vitals = VitalSign(patient_id=patient.id, heart_rate=80, blood_pressure_systolic=120, blood_pressure_diastolic=80, spo2=98, temperature=37.0, recorded_at=now)
    lab1 = LabResult(patient_id=patient.id, test_name="WBC", result_value="7.5", unit="x10^9/L")
    db.add(vitals)
    db.add(lab1)
    db.commit()

    # 1. Normal patient
    res = client.post(f"/api/v1/cdss/evaluate?patient_id={patient.id}")
    data = res.json()
    print("1. Normal Patient ->", "PASS" if not data['clinical_alerts'] else "FAIL")
    
    # 2. Abnormal vitals (HR > 130)
    vitals.heart_rate = 135
    db.commit()
    res = client.post(f"/api/v1/cdss/evaluate?patient_id={patient.id}")
    data = res.json()
    print("2. Abnormal Vitals (Tachycardia) ->", "PASS" if any(a['category'] == 'Cardiac' for a in data['clinical_alerts']) else "FAIL")
    
    # 3. Critical oxygen saturation
    vitals.spo2 = 85
    db.commit()
    res = client.post(f"/api/v1/cdss/evaluate?patient_id={patient.id}")
    data = res.json()
    print("3. Critical Oxygen Saturation ->", "PASS" if any(a['category'] == 'Respiratory' and a['severity'] == 'CRITICAL' for a in data['clinical_alerts']) else "FAIL")
    
    # 4. Abnormal laboratory result
    vitals.spo2 = 98
    vitals.heart_rate = 80
    lab1.result_value = "18.0"
    db.commit()
    res = client.post(f"/api/v1/cdss/evaluate?patient_id={patient.id}")
    data = res.json()
    print("4. Abnormal Laboratory Result ->", "PASS" if any(a['category'] == 'Infectious Disease' for a in data['clinical_alerts']) else "FAIL")
    
    # 5. Medication allergy conflict
    db.add(Allergy(patient_id=patient.id, allergen="Penicillin", severity="HIGH"))
    db.add(Medication(patient_id=patient.id, name="Penicillin V", dosage="250mg", frequency="BID"))
    db.commit()
    res = client.post(f"/api/v1/cdss/evaluate?patient_id={patient.id}")
    data = res.json()
    print("5. Medication Allergy Conflict ->", "PASS" if any(m['alert_type'] == 'ALLERGY_CONFLICT' for m in data['medication_alerts']) else "FAIL")
    
    # 6. Medication duplication
    db.add(Medication(patient_id=patient.id, name="Penicillin V", dosage="500mg", frequency="QD"))
    db.commit()
    res = client.post(f"/api/v1/cdss/evaluate?patient_id={patient.id}")
    data = res.json()
    print("6. Medication Duplication ->", "PASS" if any(m['alert_type'] == 'DUPLICATION' for m in data['medication_alerts']) else "FAIL")
    
    # 7. Drug interaction
    db.add(Medication(patient_id=patient.id, name="Warfarin", dosage="5mg", frequency="QD"))
    db.add(Medication(patient_id=patient.id, name="Aspirin", dosage="81mg", frequency="QD"))
    db.commit()
    res = client.post(f"/api/v1/cdss/evaluate?patient_id={patient.id}")
    data = res.json()
    print("7. Synthetic Drug Interaction ->", "PASS" if any(m['alert_type'] == 'DRUG_INTERACTION' for m in data['medication_alerts']) else "FAIL")
    
    # 8. High / 9. Critical deterioration risk
    # Ensure risk score parses and assigns risk category
    print("8/9. Deterioration Risk Output ->", "PASS" if 'risk_assessment' in data and data['risk_assessment']['risk_category'] in ['LOW', 'MODERATE', 'HIGH', 'CRITICAL'] else "FAIL")
    if data['risk_assessment']:
        print(f"  Risk Category: {data['risk_assessment']['risk_category']}")
        print(f"  Risk Score: {data['risk_assessment']['risk_score']}")
        
    # 10. Multiple simultaneous alerts
    print("10. Multiple Simultaneous Alerts ->", "PASS" if len(data['medication_alerts']) >= 3 and len(data['clinical_alerts']) >= 1 else "FAIL")
    
    # 11. Alert acknowledgement
    alert_id = data['clinical_alerts'][0]['id']
    from app.models.users import User
    doctor = db.query(User).first()
    admin_id = str(doctor.id) if doctor else str(uuid.uuid4())
    ack_res = client.post(f"/api/v1/cdss/alerts/{alert_id}/acknowledge", json={"reviewer_id": admin_id, "review_note": "Seen and noted"})
    print("11. Alert Acknowledgement ->", "PASS" if ack_res.status_code == 200 else "FAIL")
    
    # 12. Missing/invalid data
    bad_res = client.post(f"/api/v1/cdss/evaluate?patient_id={uuid.uuid4()}")
    print("12. Missing Data Handling ->", "PASS" if bad_res.status_code == 404 else "FAIL")
    
    # Model API test
    mod_res = client.get("/api/v1/cdss/model-info")
    print("Model Info API ->", "PASS" if mod_res.status_code == 200 else "FAIL")
    
    # Guidelines test
    print("Guideline Matching ->", "PASS" if len(data['guideline_matches']) > 0 else "FAIL")

if __name__ == "__main__":
    run_cdss_tests()
