from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.dependencies import get_current_user
from app.core.security import verify_password, create_access_token
from app.services.user_services import get_user_by_email, create_user, get_all_users, delete_user, search_user, verify_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
                db: Session = Depends(get_db)):
    # Buscar usuario en la base de datos
    user = get_user_by_email(db, form_data.username) #form_data.username en realidad es el email
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Crear un token de acceso
    access_token = create_access_token(data={"sub": user.email, "id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/", response_model=UserResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    #Verificar si ya esta registrado el email
    db_user = get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    # Crear el Usuario
    return create_user(db, user)

@router.get("/me", response_model=UserResponse)
async def read_users_me(db: Session = Depends(get_db), 
                        current_user: dict = Depends(get_current_user)):
    user_db = search_user(db, "email", current_user["sub"])
    return UserResponse.model_validate(user_db)

@router.get("/", response_model=list[UserResponse])
async def read_users(db: Session = Depends(get_db)):
    return get_all_users(db)

@router.delete("/{id}")
async def delete_user_by_id(id: int, 
                            db: Session = Depends(get_db), 
                            current_user: dict = Depends(get_current_user)):
    verify_user(current_user)
    try:
        return delete_user(db, id)
    except:
        raise HTTPException(status_code=400, detail="Usuario no encontrado")
    
@router.put("/me")
async def update_user(updated_data: UserCreate, 
                      db: Session = Depends(get_db), 
                      current_user: dict = Depends(get_current_user)):
    
    user = search_user(db, "id", current_user["id"])
    for key, value in updated_data.model_dump().items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user