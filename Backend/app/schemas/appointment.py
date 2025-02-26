from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class AppointmentBase(BaseModel):
    date: datetime = Field(..., description="Fecha y hora de la cita")
    notes: Optional[str] = Field(None, max_length=255, description="Notas del psicologo sobre la cita")
    duration: Optional[int] = 60

class AppointmentCreate(AppointmentBase):
    patient_id: int = Field(..., description="ID del paciente al que pertenece la cita")

class AppointmentUpdate(BaseModel):
    date: Optional[datetime] = Field(None, description="Nueva fecha y hora de la cita")
    notes: Optional[str] = Field(None, max_length=255, description="Actualizar notas de la cita")
    duration: Optional[int] = None

class AppointmentSchema(AppointmentBase):
    id: int
    patient_id: int
    psychologist_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True