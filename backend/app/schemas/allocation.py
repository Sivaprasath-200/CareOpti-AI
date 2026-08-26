from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from datetime import datetime
from uuid import UUID

class ConstraintEvidence(BaseModel):
    hard_constraints_passed: bool
    reasons: List[str]
    rejected_candidates: List[str]
    capacity_stats: Dict[str, Any]

class OptimizationRecommendation(BaseModel):
    allocation_id: UUID
    admission_id: UUID
    patient_id: UUID
    recommended_bed_id: Optional[UUID] = None
    recommended_doctor_id: Optional[UUID] = None
    recommended_department_id: Optional[UUID] = None
    priority: int
    optimization_score: float
    status: str
    constraints_evidence: ConstraintEvidence
    warning: str = "AI-assisted optimization recommendation \u2014 requires authorized clinical review."

class ConfirmAllocationRequest(BaseModel):
    reviewer_id: UUID
    action: str # "APPROVE" or "REJECT"

class AllocationResponse(BaseModel):
    message: str
    allocation_id: UUID
    status: str
