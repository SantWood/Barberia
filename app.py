import os
from flask import Flask, render_template, session, redirect, url_for
from flask_cors import CORS
from config import Config
from utils.db import close_db
from routes import clientes_bp, barberos_bp, citas_bp, auth_bp

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

app.register_blueprint(clientes_bp)
app.register_blueprint(barberos_bp)
app.register_blueprint(citas_bp)
app.register_blueprint(auth_bp)
app.teardown_appcontext(close_db)

def login_requerido(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect("/auth/login")
        return f(*args, **kwargs)
    return decorated

@app.route("/")
@login_requerido
def index():
    return render_template("index.html")

@app.route("/citas")
@login_requerido
def vista_citas():
    return render_template("citas.html")

@app.route("/clientes")
@login_requerido
def vista_clientes():
    return render_template("clientes.html")

@app.route("/barberos")
@login_requerido
def vista_barberos():
    return render_template("barberos.html")

@app.route("/usuarios")
@login_requerido
def vista_usuarios():
    if session.get("usuario_rol") != "admin":
        return redirect("/")
    return render_template("usuarios.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)