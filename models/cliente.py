from datetime import datetime

def nuevo_cliente(nombre, telefono, email="", notas=""):
    return {
        "nombre": nombre.strip(),
        "telefono": telefono.strip(),
        "email": email.strip(),
        "notas": notas.strip(),
        "activo": True,
        "creado_en": datetime.utcnow(),
    }

def actualizar_cliente(nombre, telefono, email="", notas=""):
    return {
        "nombre": nombre.strip(),
        "telefono": telefono.strip(),
        "email": email.strip(),
        "notas": notas.strip(),
        "actualizado_en": datetime.utcnow(),
    }
