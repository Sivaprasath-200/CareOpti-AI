from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

def run_edge_case_tests():
    print("==================================================")
    print("STARTING EDGE CASE & SECURITY VALIDATION")
    print("==================================================")
    
    # 1. Patient Not Found
    print("\n[1] Testing Patient Not Found (CDSS)...")
    bad_id = str(uuid.uuid4())
    res = client.post(f"/api/v1/cdss/evaluate?patient_id={bad_id}")
    assert res.status_code == 404, f"Expected 404, got {res.status_code}"
    print("  -> PASS: Correctly handled missing patient (HTTP 404)")
    
    # 2. Invalid Patient ID format
    print("\n[2] Testing Invalid Patient ID format (CDSS)...")
    res = client.post(f"/api/v1/cdss/evaluate?patient_id=invalid-uuid")
    assert res.status_code == 422, f"Expected 422, got {res.status_code}"
    print("  -> PASS: Correctly handled invalid UUID (HTTP 422 Unprocessable Entity)")
    
    # 3. Unauthorized Optimization Approval (Missing/Bad User)
    print("\n[3] Testing Unauthorized Optimization Approval...")
    # Attempting to approve an allocation that doesn't exist with a fake user
    fake_alloc = str(uuid.uuid4())
    fake_user = str(uuid.uuid4())
    res = client.post(f"/api/v1/allocation/{fake_alloc}/approve", json={"approved_by": fake_user})
    assert res.status_code == 404, f"Expected 404, got {res.status_code}"
    print("  -> PASS: Handled missing allocation securely")
    
    # 4. Triage Prediction with missing data
    print("\n[4] Testing AI Triage with missing required fields...")
    res = client.post("/api/v1/triage/predict", json={"patient_id": bad_id}) # Missing age, vitals, etc.
    assert res.status_code == 422
    print("  -> PASS: Request validation caught missing payload fields (HTTP 422)")
    
    # 5. Policy Engine missing fields
    print("\n[5] Testing Policy Engine missing required fields...")
    res = client.post("/api/v1/policies/evaluate", json={"patient_id": bad_id})
    assert res.status_code == 422
    print("  -> PASS: Request validation caught missing policy fields (HTTP 422)")
    
    print("\n==================================================")
    print("EDGE CASE VALIDATION COMPLETED SUCCESSFULLY")
    print("==================================================")

if __name__ == "__main__":
    run_edge_case_tests()
