from app.db.database import SessionLocal
from app.models.cdss import ClinicalRule, GuidelineReference, AlertSeverityEnum
from datetime import datetime, timezone, timedelta

def seed_cdss():
    db = SessionLocal()
    
    # Check if seeded
    if db.query(ClinicalRule).count() > 0:
        print("CDSS Rules already seeded.")
        # Make sure they are active
        for r in db.query(ClinicalRule).all():
            r.is_active = True
        db.commit()
        return
        
    now = datetime.now(timezone.utc)
    
    # Clinical Rules
    rules = [
        ClinicalRule(
            rule_code="R_SPO2_CRIT",
            name="Critical Hypoxia",
            category="Respiratory",
            condition_logic="spo2 < 90",
            severity=AlertSeverityEnum.CRITICAL,
            message="SpO2 is critically low. Immediate oxygen therapy required.",
            recommended_action="Administer high-flow oxygen, consider intubation.",
            effective_date=now - timedelta(days=1)
        ),
        ClinicalRule(
            rule_code="R_HR_HIGH",
            name="Severe Tachycardia",
            category="Cardiac",
            condition_logic="hr > 130",
            severity=AlertSeverityEnum.HIGH,
            message="Heart rate elevated above safe threshold.",
            recommended_action="Perform ECG, check for arrhythmias.",
            effective_date=now - timedelta(days=1)
        ),
        ClinicalRule(
            rule_code="R_WBC_HIGH",
            name="Leukocytosis",
            category="Infectious Disease",
            condition_logic="wbc > 15.0",
            severity=AlertSeverityEnum.MODERATE,
            message="Elevated WBC count indicating possible infection.",
            recommended_action="Consider blood cultures and broad-spectrum antibiotics.",
            effective_date=now - timedelta(days=1)
        )
    ]
    
    # Guidelines
    guidelines = [
        GuidelineReference(
            title="Sepsis Resuscitation Bundle",
            condition_category="Infectious Disease",
            recommendation_mappings={"action": "Measure lactate, obtain blood cultures before antibiotics, administer broad-spectrum antibiotics within 1 hour."}
        ),
        GuidelineReference(
            title="Acute Hypoxemic Respiratory Failure",
            condition_category="Respiratory",
            recommendation_mappings={"action": "Target SpO2 92-96%. Escalate to HFNC if standard O2 fails."}
        )
    ]
    
    db.add_all(rules)
    db.add_all(guidelines)
    db.commit()
    print("CDSS Seed complete.")

if __name__ == "__main__":
    seed_cdss()
