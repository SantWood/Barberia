from flask import Blueprint, request, jsonify
from utils import get_db, parse_id, parse_ids, validate_object_id
from models import nuevo_cliente, actualizar_cliente

clientes_bp = Blueprint("clientes", __name__, url_prefix="/api/clientes")

@clientes_bp.route("/", methods=["GET"])
def listar_clientes():
    db = get_db()
    query = {"activo": True}
    busqueda = request.args.get("q", "").strip()
    if busqueda:
        query["$or"] = [
            {"nombre": {"$regex": busqueda, "$options": "i"}},
            {"telefono": {"$regex": busqueda}},
        ]
    clientes = list(db.clientes.find(query).sort("nombre", 1))
    return jsonify(parse_ids(clientes)), 200

@clientes_bp.route("/", methods=["POST"])
def crear_cliente():
    db = get_db()
    data = request.get_json()
    nombre = data.get("nombre", "").strip()
    telefono = data.get("telefono", "").strip()
    if not nombre or not telefono:
        return jsonify({"error": "Nombre y teléfono son obligatorios"}), 400
    if db.clientes.find_one({"telefono": telefono, "activo": True}):
        return jsonify({"error": "Ya existe un cliente con ese teléfono"}), 409
    doc = nuevo_cliente(nombre, telefono, data.get("email", ""), data.get("notas", ""))
    result = db.clientes.insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    return jsonify(doc), 201

@clientes_bp.route("/<id>", methods=["PUT"])
def actualizar(id):
    db = get_db()
    oid = validate_object_id(id)
    if not oid:
        return jsonify({"error": "ID inválido"}), 400
    data = request.get_json()
    nombre = data.get("nombre", "").strip()
    telefono = data.get("telefono", "").strip()
    if not nombre or not telefono:
        return jsonify({"error": "Nombre y teléfono son obligatorios"}), 400
    campos = actualizar_cliente(nombre, telefono, data.get("email", ""), data.get("notas", ""))
    result = db.clientes.update_one({"_id": oid}, {"$set": campos})
    if result.matched_count == 0:
        return jsonify({"error": "Cliente no encontrado"}), 404
    return jsonify({"mensaje": "Cliente actualizado"}), 200

@clientes_bp.route("/<id>", methods=["DELETE"])
def eliminar_cliente(id):
    db = get_db()
    oid = validate_object_id(id)
    if not oid:
        return jsonify({"error": "ID inválido"}), 400
    result = db.clientes.update_one({"_id": oid}, {"$set": {"activo": False}})
    if result.matched_count == 0:
        return jsonify({"error": "Cliente no encontrado"}), 404
    return jsonify({"mensaje": "Cliente eliminado"}), 200
