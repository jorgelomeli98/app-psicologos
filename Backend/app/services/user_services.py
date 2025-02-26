from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.core.security import hash_password


def search_user(db: Session, key: str, value: any):
    expresion = {key: value}
    user = db.query(User).filter_by(**expresion).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_user_by_email(db: Session, email: str) -> User:
    return db.query(User).filter(User.email == email).first()

def get_all_users(db: Session) -> list[User]:
    return db.query(User).all()

def create_user(db: Session, user: UserCreate) -> User:
    hashed_password = hash_password(user.password)
    db_user = User(name=user.name, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, id: int):
    user = db.query(User).filter(User.id == id).first()
    db.delete(user)
    db.commit()
    return {"Message": "Usuario eliminado"}

def verify_user(current_user: dict):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Acceso denegado")
    else:
        pass