from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime
from uuid import UUID

class PolicyRuleBase(BaseModel):
    rule_code: str
    category: str
    description: str
    rule_logic_json: Optional[Dict[str, Any]] = None
    priority: int = 10
    status: str = "DRAFT"
    effective_start_date: Optional[datetime] = None
    effective_end_date: Optional[datetime] = None
    requires_manual_review: bool = False
    source_reference: Optional[str] = None

class PolicyRuleCreate(PolicyRuleBase):
    pass

class PolicyRuleUpdate(BaseModel):
    description: Optional[str] = None
    rule_logic_json: Optional[Dict[str, Any]] = None
    priority: Optional[int] = None
    status: Optional[str] = None
    effective_start_date: Optional[datetime] = None
    effective_end_date: Optional[datetime] = None
    requires_manual_review: Optional[bool] = None
    source_reference: Optional[str] = None

class PolicyRuleRead(PolicyRuleBase):
    id: UUID
    version: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PolicyEvaluationRequest(BaseModel):
    patient_id: Optional[UUID] = None
    admission_id: Optional[UUID] = None
    insurance_id: Optional[UUID] = None
    scheme_id: Optional[UUID] = None
    policy_category: str
    user_id: Optional[UUID] = None  # Who is triggering the evaluation

class PolicyEvaluationResponse(BaseModel):
    decision: str
    eligibility: str
    authorization_status: str
    matched_rules: List[str]
    failed_rules: List[str]
    explanation: str
    required_documents: List[str]
    warnings: List[str]
    manual_review_requirement: bool
    policy_version: int
    evaluation_timestamp: datetime
