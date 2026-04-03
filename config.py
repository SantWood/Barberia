import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "barberia_clave_secreta_2024")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/barberia_db")
    DEBUG = os.getenv("FLASK_DEBUG", "False") == "True"
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False