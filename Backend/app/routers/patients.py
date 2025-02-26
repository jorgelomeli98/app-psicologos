from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.patient import Patient as PatientModel
from app.schemas.patients import PatientCreate, Patient as PatientSchema
from app.dependencies import get_current_user
from app.services.patient_services import search_patient, create_patient_db
from app.services.user_services import verify_user

router = APIRouter(prefix="/patients", tags=["Patients"])

@router.post("/register", response_model=PatientSchema)
async def create_patient(patient: PatientCreate, 
                         db: Session = Depends(get_db), 
                         current_user: dict = Depends(get_current_user)):
    
    verify_user(current_user)
    return create_patient_db(db, patient, current_user["id"])


@router.get("/{patient_id}")
async def get_patient_by_id(patient_id: int, 
                            db: Session = Depends(get_db), 
                            current_user: dict = Depends(get_current_user)):
    
    verify_user(current_user)
    return search_patient(db, "id", patient_id, PatientModel.psychologist_id)

@router.get("/", response_model=list[PatientSchema])
async def get_patients(db: Session = Depends(get_db), 
                 current_user: dict = Depends(get_current_user)):
    
    verify_user(current_user)

    patients = db.query(PatientModel).filter(PatientModel.psychologist_id == current_user["id"]).all()
    return patients

@router.put("/{patient_id}", response_model=PatientSchema)
async def update_patient( 
                         patient_id: int,
                         updated_data: PatientCreate, 
                         db: Session = Depends(get_db), 
                         current_user: dict = Depends(get_current_user)):
    
    verify_user(current_user)

    patient = search_patient(db, "id", patient_id, current_user["id"])
    for key, value in updated_data.model_dump().items():
        setattr(patient, key, value)
        
    db.commit()
    db.refresh(patient)
    return patient

@router.delete("/{patient_id}")
async def delete_patient(patient_id: int, 
                         db: Session = Depends(get_db), 
                         current_user: dict = Depends(get_current_user)):
    
    patient = search_patient(db, "id", patient_id, current_user["id"])
    db.delete(patient)
    db.commit()
    return {"detail": "Paciente eliminado"}