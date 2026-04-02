from flask import Flask, render_template
from flask_cors import CORS
from config import Config
from utils.db import close_db
from routes import clientes_bp, barberos_bp, citas_bp, reportes_bp

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

app.register_blueprint(clientes_bp)
app.register_blueprint(reportes_bp)
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

@app.route("/reportes")
def vista_reportes():
    return render_template("reportes.html")

if __name__ == "__main__":
    print("BarberApp corriendo en http://localhost:5000")
    app.run(debug=app.config["DEBUG"], port=5000)
