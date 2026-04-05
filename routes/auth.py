from flask import Blueprint, request, jsonify, session
from utils import get_db, validate_object_id
from models.usuario import nuevo_usuario, verificar_password, ROLES

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/login", methods=["GET"])
def login_page():
    return """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>BarberApp - Login</title>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;700&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet"/>
  <style>
    *{box-sizing:border-box;margin:0;padding:0}
    body{font-family:'DM Sans',sans-serif;background:#0f0e0d;color:#e8e3d8;min-height:100vh;display:flex;align-items:center;justify-content:center;}
    .box{background:#1a1815;border:1px solid #2e2b25;border-radius:12px;padding:40px;width:100%;max-width:400px;}
    .brand{font-family:'Playfair Display',serif;font-size:28px;color:#c9a84c;text-align:center;margin-bottom:8px;}
    .subtitle{text-align:center;color:#8a8274;font-size:14px;margin-bottom:32px;}
    .form-group{margin-bottom:16px;}
    .form-group label{display:block;font-size:13px;color:#8a8274;margin-bottom:5px;}
    .form-control{width:100%;background:#242118;border:1px solid #2e2b25;border-radius:8px;padding:10px 13px;color:#e8e3d8;font-size:14px;outline:none;font-family:inherit;}
    .form-control:focus{border-color:#7a6128;}
    .btn{width:100%;padding:11px;background:#c9a84c;color:#0f0e0d;border:none;border-radius:8px;font-size:15px;font-weight:500;cursor:pointer;margin-top:8px;font-family:inherit;}
    .btn:hover{background:#dbb95e;}
    .error{background:#2c0f0e;color:#e07070;border:1px solid #5a1a1a;border-radius:8px;padding:10px;font-size:13px;margin-bottom:16px;display:none;}
  </style>
</head>
<body>
<div class="box">
  <div class="brand">✦ BarberApp</div>
  <div class="subtitle">Inicia sesion para continuar</div>
  <div class="error" id="error-msg"></div>
  <div class="form-group">
    <label>Email</label>
    <input type="email" id="email" class="form-control" placeholder="correo@ejemplo.com"/>
  </div>
  <div class="form-group">
    <label>Contrasena</label>
    <input type="password" id="password" class="form-control" placeholder="Tu contrasena"/>
  </div>
  <button class="btn" onclick="login()">Ingresar</button>
</div>
<script>
async function login() {
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;
  const errorEl = document.getElementById("error-msg");
  errorEl.style.display = "none";
  if (!email || !password) {
    errorEl.textContent = "Completa todos los campos";
    errorEl.style.display = "block";
    return;
  }
  const res = await fetch("/auth/login", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({email, password})
  });
  const data = await res.json();
  if (!res.ok) {
    errorEl.textContent = data.error;
    errorEl.style.display = "block";
    return;
  }
  window.location.href = "/";
}
document.addEventListener("keydown", e => { if(e.key==="Enter") login(); });
</script>
</body>
</html>"""

@auth_bp.route("/login", methods=["POST"])
def login():
    db = get_db()
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    if not email or not password:
        return jsonify({"error": "Email y contrasena son obligatorios"}), 400
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
    return jsonify({"mensaje": "Sesion cerrada"}), 200

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
        return jsonify({"error": "Nombre, email y contrasena son obligatorios"}), 400
    if rol not in ROLES:
        return jsonify({"error": f"Rol invalido. Opciones: {ROLES}"}), 400
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
        return jsonify({"error": "ID invalido"}), 400
    db.usuarios.update_one({"_id": oid}, {"$set": {"activo": False}})
    return jsonify({"mensaje": "Usuario desactivado"}), 200