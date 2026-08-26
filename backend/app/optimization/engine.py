import pulp
from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID
from typing import Dict, Any, Tuple

from app.models import Bed, Ward, Department, DoctorDepartment
from app.models.users import User, RoleEnum
from app.models.hospital import BedStatusEnum, BedTypeEnum
from app.models.clinical import Admission

def _get_severity_priority(severity: str) -> int:
    mapping = {
        "EMERGENCY": 100,
        "CRITICAL": 80,
        "HIGH": 60,
        "MODERATE": 40,
        "LOW": 20
    }
    return mapping.get(severity, 0)

def optimize_allocation(db: Session, admission_id: UUID, severity: str) -> Tuple[bool, Dict[str, Any]]:
    """
    Runs ILP to find the best bed and doctor for a single admission 
    (though could be expanded to batch assignment).
    """
    # 1. Fetch available beds
    available_beds = db.execute(
        select(Bed, Ward, Department)
        .join(Ward, Bed.ward_id == Ward.id)
        .join(Department, Ward.department_id == Department.id)
        .where(Bed.status == BedStatusEnum.AVAILABLE)
    ).all()
    
    # 2. Fetch available doctors (Users with Role = DOCTOR) and their departments
    # Note: We simplified by just grabbing all doctors and looking at current workload.
    doctors_query = db.execute(
        select(User, DoctorDepartment, Department)
        .join(DoctorDepartment, User.id == DoctorDepartment.doctor_id)
        .join(Department, DoctorDepartment.department_id == Department.id)
        .where(User.role == RoleEnum.DOCTOR)
    ).all()
    
    if not available_beds or not doctors_query:
        return False, {
            "reasons": ["No available beds or doctors in the hospital."],
            "rejected_candidates": [],
            "capacity_stats": {"available_beds": len(available_beds), "doctors": len(doctors_query)}
        }
        
    # We will formulate a small ILP
    prob = pulp.LpProblem("Hospital_Resource_Allocation", pulp.LpMaximize)
    
    # Variables: x[bed_id][doc_id] = 1 if assigned
    x = {}
    valid_pairs = []
    
    priority_score = _get_severity_priority(severity)
    is_icu_required = severity in ["EMERGENCY", "CRITICAL"]
    
    rejected = []
    
    for bed, ward, b_dept in available_beds:
        # Hard constraint: ICU required
        if is_icu_required and bed.bed_type != BedTypeEnum.ICU:
            rejected.append(f"Bed {bed.bed_number} rejected (Requires ICU)")
            continue
            
        for doc, doc_dept, d_dept in doctors_query:
            # Hard constraint: Dept mismatch
            # The doctor must belong to the department of the bed's ward
            if d_dept.id != b_dept.id:
                # We won't log all of these to keep logs small, just skip
                continue
                
            # Soft constraints / score
            # A base score for matching successfully
            score = priority_score 
            
            # Create binary variable
            var_name = f"assign_b{bed.id.hex[:8]}_d{doc.id.hex[:8]}"
            x[(bed.id, doc.id)] = pulp.LpVariable(var_name, cat="Binary")
            valid_pairs.append({
                "bed_id": bed.id,
                "doc_id": doc.id,
                "dept_id": b_dept.id,
                "score": score,
                "var": x[(bed.id, doc.id)]
            })
            
    if not valid_pairs:
        return False, {
            "reasons": ["No compatible bed/doctor pairs found satisfying hard constraints."],
            "rejected_candidates": rejected,
            "capacity_stats": {"available_beds": len(available_beds), "doctors": len(doctors_query)}
        }
        
    # Objective: Maximize total score
    prob += pulp.lpSum([p["score"] * p["var"] for p in valid_pairs])
    
    # Constraint: Select at most 1 pair (since we are doing single-patient allocation here)
    prob += pulp.lpSum([p["var"] for p in valid_pairs]) <= 1
    
    # Solve
    prob.solve(pulp.PULP_CBC_CMD(msg=False))
    
    if pulp.LpStatus[prob.status] != 'Optimal':
        return False, {
            "reasons": ["Solver could not find an optimal solution."],
            "rejected_candidates": rejected,
            "capacity_stats": {}
        }
        
    best_pair = None
    max_score = 0
    for p in valid_pairs:
        if pulp.value(p["var"]) == 1.0:
            best_pair = p
            max_score = p["score"]
            break
            
    if not best_pair:
        return False, {
            "reasons": ["Solver did not select any assignment."],
            "rejected_candidates": rejected,
            "capacity_stats": {}
        }
        
    return True, {
        "recommended_bed_id": str(best_pair["bed_id"]),
        "recommended_doctor_id": str(best_pair["doc_id"]),
        "recommended_department_id": str(best_pair["dept_id"]),
        "priority": priority_score,
        "optimization_score": max_score,
        "reasons": ["ILP solver successfully matched ICU/Dept constraints."],
        "rejected_candidates": rejected,
        "capacity_stats": {"available_beds": len(available_beds), "doctors": len(doctors_query)}
    }
