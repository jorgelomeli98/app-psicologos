from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Patient(Base):
    __tablename__ = "patients"

    # IDs
    id = Column(Integer, primary_key=True, index=True)
    psychologist_id = Column(Integer, ForeignKey("users.id")) # Relacion uno a muchos a Users

    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phone = Column(String(15), nullable=True)
    notes = Column(String(255), nullable=True) #Notas del psicologo
    

    psychologist = relationship("User", back_populates="patient")

    appointment = relationship("Appointment", back_populates="patient")