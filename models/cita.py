from datetime import datetime
from bson import ObjectId

ESTADOS = ["pendiente", "confirmada", "completada", "cancelada"]

SERVICIOS_BASE = [
    {"nombre": "Corte clásico",       "precio": 20000, "duracion_min": 30},
    {"nombre": "Corte + barba",       "precio": 35000, "duracion_min": 50},
    {"nombre": "Afeitado clásico",    "precio": 18000, "duracion_min": 25},
    {"nombre": "Corte fade",          "precio": 28000, "duracion_min": 40},
    {"nombre": "Tratamiento capilar", "precio": 45000, "duracion_min": 60},
]

def nueva_cita(cliente_id, barbero_id, servicio, fecha_str, hora, notas=""):
    return {
        "cliente_id": ObjectId(cliente_id),
        "barbero_id": ObjectId(barbero_id),
        "servicio": servicio,
        "fecha": fecha_str,
        "hora": hora,
        "estado": "pendiente",
        "notas": notas.strip(),
        "creado_en": datetime.utcnow(),
    }
