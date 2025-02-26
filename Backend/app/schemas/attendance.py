from pydantic import BaseModel, condecimal
from typing import Optional
from datetime import datetime

FeeType = Optional[condecimal(max_digits=10, decimal_places=2)]

class AttendanceBase(BaseModel):
    attended: bool
    absence_reason: Optional[str] = None
    amount_paid: FeeType = None

class AttendanceCreate(AttendanceBase):
    appointment_id: int

class AttendanceUpdate(BaseModel):
    attended: Optional[bool] = None
    absence_reason: Optional[str] = None
    amount_paid: FeeType = None

class AttendanceSchema(AttendanceBase):
    id: int
    appointment_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True