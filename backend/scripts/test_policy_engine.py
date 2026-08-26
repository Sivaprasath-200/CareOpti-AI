from fastapi.testclient import TestClient
from app.main import app
from app.db.database import SessionLocal
from app.models import Patient
import uuid
import json

client = TestClient(app)

def run_tests():
    db = SessionLocal()
    patient = db.query(Patient).first()
    
    if not patient:
        print("FAIL: No synthetic patient found.")
        return
        
    patient_id = str(patient.id)
    print(f"Testing with Patient ID: {patient_id}")

    # SCENARIO 1 & 2: Evaluate Admission (Patient Age)
    # We will simulate age by testing a patient. If the patient is < 60, it will fail AGE_60_PLUS.
    res = client.post("/api/v1/policies/evaluate", json={
        "patient_id": patient_id,
        "policy_category": "ADMISSION"
    })
    data = res.json()
    print("SCENARIO 1/2/3/4/6 (Admission Category):", data["decision"])
    print("- Matched Rules:", data["matched_rules"])
    print("- Failed Rules:", data["failed_rules"])
    print("- Required Docs:", data["required_documents"])
    
    # Check if EXPIRED_COVID_PROTOCOL or FUTURE_POLICY matched (they shouldn't)
    if "EXPIRED_COVID_PROTOCOL" in data["matched_rules"] or "FUTURE_POLICY" in data["matched_rules"]:
        print("FAIL: Effective dates are not working!")
    else:
        print("PASS: Effective dates working.")

    # SCENARIO 5: Conflicting Rules
    res = client.post("/api/v1/policies/evaluate", json={
        "patient_id": patient_id,
        "policy_category": "CONFLICT"
    })
    data = res.json()
    print("SCENARIO 5 (Conflict):", data["decision"])
    if data["decision"] == "ELIGIBLE" and "OVERRIDE_PRIORITY" in data["matched_rules"]:
        print("PASS: Conflict handling priority working.")
    else:
        print("FAIL: Conflict handling failed.")

    # SCENARIO 8: Manual Review Case
    res = client.post("/api/v1/policies/evaluate", json={
        "patient_id": patient_id,
        "policy_category": "MANUAL_REVIEW"
    })
    data = res.json()
    print("SCENARIO 8 (Manual):", data["decision"])
    if data["decision"] == "REQUIRES_MANUAL_REVIEW":
        print("PASS: Manual review requirement flag working.")
    else:
        print("FAIL: Manual review failed.")
        
    # Check APIs
    print("Testing GET /policies")
    res = client.get("/api/v1/policies")
    if res.status_code == 200:
        print("PASS: API GET policies working.")
    
    if len(res.json()) > 0:
        first_id = res.json()[0]["id"]
        res2 = client.get(f"/api/v1/policies/{first_id}")
        if res2.status_code == 200:
            print("PASS: API GET policy by ID working.")
            
    print("Testing DB Health...")
    res = client.get("/api/v1/db/health")
    if res.status_code == 200:
         print("PASS: DB Health OK.")
    
    print("ALL TESTS COMPLETE.")
    
if __name__ == "__main__":
    run_tests()
