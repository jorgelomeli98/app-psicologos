from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.models.appointment import Appointment
from app.schemas.appointment import AppointmentCreate
from datetime import datetime, timedelta

def search_appointment(db: Session, key: str, value: any, patient_id: int, current_user_id: int, exists: bool = False) -> Appointment|bool:
    # si exists = True entonces retornara un boleano, si exists es False, retornara el usuario o una exepcion
    expresion = {key: value, "patient_id": patient_id, "psychologist_id": current_user_id}
    appointment = db.query(Appointment).filter_by(**expresion).first()
    if exists:
        if not appointment:
            return False
        else:
            return True
    else:
        if not appointment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found or does not belong to the psychologist/patient")
        
        return appointment
    
def create_appointment_function(db: Session, appointment_data: AppointmentCreate, current_user_id: int):

    if not is_time_available(db, current_user_id, appointment_data.date, appointment_data.duration):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Conflicting appointment in the selected time.")
    
    new_appointment = Appointment(**appointment_data.model_dump(), psychologist_id = current_user_id)
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)

    return new_appointment

def is_time_available(db: Session, psychologist_id: int, date: datetime, duration: int, exclude_appointment_id: int = None) -> bool:
    """
    Verifica si el horario está disponible para el psicólogo.

    :param db: Sesión de la base de datos
    :param psychologist_id: ID del psicólogo
    :param date: Fecha y hora de la nueva cita
    :param duration: Duración de la cita en minutos
    :param exclude_appointment_id: ID de la cita que se está actualizando (para evitar conflictos consigo misma)
    :return: True si el horario está disponible, False si hay conflicto
    """
    start_time = date
    end_time = start_time + timedelta(minutes=duration)

    query = db.query(Appointment).filter(
        Appointment.psychologist_id == psychologist_id,
        Appointment.date < end_time,
        func.date_add(Appointment.date, text(f"INTERVAL {duration} MINUTE")) > start_time 
    )

    if exclude_appointment_id:
        query = query.filter(Appointment.id != exclude_appointment_id)  # Excluir la misma cita si se está editando

    return not db.query(query.exists()).scalar()  # True si no hay conflictos, False si hay una cita en ese horario
