from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.appointment import Appointment
from app.models.attendance import Attendance
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentSchema
from app.dependencies import get_current_user
from datetime import date, timedelta
from app.services.user_services import verify_user
from app.services.patient_services import search_patient
from app.services.attendance_services import search_attendance
from app.services.appointment_services import create_appointment_function, search_appointment, is_time_available

router = APIRouter(prefix="/appointments", tags=["Appointments"])

class CommonParams:
    def __init__(self, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
        self.db = db
        self.current_user = current_user

@router.post("/", response_model=AppointmentSchema)
async def create_appointment(appointment_data: AppointmentCreate, 
                             common: CommonParams = Depends(), 
                             ):
    verify_user(common.current_user)

    return create_appointment_function(common.db, appointment_data, common.current_user["id"])

@router.get("/day/{selected_date}")
async def get_appointment_by_day(selected_date: date,
                                 limit: int = 10, 
                                 offset: int = 0,
                                 attended: bool = None,  
                                 common: CommonParams = Depends()):
    
    verify_user(common.current_user)

    query = (
        common.db.query(Appointment)
        .filter(
            Appointment.date >= selected_date, 
            Appointment.date < selected_date + timedelta(days=1), 
            Appointment.psychologist_id == common.current_user["id"]
        )
    )

    
    if attended is not None:

        query = query.join(Attendance).filter(Attendance.attended == attended)
    
    appointments = query.offset(offset).limit(limit).all()
    
    return appointments

@router.get("/range/")
async def get_appointments_by_date_range(start_date: date, end_date: date, 
                                         common: CommonParams = Depends(),
                                         skip: int = 0, limit: int = 10, attended: bool = None):
    verify_user(common.current_user)

    query = (
        common.db.query(Appointment)
        .filter(Appointment.date >= start_date, Appointment.date <= end_date)
        .filter_by(psychologist_id=common.current_user["id"])
    )

    if attended is not None:
        query = query.join(Attendance).filter(Attendance.attended == attended)

    appointments = query.offset(skip).limit(limit).all()
    return appointments

@router.get("/{patient_id}/{appointment_id}", response_model=AppointmentSchema)
async def get_appointment(appointment_id: int,
                          patient_id: int,  
                          common: CommonParams = Depends()):
    verify_user(common.current_user)

    return search_appointment(common.db, "id", appointment_id, patient_id, common.current_user["id"])

@router.get("/{patient_id}", response_model=list[AppointmentSchema])
async def get_appointments_by_patient(patient_id: int,
                                      limit: int = 10, 
                                      offset: int = 0, # conpaginación  
                                      common: CommonParams = Depends()):
    verify_user(common.current_user)

    search_patient(common.db, "id", patient_id, common.current_user["id"])

    appointments = (
        common.db.query(Appointment)
        .filter_by(patient_id = patient_id, psychologist_id = common.current_user["id"])
        .limit(limit)
        .offset(offset)
        .all() 
    )

    return appointments



@router.put("/{patient_id}/{appointment_id}", response_model=AppointmentSchema)
async def update_appointment(appointment_id: int,
                             patient_id: int, 
                             updated_data: AppointmentUpdate,
                             common: CommonParams = Depends()):
    
    verify_user(common.current_user)

    appointment = search_appointment(common.db, "id", appointment_id, patient_id, common.current_user["id"])

    if updated_data.date or updated_data.duration:
        new_date = updated_data.date if updated_data.date else appointment.date
        new_duration = updated_data.duration if updated_data.duration else appointment.duration
    
    if not is_time_available(common.db, common.current_user["id"], new_date, new_duration, exclude_appointment_id=appointment_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Conflicting appointment in the selected time.")


    for key, value in updated_data.model_dump(exclude_unset=True).items():
        setattr(appointment, key, value)

    common.db.commit()
    common.db.refresh(appointment)

    return appointment

@router.delete("/{patient_id}/{appointment_id}")
async def delete_appointment(patient_id: int, 
                             appointment_id: int, 
                             common: CommonParams = Depends()):
    
    verify_user(common.current_user)

    appointment = search_appointment(common.db, "id", appointment_id, patient_id, common.current_user["id"])

    common.db.delete(appointment)
    common.db.commit()

    return {"message": "Appointment deleted successfully"}
