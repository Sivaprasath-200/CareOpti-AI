from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Dict, Any
from uuid import UUID
from datetime import datetime, timezone

from app.db.database import get_db
from app.models.clinical import Admission, AdmissionStatusEnum
from app.models.optimization import ResourceAllocation, AllocationStatusEnum
from app.models.hospital import Bed, BedStatusEnum
from app.schemas.allocation import OptimizationRecommendation, ConfirmAllocationRequest, AllocationResponse, ConstraintEvidence
from app.optimization.engine import optimize_allocation

router = APIRouter(prefix="/api/v1/admissions", tags=["Resource Allocation"])

@router.post("/{admission_id}/optimize", response_model=OptimizationRecommendation)
def optimize_admission_allocation(admission_id: UUID, severity: str, db: Session = Depends(get_db)):
    """
    Run ILP optimization for a single admission based on Phase 4 severity.
    """
    admission = db.get(Admission, admission_id)
    if not admission:
        raise HTTPException(status_code=404, detail="Admission not found")
        
    # Run Engine
    success, result = optimize_allocation(db, admission_id, severity)
    
    if not success:
        # Create a rejected dummy record or just return NO_FEASIBLE_ALLOCATION via HTTP error
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "NO_FEASIBLE_ALLOCATION",
                "evidence": result
            }
        )
        
    # Store recommendation
    allocation = ResourceAllocation(
        admission_id=admission.id,
        patient_id=admission.patient_id,
        recommended_bed_id=result["recommended_bed_id"],
        recommended_doctor_id=result["recommended_doctor_id"],
        recommended_department_id=result["recommended_department_id"],
        priority=result["priority"],
        optimization_score=result["optimization_score"],
        status=AllocationStatusEnum.RECOMMENDED,
        constraints_evidence=result
    )
    db.add(allocation)
    db.commit()
    db.refresh(allocation)
    
    return OptimizationRecommendation(
        allocation_id=allocation.id,
        admission_id=allocation.admission_id,
        patient_id=allocation.patient_id,
        recommended_bed_id=allocation.recommended_bed_id,
        recommended_doctor_id=allocation.recommended_doctor_id,
        recommended_department_id=allocation.recommended_department_id,
        priority=allocation.priority,
        optimization_score=allocation.optimization_score,
        status=allocation.status.value,
        constraints_evidence=ConstraintEvidence(
            hard_constraints_passed=True,
            reasons=result.get("reasons", []),
            rejected_candidates=result.get("rejected_candidates", []),
            capacity_stats=result.get("capacity_stats", {})
        )
    )

@router.get("/{admission_id}/recommendation")
def get_recommendation(admission_id: UUID, db: Session = Depends(get_db)):
    alloc = db.execute(
        select(ResourceAllocation)
        .where(ResourceAllocation.admission_id == admission_id)
        .order_by(ResourceAllocation.created_at.desc())
    ).scalars().first()
    
    if not alloc:
        raise HTTPException(status_code=404, detail="No recommendation found")
    return alloc

@router.post("/{admission_id}/confirm-allocation", response_model=AllocationResponse)
def confirm_allocation(admission_id: UUID, request: ConfirmAllocationRequest, db: Session = Depends(get_db)):
    alloc = db.execute(
        select(ResourceAllocation)
        .where(
            ResourceAllocation.admission_id == admission_id,
            ResourceAllocation.status == AllocationStatusEnum.RECOMMENDED
        )
        .order_by(ResourceAllocation.created_at.desc())
    ).scalars().first()
    
    if not alloc:
        raise HTTPException(status_code=404, detail="No pending recommendation to confirm.")
        
    admission = db.get(Admission, admission_id)
    now = datetime.now(timezone.utc)
    
    alloc.reviewed_by = request.reviewer_id
    alloc.reviewed_at = now
    
    if request.action.upper() == "APPROVE":
        alloc.status = AllocationStatusEnum.APPROVED
        
        # Update admission
        if alloc.recommended_bed_id:
            admission.bed_id = alloc.recommended_bed_id
            # Also update bed status
            bed = db.get(Bed, alloc.recommended_bed_id)
            if bed:
                bed.status = BedStatusEnum.OCCUPIED
                
        if alloc.recommended_doctor_id:
            admission.doctor_id = alloc.recommended_doctor_id
            
        admission.status = AdmissionStatusEnum.ADMITTED
        
    elif request.action.upper() == "REJECT":
        alloc.status = AllocationStatusEnum.REJECTED
    else:
        raise HTTPException(status_code=400, detail="Action must be APPROVE or REJECT")
        
    db.commit()
    
    return AllocationResponse(
        message=f"Allocation {request.action.upper()}D successfully",
        allocation_id=alloc.id,
        status=alloc.status.value
    )
