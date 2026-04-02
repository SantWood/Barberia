import os
from flask import Flask, render_template
from flask_cors import CORS
from config import Config
from utils.db import close_db
from routes import clientes_bp, barberos_bp, citas_bp

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

app.register_blueprint(clientes_bp)
app.register_blueprint(barberos_bp)
app.register_blueprint(citas_bp)
app.teardown_appcontext(close_db)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/citas")
def vista_citas():
    return render_template("citas.html")

@app.route("/clientes")
def vista_clientes():
    return render_template("clientes.html")

@app.route("/barberos")
def vista_barberos():
    return render_template("barberos.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)