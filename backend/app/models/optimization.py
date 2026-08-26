import enum
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Enum, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.models.base import Base, UUIDMixin, TimestampMixin

class AllocationStatusEnum(str, enum.Enum):
    RECOMMENDED = "RECOMMENDED"
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"

class ResourceAllocation(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "resource_allocations"

    admission_id = Column(ForeignKey("admissions.id"), nullable=False, index=True)
    patient_id = Column(ForeignKey("patients.id"), nullable=False, index=True)
    
    recommended_bed_id = Column(ForeignKey("beds.id"), nullable=True, index=True)
    recommended_doctor_id = Column(ForeignKey("users.id"), nullable=True, index=True)
    recommended_department_id = Column(ForeignKey("departments.id"), nullable=True, index=True)
    
    priority = Column(Integer, nullable=False, default=0)
    optimization_score = Column(Float, nullable=False, default=0.0)
    
    status = Column(Enum(AllocationStatusEnum), nullable=False, default=AllocationStatusEnum.RECOMMENDED)
    
    constraints_evidence = Column(JSONB, nullable=True) # Changed to JSONB for PostgreSQL
    
    reviewed_by = Column(ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    admission = relationship("Admission", foreign_keys=[admission_id])
    patient = relationship("Patient", foreign_keys=[patient_id])
    bed = relationship("Bed", foreign_keys=[recommended_bed_id])
    doctor = relationship("User", foreign_keys=[recommended_doctor_id])
    department = relationship("Department", foreign_keys=[recommended_department_id])
    reviewer = relationship("User", foreign_keys=[reviewed_by])
