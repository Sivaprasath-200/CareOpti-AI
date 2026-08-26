import enum
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.models.base import Base, UUIDMixin, TimestampMixin

class AlertSeverityEnum(str, enum.Enum):
    INFO = "INFO"
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class RiskCategoryEnum(str, enum.Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ClinicalRule(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "cdss_clinical_rules"
    
    rule_code = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    condition_logic = Column(Text, nullable=False) # e.g. "hr > 120"
    severity = Column(Enum(AlertSeverityEnum), nullable=False)
    message = Column(Text, nullable=False)
    recommended_action = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    version = Column(String(50), default="1.0")
    effective_date = Column(DateTime(timezone=True), nullable=True)
    source_reference = Column(String(255), nullable=True)

class CDSSEvaluation(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "cdss_evaluations"
    
    patient_id = Column(ForeignKey("patients.id"), nullable=False, index=True)
    admission_id = Column(ForeignKey("admissions.id"), nullable=True, index=True)
    clinician_review_required = Column(Boolean, default=True)
    
    # Relationships to results
    risk_assessments = relationship("RiskAssessment", back_populates="evaluation", cascade="all, delete-orphan")
    clinical_alerts = relationship("ClinicalAlert", back_populates="evaluation", cascade="all, delete-orphan")
    medication_alerts = relationship("MedicationSafetyAlert", back_populates="evaluation", cascade="all, delete-orphan")

class RiskAssessment(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "cdss_risk_assessments"
    
    evaluation_id = Column(ForeignKey("cdss_evaluations.id"), nullable=False)
    patient_id = Column(ForeignKey("patients.id"), nullable=False)
    
    risk_score = Column(Float, nullable=False)
    risk_category = Column(Enum(RiskCategoryEnum), nullable=False)
    confidence = Column(Float, nullable=False)
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(50), nullable=False)
    contributing_factors = Column(JSONB, nullable=True)
    
    evaluation = relationship("CDSSEvaluation", back_populates="risk_assessments")

class ClinicalAlert(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "cdss_clinical_alerts"
    
    evaluation_id = Column(ForeignKey("cdss_evaluations.id"), nullable=False)
    patient_id = Column(ForeignKey("patients.id"), nullable=False)
    rule_id = Column(ForeignKey("cdss_clinical_rules.id"), nullable=True)
    
    category = Column(String(100), nullable=False)
    severity = Column(Enum(AlertSeverityEnum), nullable=False)
    message = Column(Text, nullable=False)
    supporting_value = Column(String(255), nullable=True)
    rule_version = Column(String(50), nullable=True)
    
    # Acknowledgement
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(ForeignKey("users.id"), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    review_note = Column(Text, nullable=True)
    
    evaluation = relationship("CDSSEvaluation", back_populates="clinical_alerts")

class MedicationSafetyAlert(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "cdss_medication_alerts"
    
    evaluation_id = Column(ForeignKey("cdss_evaluations.id"), nullable=False)
    patient_id = Column(ForeignKey("patients.id"), nullable=False)
    
    medication = Column(String(255), nullable=False)
    alert_type = Column(String(100), nullable=False) # e.g. "ALLERGY", "DUPLICATION", "INTERACTION"
    severity = Column(Enum(AlertSeverityEnum), nullable=False)
    explanation = Column(Text, nullable=False)
    
    evaluation = relationship("CDSSEvaluation", back_populates="medication_alerts")

class GuidelineReference(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "cdss_guidelines"
    
    title = Column(String(255), nullable=False)
    condition_category = Column(String(100), nullable=False)
    version = Column(String(50), default="1.0")
    source = Column(String(255), nullable=True)
    effective_date = Column(DateTime(timezone=True), nullable=True)
    recommendation_mappings = Column(JSONB, nullable=True)
