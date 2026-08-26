from pydantic import BaseModel
from datetime import date
from typing import Optional
from uuid import UUID

class PatientBase(BaseModel):
    mrn: str
    first_name: str
    last_name: str
    dob: date
    gender: str
    blood_group: Optional[str] = None
    contact_number: Optional[str] = None
    emergency_contact: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class PatientRead(PatientBase):
    id: UUID
    
    class Config:
        from_attributes = True
