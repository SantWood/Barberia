from flask import Blueprint, jsonify, request
from utils import get_db, parse_ids, validate_object_id
from models import nuevo_barbero

barberos_bp = Blueprint("barberos", __name__, url_prefix="/api/barberos")

@barberos_bp.route("/", methods=["GET"])
def listar_barberos():
    db = get_db()
    barberos = list(db.barberos.find({"activo": True}).sort("nombre", 1))
    return jsonify(parse_ids(barberos)), 200

@barberos_bp.route("/", methods=["POST"])
def crear_barbero():
    db = get_db()
    data = request.get_json()
    nombre = data.get("nombre", "").strip()
    if not nombre:
        return jsonify({"error": "El nombre es obligatorio"}), 400
    doc = nuevo_barbero(nombre, data.get("especialidades", []), data.get("telefono", ""))
    result = db.barberos.insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    return jsonify(doc), 201

@barberos_bp.route("/<id>", methods=["DELETE"])
def eliminar_barbero(id):
    db = get_db()
    oid = validate_object_id(id)
    if not oid:
        return jsonify({"error": "ID inválido"}), 400
    db.barberos.update_one({"_id": oid}, {"$set": {"activo": False}})
    return jsonify({"mensaje": "Barbero desactivado"}), 200
