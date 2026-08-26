from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func
from datetime import datetime, timezone
import json

from app.models import PolicyRule, PolicyStatusEnum, PolicyEvaluationAudit, Patient, Admission
from app.schemas.policy import PolicyEvaluationRequest, PolicyEvaluationResponse

class DeterministicEvaluator:
    @staticmethod
    def _get_value(context: Dict[str, Any], path: str):
        parts = path.split('.')
        val = context
        for part in parts:
            if isinstance(val, dict) and part in val:
                val = val[part]
            else:
                return None
        return val

    @staticmethod
    def evaluate_condition(condition: Dict[str, Any], context: Dict[str, Any]) -> bool:
        if "AND" in condition:
            return all(DeterministicEvaluator.evaluate_condition(c, context) for c in condition["AND"])
        if "OR" in condition:
            return any(DeterministicEvaluator.evaluate_condition(c, context) for c in condition["OR"])
        
        # Simple operator evaluation
        if "field" in condition and "operator" in condition and "value" in condition:
            actual_val = DeterministicEvaluator._get_value(context, condition["field"])
            expected_val = condition["value"]
            op = condition["operator"]

            if actual_val is None:
                return False

            try:
                if op == "==": return actual_val == expected_val
                if op == "!=": return actual_val != expected_val
                if op == ">=": return float(actual_val) >= float(expected_val)
                if op == "<=": return float(actual_val) <= float(expected_val)
                if op == ">": return float(actual_val) > float(expected_val)
                if op == "<": return float(actual_val) < float(expected_val)
                if op == "IN": return actual_val in expected_val
            except (ValueError, TypeError):
                return False
                
        return False

class PolicyEngineService:
    def __init__(self, db: Session):
        self.db = db

    def evaluate(self, request: PolicyEvaluationRequest) -> PolicyEvaluationResponse:
        now = datetime.now(timezone.utc)
        
        # 1. Fetch active policies for category
        query = select(PolicyRule).where(
            PolicyRule.category == request.policy_category,
            PolicyRule.status == PolicyStatusEnum.ACTIVE,
            (PolicyRule.effective_start_date == None) | (PolicyRule.effective_start_date <= now),
            (PolicyRule.effective_end_date == None) | (PolicyRule.effective_end_date >= now)
        ).order_by(PolicyRule.priority.desc())
        
        rules = self.db.scalars(query).all()

        # 2. Build Context Data
        context = {}
        if request.patient_id:
            patient = self.db.get(Patient, request.patient_id)
            if patient:
                age = (now.date() - patient.dob).days / 365.25
                context["patient"] = {
                    "age": age,
                    "gender": patient.gender.value if patient.gender else None,
                    "blood_group": patient.blood_group
                }
        
        if request.admission_id:
            admission = self.db.get(Admission, request.admission_id)
            if admission:
                context["admission"] = {
                    "status": admission.status.value,
                    "type": "emergency" if getattr(admission, 'type', None) == 'emergency' else "standard"
                }

        # 3. Evaluate Rules
        matched_rules = []
        failed_rules = []
        required_documents = []
        requires_manual_review = False
        decision = "NOT_ELIGIBLE"
        explanation = "No rules matched the current context."

        for rule in rules:
            if not rule.rule_logic_json:
                continue
            
            # Extract IF condition
            condition = rule.rule_logic_json.get("IF", {})
            if condition:
                is_match = DeterministicEvaluator.evaluate_condition(condition, context)
            else:
                is_match = True # No condition = unconditionally applies if active

            if is_match:
                matched_rules.append(rule.rule_code)
                if rule.requires_manual_review:
                    requires_manual_review = True
                
                # Apply THEN action
                action = rule.rule_logic_json.get("THEN", {})
                if action.get("eligibility"):
                    decision = action.get("eligibility")
                    explanation = f"Matched rule {rule.rule_code}: {rule.description}"
                    
                if action.get("required_documents"):
                    required_documents.extend(action.get("required_documents"))
                    
                # Conflict resolution: we process in priority order. 
                # If it's a hard outcome, we break to respect priority overriding.
                if action.get("stop_processing", False):
                    break
            else:
                failed_rules.append(rule.rule_code)

        if requires_manual_review:
            decision = "REQUIRES_MANUAL_REVIEW"

        # 4. Audit Log
        audit = PolicyEvaluationAudit(
            patient_id=request.patient_id,
            admission_id=request.admission_id,
            user_id=request.user_id,
            policy_category=request.policy_category,
            decision=decision,
            reason=explanation,
            matched_rules_json=matched_rules,
            failed_rules_json=failed_rules,
            required_documents_json=required_documents
        )
        self.db.add(audit)
        self.db.commit()

        return PolicyEvaluationResponse(
            decision=decision,
            eligibility=decision,
            authorization_status="AUTHORIZED" if decision == "ELIGIBLE" else "NOT_AUTHORIZED",
            matched_rules=matched_rules,
            failed_rules=failed_rules,
            explanation=explanation,
            required_documents=required_documents,
            warnings=[],
            manual_review_requirement=requires_manual_review,
            policy_version=rules[0].version if rules else 0,
            evaluation_timestamp=now
        )
