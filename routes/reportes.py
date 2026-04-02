from flask import Blueprint, jsonify
from utils import get_db

reportes_bp = Blueprint("reportes", __name__, url_prefix="/api/reportes")

@reportes_bp.route("/resumen")
def resumen():
    db = get_db()

    # Citas por estado
    por_estado = list(db.citas.aggregate([
        {"$group": {"_id": "$estado", "total": {"$sum": 1}}}
    ]))

    # Citas por servicio
    por_servicio = list(db.citas.aggregate([
        {"$group": {"_id": "$servicio", "total": {"$sum": 1}}},
        {"$sort": {"total": -1}},
        {"$limit": 6}
    ]))

    # Citas por barbero
    por_barbero = list(db.citas.aggregate([
        {"$lookup": {"from": "barberos", "localField": "barbero_id", "foreignField": "_id", "as": "barbero"}},
        {"$unwind": {"path": "$barbero", "preserveNullAndEmptyArrays": True}},
        {"$group": {"_id": "$barbero.nombre", "total": {"$sum": 1}}},
        {"$sort": {"total": -1}}
    ]))

    # Citas por día (últimos 14 días)
    por_dia = list(db.citas.aggregate([
        {"$group": {"_id": "$fecha", "total": {"$sum": 1}}},
        {"$sort": {"_id": 1}},
        {"$limit": 14}
    ]))

    # Ingresos por servicio (usando precio del servicio)
    PRECIOS = {
        "Corte clásico": 20000,
        "Corte + barba": 35000,
        "Afeitado clásico": 18000,
        "Corte fade": 28000,
        "Tratamiento capilar": 45000,
    }
    ingresos_data = []
    for s in por_servicio:
        nombre = s["_id"] if isinstance(s["_id"], str) else (s["_id"].get("nombre") if s["_id"] else "Desconocido")
        precio = PRECIOS.get(nombre, 0)
        ingresos_data.append({"servicio": nombre, "total": s["total"], "ingresos": s["total"] * precio})

    # Totales
    total_citas    = db.citas.count_documents({})
    total_clientes = db.clientes.count_documents({"activo": True})
    total_barberos = db.barberos.count_documents({"activo": True})
    total_ingresos = sum(i["ingresos"] for i in ingresos_data)

    def clean(lst, key="_id"):
        return [{"label": (str(d[key]) if d[key] else "Sin nombre"), "total": d["total"]} for d in lst]

    return jsonify({
        "totales": {
            "citas": total_citas,
            "clientes": total_clientes,
            "barberos": total_barberos,
            "ingresos": total_ingresos,
        },
        "por_estado":   clean(por_estado),
        "por_servicio": [{"label": d["servicio"], "total": d["total"], "ingresos": d["ingresos"]} for d in ingresos_data],
        "por_barbero":  clean(por_barbero),
        "por_dia":      clean(por_dia),
    }), 200
