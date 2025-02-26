from fastapi import APIRouter, Depends
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.attendance import AttendanceCreate, AttendanceUpdate, AttendanceSchema
from app.services.attendance_services import search_attendance, create_attendance_function
from app.services.user_services import verify_user
from app.dependencies import get_current_user

router = APIRouter(prefix="/attendances", tags=["Attendances"])

@router.post("/{patient_id}", response_model=AttendanceSchema)
async def create_attendance(patient_id: int,  
                            attendance_data: AttendanceCreate, 
                            db: Session = Depends(get_db), 
                            current_user: dict = Depends(get_current_user)):
    verify_user(current_user)
    return create_attendance_function(db, attendance_data, patient_id, current_user["id"])

@router.get("/{appointment_id}/{attendance_id}", response_model=AttendanceSchema)
async def get_attendance(attendance_id: int, 
                         appointment_id: int,  
                         db: Session = Depends(get_db), 
                         current_user: dict = Depends(get_current_user)):
    verify_user(current_user)
    return search_attendance(db=db, attendance_id=attendance_id, current_user_id=current_user["id"], appointment_id=appointment_id)

@router.put("/{appointment_id}/{attendance_id}")
async def updated_attendance(attendance_id: int, 
                             appointment_id: int,
                             updated_data: AttendanceUpdate,  
                             db: Session = Depends(get_db), 
                             current_user: dict = Depends(get_current_user)):
    verify_user(current_user)

    attendance = search_attendance(db, attendance_id, current_user["id"], appointment_id)
    
    for key, value in updated_data.model_dump().items():
        if value is not None:
            setattr(attendance, key, value)
    
    attendance.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(attendance)
    return attendance

@router.delete("/{appointment_id}/{attendance_id}")
async def delete_attendance(attendance_id: int, 
                             appointment_id: int,  
                             db: Session = Depends(get_db), 
                             current_user: dict = Depends(get_current_user)):
    
    verify_user(current_user)

    attendance = search_attendance(db, attendance_id, current_user["id"], appointment_id)

    db.delete(attendance)
    db.commit()

    return {"message": "asistencia eliminada con exito"}