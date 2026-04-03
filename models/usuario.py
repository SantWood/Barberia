from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

ROLES = ["admin", "barbero", "recepcionista"]

def nuevo_usuario(nombre, email, password, rol="recepcionista"):
    return {
        "nombre": nombre.strip(),
        "email": email.strip().lower(),
        "password": generate_password_hash(password),
        "rol": rol,
        "activo": True,
        "creado_en": datetime.utcnow(),
    }

def verificar_password(hash_guardado, password_ingresado):
    return check_password_hash(hash_guardado, password_ingresado)