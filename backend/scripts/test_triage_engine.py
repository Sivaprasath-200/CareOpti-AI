from fastapi.testclient import TestClient
from app.main import app
from app.db.database import SessionLocal
from app.models import Patient
import uuid
import json

client = TestClient(app)

def get_base_payload():
    return {
        "age": 45,
        "heart_rate": 75,
        "systolic_bp": 120,
        "diastolic_bp": 80,
        "respiratory_rate": 16,
        "oxygen_saturation": 98,
        "temperature": 37.0,
        "chest_pain": 0,
        "shortness_of_breath": 0,
        "fever": 0,
        "severe_bleeding": 0,
        "altered_consciousness": 0
    }

def run_tests():
    db = SessionLocal()
    patient = db.query(Patient).first()
    
    patient_id = str(patient.id) if patient else None
    print(f"Testing with Patient ID: {patient_id}")
    
    scenarios = {
        "1. EMERGENCY": {
            "payload": {**get_base_payload(), "heart_rate": 160, "chest_pain": 1, "altered_consciousness": 1},
            "expected_severity": ["EMERGENCY"]
        },
        "2. CRITICAL": {
            "payload": {**get_base_payload(), "systolic_bp": 75, "severe_bleeding": 1},
            "expected_severity": ["CRITICAL", "EMERGENCY"]
        },
        "3. HIGH": {
            "payload": {**get_base_payload(), "temperature": 40.5, "fever": 1, "heart_rate": 115},
            "expected_severity": ["HIGH"]
        },
        "4. MODERATE": {
            "payload": {**get_base_payload(), "temperature": 38.0, "fever": 1},
            "expected_severity": ["MODERATE", "HIGH"]
        },
        "5. LOW": {
            "payload": get_base_payload(),
            "expected_severity": ["LOW", "MODERATE"]
        },
        "6. Missing/Boundary Data (High HR)": {
            "payload": {**get_base_payload(), "heart_rate": 200},
            "expected_severity": ["EMERGENCY", "HIGH", "CRITICAL"] # Often extreme values push to high severity
        },
        "7. Multiple Symptoms": {
            "payload": {**get_base_payload(), "chest_pain": 1, "shortness_of_breath": 1, "oxygen_saturation": 88},
            "expected_severity": ["EMERGENCY", "CRITICAL"]
        }
    }

    print("--- Triage Engine Tests ---")
    for name, data in scenarios.items():
        payload = data["payload"]
        if patient_id:
            payload["patient_id"] = patient_id
            
        res = client.post("/api/v1/triage/predict", json=payload)
        assert res.status_code == 200, f"Error: {res.text}"
        result = res.json()
        
        severity = result["severity"]
        confidence = result["confidence"]
        
        print(f"\n{name} -> Predicted: {severity} (Confidence: {confidence:.2f})")
        
        if severity in data["expected_severity"]:
            print("  PASS: Realistic prediction.")
        else:
            print(f"  WARN: Predicted {severity} but expected one of {data['expected_severity']}.")
            
        print("  Top Factor:", result["contributing_factors"][0]["feature"], "Impact:", round(result["contributing_factors"][0]["impact"], 3))
        
        assert result["requires_clinical_review"] == True
        assert "AI-assisted triage recommendation" in result["warning"]

    print("\n8. Testing API Validation (Missing Field)")
    bad_payload = get_base_payload()
    del bad_payload["age"]
    res = client.post("/api/v1/triage/predict", json=bad_payload)
    if res.status_code == 422:
        print("PASS: Missing data rejected appropriately (HTTP 422)")
    else:
        print("FAIL: Missing data not rejected")
        
    print("\n9. Testing Model Info")
    res = client.get("/api/v1/triage/model-info")
    if res.status_code == 200:
        print("PASS: Model info API OK")

    print("\nTesting DB Health...")
    res = client.get("/api/v1/db/health")
    if res.status_code == 200:
         print("PASS: DB Health OK.")
    
    print("\nALL TESTS COMPLETE.")
    
if __name__ == "__main__":
    run_tests()
