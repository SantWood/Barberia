from flask import Blueprint, request, jsonify, session, redirect, url_for
from utils import get_db, parse_id, validate_object_id
from models.usuario import nuevo_usuario, verificar_password, ROLES

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/login", methods=["GET"])
def login_page():
    from flask import render_template
    return render_template("login.html")

@auth_bp.route("/login", methods=["POST"])
def login():
    db = get_db()
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    if not email or not password:
        return jsonify({"error": "Email y contraseña son obligatorios"}), 400
    usuario = db.usuarios.find_one({"email": email, "activo": True})
    if not usuario or not verificar_password(usuario["password"], password):
        return jsonify({"error": "Credenciales incorrectas"}), 401
    session["usuario_id"] = str(usuario["_id"])
    session["usuario_nombre"] = usuario["nombre"]
    session["usuario_rol"] = usuario["rol"]
    return jsonify({
        "mensaje": "Login exitoso",
        "rol": usuario["rol"],
        "nombre": usuario["nombre"]
    }), 200

@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"mensaje": "Sesión cerrada"}), 200

@auth_bp.route("/me", methods=["GET"])
def me():
    if "usuario_id" not in session:
        return jsonify({"error": "No autenticado"}), 401
    return jsonify({
        "id": session["usuario_id"],
        "nombre": session["usuario_nombre"],
        "rol": session["usuario_rol"]
    }), 200

@auth_bp.route("/usuarios", methods=["GET"])
def listar_usuarios():
    if session.get("usuario_rol") != "admin":
        return jsonify({"error": "Sin permisos"}), 403
    db = get_db()
    usuarios = list(db.usuarios.find({"activo": True}, {"password": 0}))
    for u in usuarios:
        u["_id"] = str(u["_id"])
    return jsonify(usuarios), 200

@auth_bp.route("/usuarios", methods=["POST"])
def crear_usuario():
    if session.get("usuario_rol") != "admin":
        return jsonify({"error": "Sin permisos"}), 403
    db = get_db()
    data = request.get_json()
    nombre = data.get("nombre", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()
    rol = data.get("rol", "recepcionista")
    if not nombre or not email or not password:
        return jsonify({"error": "Nombre, email y contraseña son obligatorios"}), 400
    if rol not in ROLES:
        return jsonify({"error": f"Rol inválido. Opciones: {ROLES}"}), 400
    if db.usuarios.find_one({"email": email}):
        return jsonify({"error": "Ya existe un usuario con ese email"}), 409
    doc = nuevo_usuario(nombre, email, password, rol)
    result = db.usuarios.insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    doc.pop("password")
    return jsonify(doc), 201

@auth_bp.route("/usuarios/<id>", methods=["DELETE"])
def eliminar_usuario(id):
    if session.get("usuario_rol") != "admin":
        return jsonify({"error": "Sin permisos"}), 403
    db = get_db()
    oid = validate_object_id(id)
    if not oid:
        return jsonify({"error": "ID inválido"}), 400
    db.usuarios.update_one({"_id": oid}, {"$set": {"activo": False}})
    return jsonify({"mensaje": "Usuario desactivado"}), 200