from datetime import datetime

def nuevo_barbero(nombre, especialidades=None, telefono=""):
    return {
        "nombre": nombre.strip(),
        "especialidades": especialidades or ["Corte clásico"],
        "telefono": telefono.strip(),
        "activo": True,
        "creado_en": datetime.utcnow(),
    }
