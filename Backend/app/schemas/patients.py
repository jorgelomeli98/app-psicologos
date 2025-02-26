from pydantic import BaseModel, EmailStr
from typing import Optional

class PatientBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    notes: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class Patient(PatientBase):
    id: int
    psychologist_id: int

    class Config:
        from_attributes = True