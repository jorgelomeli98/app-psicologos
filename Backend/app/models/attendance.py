from sqlalchemy import Column, Integer, Boolean, String, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class Attendance(Base):
    __tablename__ = "attendances"
    
    # IDs
    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id", ondelete="CASCADE"), nullable=False) # Relacion uno a uno a Citas
    
    attended = Column(Boolean, nullable=False)
    absence_reason = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    amount_paid = Column(Numeric(10, 2), nullable=True)

    # Relaciones
    appointment = relationship("Appointment", back_populates="attendance")

