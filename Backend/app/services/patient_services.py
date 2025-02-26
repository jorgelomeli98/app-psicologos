from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.patient import Patient
from app.schemas.patients import PatientCreate

def search_patient(db: Session, key: str, value: any, current_user_id: int) -> Patient:
    expresion = {key: value, "psychologist_id": current_user_id}
    patient = db.query(Patient).filter_by(**expresion).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="patient not found")
    return patient

def create_patient_db(db: Session, patient: PatientCreate, current_user_id: str):
    try:
        verify = search_patient(db, "email", str(patient.email), current_user_id)
        if type(verify) == Patient:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="el usuario ya existe")
    except HTTPException as e:
        if e.status_code == status.HTTP_404_NOT_FOUND:
            pass
        else:
            raise

    new_patient = Patient(**patient.model_dump(),
                        psychologist_id = current_user_id)

    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return new_patient