from flask import Blueprint, request, jsonify
from bson import ObjectId
from utils import get_db, parse_ids, validate_object_id, now_colombia
from models import nueva_cita, ESTADOS, SERVICIOS_BASE

citas_bp = Blueprint("citas", __name__, url_prefix="/api/citas")

@citas_bp.route("/servicios", methods=["GET"])
def listar_servicios():
    return jsonify(SERVICIOS_BASE), 200

@citas_bp.route("/", methods=["GET"])
def listar_citas():
    db = get_db()
    query = {}
    fecha = request.args.get("fecha")
    barbero_id = request.args.get("barbero_id")
    estado = request.args.get("estado")
    if fecha:
        query["fecha"] = fecha
    if barbero_id:
        oid = validate_object_id(barbero_id)
        if oid:
            query["barbero_id"] = oid
    if estado and estado in ESTADOS:
        query["estado"] = estado
    pipeline = [
        {"$match": query},
        {"$lookup": {"from": "clientes", "localField": "cliente_id", "foreignField": "_id", "as": "cliente"}},
        {"$lookup": {"from": "barberos",  "localField": "barbero_id", "foreignField": "_id", "as": "barbero"}},
        {"$unwind": {"path": "$cliente", "preserveNullAndEmptyArrays": True}},
        {"$unwind": {"path": "$barbero",  "preserveNullAndEmptyArrays": True}},
        {"$sort": {"fecha": 1, "hora": 1}},
    ]
    citas = list(db.citas.aggregate(pipeline))
    for c in citas:
        c["_id"]        = str(c["_id"])
        c["cliente_id"] = str(c["cliente_id"])
        c["barbero_id"] = str(c["barbero_id"])
        if c.get("cliente"):
            c["cliente"]["_id"] = str(c["cliente"]["_id"])
        if c.get("barbero"):
            c["barbero"]["_id"] = str(c["barbero"]["_id"])
    return jsonify(citas), 200

@citas_bp.route("/", methods=["POST"])
def crear_cita():
    db = get_db()
    data = request.get_json()
    cliente_id = data.get("cliente_id", "")
    barbero_id = data.get("barbero_id", "")
    fecha      = data.get("fecha", "")
    hora       = data.get("hora", "")
    servicio   = data.get("servicio")
    if not all([cliente_id, barbero_id, fecha, hora, servicio]):
        return jsonify({"error": "Faltan campos obligatorios"}), 400
    if not validate_object_id(cliente_id) or not validate_object_id(barbero_id):
        return jsonify({"error": "IDs inválidos"}), 400
    conflicto = db.citas.find_one({
        "barbero_id": ObjectId(barbero_id),
        "fecha": fecha, "hora": hora,
        "estado": {"$nin": ["cancelada"]},
    })
    if conflicto:
        return jsonify({"error": "El barbero ya tiene una cita en ese horario"}), 409
    doc = nueva_cita(cliente_id, barbero_id, servicio, fecha, hora, data.get("notas", ""))
    result = db.citas.insert_one(doc)
    doc["_id"]        = str(result.inserted_id)
    doc["cliente_id"] = str(doc["cliente_id"])
    doc["barbero_id"] = str(doc["barbero_id"])
    return jsonify(doc), 201

@citas_bp.route("/<id>/estado", methods=["PATCH"])
def cambiar_estado(id):
    db = get_db()
    oid = validate_object_id(id)
    if not oid:
        return jsonify({"error": "ID inválido"}), 400
    nuevo_estado = request.get_json().get("estado")
    if nuevo_estado not in ESTADOS:
        return jsonify({"error": f"Estado inválido. Opciones: {ESTADOS}"}), 400
    db.citas.update_one({"_id": oid}, {"$set": {"estado": nuevo_estado, "actualizado_en": now_colombia()}})
    return jsonify({"mensaje": f"Cita marcada como {nuevo_estado}"}), 200

@citas_bp.route("/<id>", methods=["DELETE"])
def cancelar_cita(id):
    db = get_db()
    oid = validate_object_id(id)
    if not oid:
        return jsonify({"error": "ID inválido"}), 400
    result = db.citas.update_one({"_id": oid}, {"$set": {"estado": "cancelada", "actualizado_en": now_colombia()}})
    if result.matched_count == 0:
        return jsonify({"error": "Cita no encontrada"}), 404
    return jsonify({"mensaje": "Cita cancelada"}), 200
