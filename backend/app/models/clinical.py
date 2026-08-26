import enum
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from app.models.base import Base, UUIDMixin, TimestampMixin

class AdmissionStatusEnum(str, enum.Enum):
    PLANNED = "PLANNED"
    ADMITTED = "ADMITTED"
    DISCHARGED = "DISCHARGED"
    TRANSFERRED = "TRANSFERRED"

class Admission(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "admissions"

    patient_id = Column(ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id = Column(ForeignKey("users.id"), nullable=False, index=True)
    bed_id = Column(ForeignKey("beds.id"), nullable=True, index=True)
    status = Column(Enum(AdmissionStatusEnum), nullable=False, default=AdmissionStatusEnum.PLANNED)
    admission_date = Column(DateTime(timezone=True), nullable=True)
    discharge_date = Column(DateTime(timezone=True), nullable=True)

    patient = relationship("Patient", back_populates="admissions")
    doctor = relationship("User")
    bed = relationship("Bed", back_populates="admissions")
    claims = relationship("InsuranceClaim", back_populates="admission")

class Appointment(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "appointments"
    patient_id = Column(ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id = Column(ForeignKey("users.id"), nullable=False, index=True)
    scheduled_time = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(50), default="SCHEDULED")

class Diagnosis(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "diagnoses"
    patient_id = Column(ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id = Column(ForeignKey("users.id"), nullable=False)
    icd10_code = Column(String(50), nullable=True)
    description = Column(Text, nullable=False)
    clinical_status = Column(String(50), default="ACTIVE")
    patient = relationship("Patient", back_populates="diagnoses")

class Symptom(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "symptoms"
    patient_id = Column(ForeignKey("patients.id"), nullable=False, index=True)
    description = Column(Text, nullable=False)
    severity = Column(String(50), nullable=True)

class VitalSign(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "vital_signs"
    patient_id = Column(ForeignKey("patients.id"), nullable=False, index=True)
    heart_rate = Column(Float, nullable=True)
    blood_pressure_systolic = Column(Float, nullable=True)
    blood_pressure_diastolic = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    spo2 = Column(Float, nullable=True)
    recorded_at = Column(DateTime(timezone=True), nullable=False)
    patient = relationship("Patient", back_populates="vitals")

class LabResult(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "lab_results"
    patient_id = Column(ForeignKey("patients.id"), nullable=False, index=True)
    test_name = Column(String(255), nullable=False)
    result_value = Column(String(255), nullable=False)
    unit = Column(String(50), nullable=True)
    reference_range = Column(String(100), nullable=True)
    patient = relationship("Patient", back_populates="labs")

class Medication(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "medications"
    patient_id = Column(ForeignKey("patients.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    dosage = Column(String(100), nullable=False)
    frequency = Column(String(100), nullable=False)
    patient = relationship("Patient", back_populates="medications")

class Allergy(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "allergies"
    patient_id = Column(ForeignKey("patients.id"), nullable=False, index=True)
    allergen = Column(String(255), nullable=False)
    severity = Column(String(50), nullable=True)
    patient = relationship("Patient", back_populates="allergies")

class MedicalHistory(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "medical_history"
    patient_id = Column(ForeignKey("patients.id"), nullable=False, index=True)
    condition_name = Column(String(255), nullable=False)
    patient = relationship("Patient", back_populates="medical_history")

class TreatmentPlan(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "treatment_plans"
    patient_id = Column(ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id = Column(ForeignKey("users.id"), nullable=False)
    description = Column(Text, nullable=False)
    patient = relationship("Patient", back_populates="treatment_plans")

class ClinicalNote(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "clinical_notes"
    patient_id = Column(ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id = Column(ForeignKey("users.id"), nullable=False, index=True)
    note_text = Column(Text, nullable=False)
