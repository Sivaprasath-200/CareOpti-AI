from sqlalchemy import Column, String, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from app.models.base import Base, UUIDMixin, TimestampMixin

class BedStatusEnum(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    OCCUPIED = "OCCUPIED"
    CLEANING = "CLEANING"
    MAINTENANCE = "MAINTENANCE"

class BedTypeEnum(str, enum.Enum):
    GENERAL = "GENERAL"
    ICU = "ICU"
    ER = "ER"
    MATERNITY = "MATERNITY"

class Hospital(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "hospitals"

    name = Column(String(255), nullable=False)
    address = Column(String(500), nullable=True)
    contact_number = Column(String(50), nullable=True)

    departments = relationship("Department", back_populates="hospital")

class Department(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "departments"

    name = Column(String(255), nullable=False)
    hospital_id = Column(ForeignKey("hospitals.id"), nullable=False, index=True)

    hospital = relationship("Hospital", back_populates="departments")
    wards = relationship("Ward", back_populates="department")
    doctors = relationship("DoctorDepartment", back_populates="department")

class DoctorDepartment(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "doctor_departments"
    # Many to many association between Users(Doctors) and Departments
    doctor_id = Column(ForeignKey("users.id"), nullable=False, index=True)
    department_id = Column(ForeignKey("departments.id"), nullable=False, index=True)

    department = relationship("Department", back_populates="doctors")
    doctor = relationship("User") # Links to the User model

class Ward(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "wards"

    name = Column(String(255), nullable=False)
    department_id = Column(ForeignKey("departments.id"), nullable=False, index=True)

    department = relationship("Department", back_populates="wards")
    beds = relationship("Bed", back_populates="ward")

class Bed(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "beds"

    bed_number = Column(String(50), nullable=False)
    ward_id = Column(ForeignKey("wards.id"), nullable=False, index=True)
    bed_type = Column(Enum(BedTypeEnum), nullable=False, default=BedTypeEnum.GENERAL)
    status = Column(Enum(BedStatusEnum), nullable=False, default=BedStatusEnum.AVAILABLE)

    ward = relationship("Ward", back_populates="beds")
    admissions = relationship("Admission", back_populates="bed")
