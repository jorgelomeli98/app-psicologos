from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, timezone

class Appointment(Base):
    __tablename__ = "appointments" #Citas
    
    # IDs
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False) #Relacion muchos a uno a Patient
    psychologist_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    duration = Column(Integer, default=60)
    notes = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))


    # Relaciones
    from app.models.attendance import Attendance
    attendance = relationship("Attendance", back_populates="appointment", uselist=False, cascade="all, delete")
    
    patient = relationship("Patient", back_populates="appointment")

    psychologist = relationship("User", back_populates="appointments")