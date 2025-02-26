from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.attendance import Attendance
from app.models.appointment import Appointment
from app.models.patient import Patient
from app.schemas.attendance import AttendanceCreate, AttendanceSchema
from app.services.appointment_services import search_appointment

"""
    Para buscar:
    User(user_id)
        id: int

        Patient(patient_id, user_id)
            patient_id: int
            user_id: int

            Appointment(appointment_id, patient_id)
                appointment_id: int
                patient_id: int
            
            Attendance(attendance_id, appointment_id)
                attendance_id: int
                appointment_id: int


"""



def search_attendance(db: Session, current_user_id: int, appointment_id: int):
    attendance = db.query(Attendance).join(Appointment).join(Patient).filter( 
        Appointment.id == appointment_id, 
        Patient.psychologist_id == current_user_id
    ).first()
    
    if not attendance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="attendance not found")
    return attendance

def create_attendance_function(db: Session, attendance_data: AttendanceCreate, patient_id: int, current_user_id: int) -> AttendanceSchema:
    try:
        search_appointment(db, "id", attendance_data.appointment_id, patient_id, current_user_id)
        new_attendence = Attendance(**attendance_data.model_dump())
        db.add(new_attendence)
        db.commit()
        db.refresh(new_attendence)

        return new_attendence
    
    except IntegrityError:
        db.rollback()  # Deshacer los cambios en caso de error
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Conflict in data")
    
    except Exception as e:
        db.rollback()  # Deshacer los cambios en caso de cualquier otro error
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

