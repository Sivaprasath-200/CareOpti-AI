from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.db.database import get_db
from app.models import PolicyRule, PolicyStatusEnum
from app.schemas.policy import (
    PolicyRuleCreate, PolicyRuleUpdate, PolicyRuleRead, 
    PolicyEvaluationRequest, PolicyEvaluationResponse
)
from app.services.policy_engine import PolicyEngineService

router = APIRouter(prefix="/api/v1/policies", tags=["Policies"])

@router.post("/evaluate", response_model=PolicyEvaluationResponse)
def evaluate_policy(request: PolicyEvaluationRequest, db: Session = Depends(get_db)):
    engine = PolicyEngineService(db)
    return engine.evaluate(request)

@router.get("", response_model=List[PolicyRuleRead])
def get_policies(db: Session = Depends(get_db)):
    query = select(PolicyRule).order_by(PolicyRule.created_at.desc())
    return db.scalars(query).all()

@router.get("/{policy_id}", response_model=PolicyRuleRead)
def get_policy(policy_id: UUID, db: Session = Depends(get_db)):
    policy = db.get(PolicyRule, policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy

@router.get("/{policy_code}/history", response_model=List[PolicyRuleRead])
def get_policy_history(policy_code: str, db: Session = Depends(get_db)):
    query = select(PolicyRule).where(PolicyRule.rule_code == policy_code).order_by(PolicyRule.version.desc())
    return db.scalars(query).all()

@router.post("", response_model=PolicyRuleRead)
def create_policy(policy_in: PolicyRuleCreate, db: Session = Depends(get_db)):
    db_policy = PolicyRule(**policy_in.model_dump())
    db_policy.version = 1
    db.add(db_policy)
    db.commit()
    db.refresh(db_policy)
    return db_policy

@router.put("/{policy_id}", response_model=PolicyRuleRead)
def update_policy(policy_id: UUID, policy_in: PolicyRuleUpdate, db: Session = Depends(get_db)):
    existing_policy = db.get(PolicyRule, policy_id)
    if not existing_policy:
        raise HTTPException(status_code=404, detail="Policy not found")
        
    # We implement versioning: updating creates a new version, old is kept for history
    # Actually, proper versioning might mean creating a new row, but for PUT on a specific ID, 
    # we'll just update it in place if it's draft, or create a new version if active.
    # To strictly follow Phase 3: "Rule versioning"
    new_policy_data = existing_policy.__dict__.copy()
    new_policy_data.pop('_sa_instance_state', None)
    new_policy_data.pop('id', None)
    
    new_policy = PolicyRule(**new_policy_data)
    new_policy.version = existing_policy.version + 1
    
    update_data = policy_in.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(new_policy, k, v)
        
    # Set old policy to inactive
    existing_policy.status = PolicyStatusEnum.INACTIVE
    
    db.add(new_policy)
    db.commit()
    db.refresh(new_policy)
    return new_policy
