"""
Script para poblar la base de datos con datos de prueba.
Ejecutar con: python seed.py
"""

from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/barberia_db")
client = MongoClient(MONGO_URI)
db = client.get_default_database()

# ── Limpiar colecciones existentes ──────────────────────────────────────────
db.barberos.delete_many({})
db.clientes.delete_many({})
db.citas.delete_many({})
print("✓ Colecciones limpiadas")

# ── Barberos ─────────────────────────────────────────────────────────────────
barberos = db.barberos.insert_many([
    {
        "nombre": "Carlos Mendoza",
        "especialidades": ["Corte clásico", "Corte fade"],
        "telefono": "3001234567",
        "activo": True,
        "creado_en": datetime.utcnow(),
    },
    {
        "nombre": "Andrés Ríos",
        "especialidades": ["Corte + barba", "Afeitado clásico"],
        "telefono": "3109876543",
        "activo": True,
        "creado_en": datetime.utcnow(),
    },
    {
        "nombre": "Luis Patiño",
        "especialidades": ["Tratamiento capilar", "Corte clásico"],
        "telefono": "3205554433",
        "activo": True,
        "creado_en": datetime.utcnow(),
    },
])
print(f"✓ {len(barberos.inserted_ids)} barberos insertados")

# ── Clientes ─────────────────────────────────────────────────────────────────
clientes = db.clientes.insert_many([
    {
        "nombre": "Juan García",
        "telefono": "3001112233",
        "email": "juan@email.com",
        "notas": "Prefiere corte fade bajo",
        "activo": True,
        "creado_en": datetime.utcnow(),
    },
    {
        "nombre": "Miguel Torres",
        "telefono": "3154445566",
        "email": "miguel@email.com",
        "notas": "",
        "activo": True,
        "creado_en": datetime.utcnow(),
    },
    {
        "nombre": "Sebastián López",
        "telefono": "3187778899",
        "email": "sebas@email.com",
        "notas": "Alérgico a ciertos productos capilares",
        "activo": True,
        "creado_en": datetime.utcnow(),
    },
    {
        "nombre": "David Herrera",
        "telefono": "3002223344",
        "email": "",
        "notas": "",
        "activo": True,
        "creado_en": datetime.utcnow(),
    },
])
print(f"✓ {len(clientes.inserted_ids)} clientes insertados")

# ── Citas de ejemplo ──────────────────────────────────────────────────────────
barbero_ids = barberos.inserted_ids
cliente_ids = clientes.inserted_ids

citas = db.citas.insert_many([
    {
        "cliente_id": cliente_ids[0],
        "barbero_id": barbero_ids[0],
        "servicio": "Corte fade",
        "fecha": "2026-04-01",
        "hora": "10:00",
        "estado": "pendiente",
        "notas": "",
        "creado_en": datetime.utcnow(),
    },
    {
        "cliente_id": cliente_ids[1],
        "barbero_id": barbero_ids[1],
        "servicio": "Corte + barba",
        "fecha": "2026-04-01",
        "hora": "11:00",
        "estado": "confirmada",
        "notas": "Cliente frecuente",
        "creado_en": datetime.utcnow(),
    },
    {
        "cliente_id": cliente_ids[2],
        "barbero_id": barbero_ids[2],
        "servicio": "Tratamiento capilar",
        "fecha": "2026-04-02",
        "hora": "14:00",
        "estado": "pendiente",
        "notas": "",
        "creado_en": datetime.utcnow(),
    },
])
print(f"✓ {len(citas.inserted_ids)} citas insertadas")

print("\n✅ Base de datos lista. Abre http://localhost:5000 y recarga la página.")
client.close()
