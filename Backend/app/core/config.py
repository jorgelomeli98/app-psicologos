from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = "HS256"  # Algoritmo para firmar los JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # Tiempo de expiración del token

settings = Settings()
