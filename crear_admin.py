from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
import os

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client.barberia_db

# Verificar si ya existe
if db.usuarios.find_one({"email": "admin@barberia.com"}):
    print("El admin ya existe")
else:
    db.usuarios.insert_one({
        "nombre": "Administrador",
        "email": "admin@barberia.com",
        "password": generate_password_hash("admin123"),
        "rol": "admin",
        "activo": True,
    })
    print("✅ Admin creado exitosamente")
    print("Email: admin@barberia.com")
    print("Contraseña: admin123")

client.close()