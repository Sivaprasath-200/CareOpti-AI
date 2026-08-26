import enum
from sqlalchemy import Column, String, Date, Boolean, ForeignKey, Float, Enum
from sqlalchemy.orm import relationship
from app.models.base import Base, UUIDMixin, TimestampMixin

class GenderEnum(str, enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"

class Patient(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "patients"

    mrn = Column(String(100), unique=True, index=True, nullable=False) # Medical Record Number
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    dob = Column(Date, nullable=False)
    gender = Column(Enum(GenderEnum), nullable=False)
    blood_group = Column(String(10), nullable=True)
    contact_number = Column(String(50), nullable=True)
    emergency_contact = Column(String(255), nullable=True)

    insurances = relationship("Insurance", back_populates="patient")
    admissions = relationship("Admission", back_populates="patient")
    medical_history = relationship("MedicalHistory", back_populates="patient")
    allergies = relationship("Allergy", back_populates="patient")
    vitals = relationship("VitalSign", back_populates="patient")
    labs = relationship("LabResult", back_populates="patient")
    diagnoses = relationship("Diagnosis", back_populates="patient")
    medications = relationship("Medication", back_populates="patient")
    treatment_plans = relationship("TreatmentPlan", back_populates="patient")
    predictions = relationship("AIPrediction", back_populates="patient")
    risk_scores = relationship("RiskScore", back_populates="patient")

class Insurance(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "insurances"

    patient_id = Column(ForeignKey("patients.id"), nullable=False, index=True)
    provider_name = Column(String(255), nullable=False)
    policy_number = Column(String(100), nullable=False, index=True)
    coverage_limit = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)

    patient = relationship("Patient", back_populates="insurances")
    claims = relationship("InsuranceClaim", back_populates="insurance")

class InsuranceClaim(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "insurance_claims"

    insurance_id = Column(ForeignKey("insurances.id"), nullable=False, index=True)
    admission_id = Column(ForeignKey("admissions.id"), nullable=False, index=True)
    claim_amount = Column(Float, nullable=False)
    status = Column(String(50), default="PENDING") # PENDING, APPROVED, REJECTED

    insurance = relationship("Insurance", back_populates="claims")
    admission = relationship("Admission", back_populates="claims")

class GovernmentScheme(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "government_schemes"

    name = Column(String(255), nullable=False, unique=True)
    description = Column(String(1000), nullable=True)
    eligibility_criteria_json = Column(String, nullable=True) # JSON string of rules
