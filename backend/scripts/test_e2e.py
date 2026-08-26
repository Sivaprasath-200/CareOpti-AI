from fastapi.testclient import TestClient
from app.main import app
from app.db.database import SessionLocal
from app.models.clinical import VitalSign, LabResult, Medication, Allergy, MedicalHistory, Admission
from app.models.patient import Patient, Insurance
from app.models.users import User
from app.models.cdss import CDSSEvaluation, ClinicalAlert
import uuid
import time
from datetime import datetime, timezone, timedelta

client = TestClient(app)

def run_e2e_test():
    print("==================================================")
    print("STARTING END-TO-END VALIDATION: SYNTHETIC PATIENT JOURNEY")
    print("==================================================")
    
    db = SessionLocal()
    
    # Setup - Need a clinician for CDSS acknowledgement
    clinician = db.query(User).filter(User.role == "DOCTOR").first()
    if not clinician:
        clinician = User(name="Test Doc", email=f"dr_{uuid.uuid4().hex[:6]}@hospital.local", password_hash="hash", role="DOCTOR")
        db.add(clinician)
        db.commit()
        db.refresh(clinician)
        
    admin_user = db.query(User).filter(User.role == "ADMIN").first()
    if not admin_user:
        admin_user = User(name="Test Admin", email=f"admin_{uuid.uuid4().hex[:6]}@hospital.local", password_hash="hash", role="ADMIN")
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

    now = datetime.now(timezone.utc)
    
    # 0. System Health Checks
    print("\n[0] Verifying System Health...")
    res_health = client.get("/health")
    assert res_health.status_code == 200, f"Error: {res_health.text}"
    print("  -> SUCCESS: /health is OK")
    
    res_db_health = client.get("/api/v1/db/health")
    assert res_db_health.status_code == 200, f"Error: {res_db_health.text}"
    print("  -> SUCCESS: /api/v1/db/health is OK")

    # 1. Register synthetic patient (EHR)
    print("\n[1] Registering synthetic patient...")
    patient = Patient(
        mrn=f"MRN-{uuid.uuid4().hex[:8].upper()}",
        first_name="E2E_Test", 
        last_name=f"Patient_{uuid.uuid4().hex[:6]}", 
        dob=(now - timedelta(days=60*365)).date(), # 60 years old
        gender="MALE",
        contact_number="555-0199"
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    print(f"  -> SUCCESS: Created Patient ID: {patient.id}")
    
    # 2. Add Medical History, Vitals, Labs (EHR)
    print("\n[2] Populating EHR data...")
    history = MedicalHistory(patient_id=patient.id, condition_name="Hypertension")
    db.add(history)
    
    # Patient is critical: High HR, Low SpO2, High WBC
    vitals = VitalSign(
        patient_id=patient.id, heart_rate=140, blood_pressure_systolic=90, 
        blood_pressure_diastolic=60, spo2=88, temperature=38.5, recorded_at=now
    )
    db.add(vitals)
    
    lab = LabResult(patient_id=patient.id, test_name="WBC", result_value="18.5", unit="x10^9/L")
    db.add(lab)
    db.commit()
    print("  -> SUCCESS: EHR data (Vitals, Labs, History) committed")
    
    # 3. Create Insurance & Admission
    print("\n[3] Creating Insurance & Admission...")
    insurance = Insurance(patient_id=patient.id, provider_name="Medicare", policy_number="MC-12345", is_active=True)
    db.add(insurance)
    db.commit()
    db.refresh(insurance)
    
    admission = Admission(patient_id=patient.id, doctor_id=clinician.id, status="PLANNED", admission_date=now)
    db.add(admission)
    db.commit()
    db.refresh(admission)
    print(f"  -> SUCCESS: Admission {admission.id} created")

    # 4. Policy Engine Evaluation (Phase 3)
    print("\n[4] Running Policy Engine...")
    payload_policy = {
        "patient_id": str(patient.id),
        "insurance_provider": "Medicare",
        "condition_severity": "CRITICAL",
        "requested_department": "Emergency",
        "has_referral": False,
        "is_emergency": True,
        "policy_category": "ADMISSION"
    }
    res = client.post("/api/v1/policies/evaluate", json=payload_policy)
    if res.status_code != 200:
        print(res.text)
    assert res.status_code == 200
    data_policy = res.json()
    print(f"  -> SUCCESS: Policy Engine responded. Status: {data_policy['decision']}")
    assert data_policy['decision'] in ["ELIGIBLE", "NOT_ELIGIBLE", "REQUIRES_MANUAL_REVIEW"]
    
    # 5. AI Triage Evaluation (Phase 4)
    print("\n[5] Running AI Triage...")
    payload_triage = {
        "patient_id": str(patient.id),
        "admission_id": str(admission.id),
        "age": 60,
        "heart_rate": 140,
        "systolic_bp": 90,
        "diastolic_bp": 60,
        "respiratory_rate": 28,
        "oxygen_saturation": 88,
        "temperature": 38.5,
        "chest_pain": 1,
        "shortness_of_breath": 1,
        "fever": 1,
        "severe_bleeding": 0,
        "altered_consciousness": 0
    }
    res = client.post("/api/v1/triage/predict", json=payload_triage)
    if res.status_code != 200:
        print(res.text)
    assert res.status_code == 200
    data_triage = res.json()
    print(f"  -> SUCCESS: Triage Output -> Severity: {data_triage['severity']}")
    
    # 6. Resource Optimization (Phase 5)
    print("\n[6] Running Resource Optimization Engine...")
    res = client.post(f"/api/v1/admissions/{admission.id}/optimize?severity={data_triage['severity']}")
    assert res.status_code == 200, f"Error: {res.text}"
    data_opt = res.json()
    print(f"  -> SUCCESS: Found allocation. Bed ID: {data_opt['recommended_bed_id']}, Doctor ID: {data_opt['recommended_doctor_id']}")
    
    # Approve Allocation
    print("  -> Approving Resource Allocation...")
    res_approve = client.post(f"/api/v1/admissions/{admission.id}/confirm-allocation", json={"reviewer_id": str(admin_user.id), "action": "APPROVE"})
    assert res_approve.status_code == 200, f"Error: {res_approve.text}"
    print("  -> SUCCESS: Allocation Approved and Committed")
        
    # 7. CDSS Evaluation (Phase 6)
    print("\n[7] Running CDSS Evaluation...")
    res = client.post(f"/api/v1/cdss/evaluate?patient_id={patient.id}&admission_id={admission.id}")
    assert res.status_code == 200
    data_cdss = res.json()
    print("  -> SUCCESS: CDSS Evaluated EHR data")
    
    print("  -> Deterioration Risk:")
    if data_cdss['risk_assessment']:
        print(f"       Category: {data_cdss['risk_assessment']['risk_category']}")
        print(f"       Score: {data_cdss['risk_assessment']['risk_score']}")
    
    print(f"  -> Clinical Alerts Found: {len(data_cdss['clinical_alerts'])}")
    for a in data_cdss['clinical_alerts']:
        print(f"       - [{a['severity']}] {a['category']}: {a['message']}")
        
    # 8. Alert Acknowledgement (Audit Trail)
    print("\n[8] Acknowledging CDSS Alert (Audit Trail)...")
    if len(data_cdss['clinical_alerts']) > 0:
        alert_id = data_cdss['clinical_alerts'][0]['id']
        ack_res = client.post(f"/api/v1/cdss/alerts/{alert_id}/acknowledge", json={
            "reviewer_id": str(clinician.id),
            "review_note": "Reviewed patient vitals. Proceeding with oxygen therapy."
        })
        assert ack_res.status_code == 200
        print(f"  -> SUCCESS: Alert {alert_id} acknowledged by Doctor {clinician.id}")
    else:
        print("  -> No alerts to acknowledge in this scenario.")
        
    print("\n==================================================")
    print("END-TO-END VALIDATION COMPLETED SUCCESSFULLY")
    print("==================================================")

if __name__ == "__main__":
    run_e2e_test()
