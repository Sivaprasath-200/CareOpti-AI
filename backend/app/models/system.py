import enum
from sqlalchemy import Column, String, ForeignKey, Text, Float, JSON, Integer, Boolean, DateTime, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import Base, UUIDMixin, TimestampMixin

class PolicyStatusEnum(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DRAFT = "DRAFT"

class PolicyRule(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "policy_rules"
    rule_code = Column(String(100), index=True, nullable=False)
    version = Column(Integer, nullable=False, default=1)
    category = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    rule_logic_json = Column(JSON, nullable=True) # Deterministic rules
    priority = Column(Integer, nullable=False, default=10)
    status = Column(Enum(PolicyStatusEnum), nullable=False, default=PolicyStatusEnum.DRAFT)
    effective_start_date = Column(DateTime(timezone=True), nullable=True)
    effective_end_date = Column(DateTime(timezone=True), nullable=True)
    requires_manual_review = Column(Boolean, nullable=False, default=False)
    source_reference = Column(String(255), nullable=True)

    __table_args__ = (
        UniqueConstraint('rule_code', 'version', name='uq_policy_rule_code_version'),
    )

class HospitalProtocol(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "hospital_protocols"
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)

class AIPrediction(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ai_predictions"
    patient_id = Column(ForeignKey("patients.id"), nullable=False, index=True)
    model_name = Column(String(100), nullable=False)
    prediction_result = Column(String(255), nullable=False)
    confidence_score = Column(Float, nullable=True)
    explanation_json = Column(JSON, nullable=True)
    patient = relationship("Patient", back_populates="predictions")

class RiskScore(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "risk_scores"
    patient_id = Column(ForeignKey("patients.id"), nullable=False, index=True)
    risk_type = Column(String(100), nullable=False) # e.g., READMISSION, SEPSIS
    score = Column(Float, nullable=False)
    patient = relationship("Patient", back_populates="risk_scores")

class AuditLog(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "audit_logs"
    user_id = Column(ForeignKey("users.id"), nullable=False, index=True)
    action = Column(String(255), nullable=False)
    resource_type = Column(String(100), nullable=True)
    resource_id = Column(String(255), nullable=True)
    ip_address = Column(String(50), nullable=True)

class PolicyEvaluationAudit(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "policy_evaluation_audits"
    
    patient_id = Column(ForeignKey("patients.id"), nullable=True, index=True)
    admission_id = Column(ForeignKey("admissions.id"), nullable=True, index=True)
    user_id = Column(ForeignKey("users.id"), nullable=True, index=True)
    policy_category = Column(String(100), nullable=False)
    decision = Column(String(100), nullable=False) # ELIGIBLE, NOT_ELIGIBLE, etc.
    reason = Column(Text, nullable=True)
    matched_rules_json = Column(JSON, nullable=True)
    failed_rules_json = Column(JSON, nullable=True)
    warnings_json = Column(JSON, nullable=True)
    required_documents_json = Column(JSON, nullable=True)
