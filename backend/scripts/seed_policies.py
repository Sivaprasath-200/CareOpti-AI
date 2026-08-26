import json
import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.system import PolicyRule, PolicyStatusEnum
from sqlalchemy import text

def seed_policies():
    db = SessionLocal()
    
    # Clean existing
    db.execute(text("DELETE FROM policy_evaluation_audits;"))
    db.execute(text("DELETE FROM policy_rules;"))
    db.commit()

    now = datetime.now(timezone.utc)

    # Synthetic Demo Policies
    policies = [
        # Scenario 1/2: Eligible/Ineligible Age Rule
        PolicyRule(
            rule_code="AGE_60_PLUS",
            category="ADMISSION",
            description="Patients 60 or older are eligible for senior care.",
            rule_logic_json={
                "IF": {"field": "patient.age", "operator": ">=", "value": 60},
                "THEN": {"eligibility": "ELIGIBLE"}
            },
            priority=10,
            status=PolicyStatusEnum.ACTIVE
        ),
        # Scenario 3: Missing Document
        PolicyRule(
            rule_code="ID_REQUIRED",
            category="ADMISSION",
            description="Identity proof is required.",
            rule_logic_json={
                "IF": {}, # Unconditional
                "THEN": {"required_documents": ["Identity Proof"]}
            },
            priority=5,
            status=PolicyStatusEnum.ACTIVE
        ),
        # Scenario 4: Expired Policy
        PolicyRule(
            rule_code="EXPIRED_COVID_PROTOCOL",
            category="ADMISSION",
            description="Expired rule.",
            rule_logic_json={"THEN": {"eligibility": "NOT_ELIGIBLE"}},
            priority=100,
            status=PolicyStatusEnum.ACTIVE,
            effective_end_date=now - timedelta(days=10)
        ),
        # Scenario 5: Conflicting Rules - High Priority Override
        PolicyRule(
            rule_code="OVERRIDE_PRIORITY",
            category="CONFLICT",
            description="High priority override.",
            rule_logic_json={"THEN": {"eligibility": "ELIGIBLE", "stop_processing": True}},
            priority=20,
            status=PolicyStatusEnum.ACTIVE
        ),
        PolicyRule(
            rule_code="LOW_PRIORITY",
            category="CONFLICT",
            description="Low priority failure.",
            rule_logic_json={"THEN": {"eligibility": "NOT_ELIGIBLE", "stop_processing": True}},
            priority=10,
            status=PolicyStatusEnum.ACTIVE
        ),
        # Scenario 6: Outside Date (Future)
        PolicyRule(
            rule_code="FUTURE_POLICY",
            category="ADMISSION",
            description="Policy starts next year.",
            rule_logic_json={"THEN": {"eligibility": "ELIGIBLE"}},
            priority=90,
            status=PolicyStatusEnum.ACTIVE,
            effective_start_date=now + timedelta(days=365)
        ),
        # Scenario 7: Emergency Admission
        PolicyRule(
            rule_code="EMERGENCY_WAIVER",
            category="ADMISSION",
            description="Emergencies are automatically eligible.",
            rule_logic_json={
                "IF": {"field": "admission.type", "operator": "==", "value": "emergency"},
                "THEN": {"eligibility": "ELIGIBLE", "stop_processing": True}
            },
            priority=50,
            status=PolicyStatusEnum.ACTIVE
        ),
        # Scenario 8: Manual Review Case
        PolicyRule(
            rule_code="FLAGGED_MANUAL",
            category="MANUAL_REVIEW",
            description="Requires manual override.",
            rule_logic_json={"THEN": {"eligibility": "ELIGIBLE"}},
            priority=10,
            status=PolicyStatusEnum.ACTIVE,
            requires_manual_review=True
        )
    ]
    
    for p in policies:
        db.add(p)
        
    db.commit()
    print("Seed policies injected.")

if __name__ == "__main__":
    seed_policies()
