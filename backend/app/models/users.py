import enum
from sqlalchemy import Column, String, Enum
from app.models.base import Base, UUIDMixin, TimestampMixin

class RoleEnum(str, enum.Enum):
    ADMIN = "ADMIN"
    DOCTOR = "DOCTOR"
    NURSE = "NURSE"
    POLICY_OFFICER = "POLICY_OFFICER"
    RECEPTIONIST = "RECEPTIONIST"

class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)
    specialty = Column(String(255), nullable=True) # e.g. Cardiology
