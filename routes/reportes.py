from flask import Blueprint, jsonify, render_template
from utils.db import get_db

reportes_bp = Blueprint("reportes", __name__)

@reportes_bp.route("/reportes")
def ver_reportes():
    return render_template("reportes.html")

@reportes_bp.route("/api/reportes/resumen")
def resumen():
    db = get_db()

    # Citas por estado
    por_estado = list(db.citas.aggregate([
        {"$group": {"_id": "$estado", "total": {"$sum": 1}}}
    ]))

    # Citas por servicio con ingresos
    por_servicio_ingresos = list(db.citas.aggregate([
        {"$group": {
            "_id": "$servicio",
            "total": {"$sum": 1},
            "ingresos": {"$sum": "$precio"}
        }},
        {"$sort": {"total": -1}},
        {"$limit": 6}
    ]))

    # Citas por barbero — usa nombre directo
    por_barbero = list(db.citas.aggregate([
        {"$group": {"_id": "$barbero", "total": {"$sum": 1}}},
        {"$sort": {"total": -1}}
    ]))

    # Citas por día (últimos 14 días)
    por_dia = list(db.citas.aggregate([
        {"$group": {"_id": "$fecha", "total": {"$sum": 1}}},
        {"$sort": {"_id": 1}},
        {"$limit": 14}
    ]))

    # Totales
    total_citas    = db.citas.count_documents({})
    total_clientes = db.clientes.count_documents({})
    total_barberos = db.barberos.count_documents({"activo": True})

    ingresos_result = list(db.citas.aggregate([
        {"$match": {"estado": "completada"}},
        {"$group": {"_id": None, "total": {"$sum": "$precio"}}}
    ]))
    total_ingresos = ingresos_result[0]["total"] if ingresos_result else 0

    def clean(lst):
        return [
            {
                "label": str(d["_id"]) if d["_id"] else "Sin nombre",
                "total": d["total"]
            }
            for d in lst
        ]

    def clean_servicios(lst):
        return [
            {
                "label": str(d["_id"]) if d["_id"] else "Sin nombre",
                "total": d["total"],
                "ingresos": d.get("ingresos", 0)
            }
            for d in lst
        ]

    return jsonify({
        "totales": {
            "citas":    total_citas,
            "clientes": total_clientes,
            "barberos": total_barberos,
            "ingresos": total_ingresos,
        },
        "por_estado":   clean(por_estado),
        "por_servicio": clean_servicios(por_servicio_ingresos),
        "por_barbero":  clean(por_barbero),
        "por_dia":      clean(por_dia),
    }), 200