from fastapi import FastAPI
from app.database import Base, engine
from app.routers import users, patients, appointments, attendances

app = FastAPI()

#crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

app.include_router(users.router)
app.include_router(patients.router)
app.include_router(appointments.router)
app.include_router(attendances.router)

@app.get("/")
async def home():
    return {"message": "Bienvenido al sistema para psicologos"}