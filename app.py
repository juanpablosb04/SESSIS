from flask import Flask, render_template
from login import login_bp 

app = Flask(__name__)

# Clave secreta para manejar sesiones
app.secret_key = "Momentanea"

# Registrar el blueprint del login
app.register_blueprint(login_bp)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/inicio")
def inicio():
    return render_template("inicio.html")

@app.route("/empleados")
def empleados():
    return render_template("Administrador/empleados.html")

@app.route("/horasExtras")
def horas_extras():
    return render_template("Administrador/horasExtras.html")

@app.route("/asistencia")
def asistencia():
    return render_template("Administrador/asistencia.html")

@app.route("/clientes")
def clientes():
    return render_template("Administrador/clientes.html")

@app.route("/registrarCitas")
def registrar_citas():
    return render_template("Administrador/registrarCitas.html")

@app.route("/consultarCitas")
def consultar_citas():
    return render_template("Administrador/consultarCitas.html")

@app.route("/inventario")
def inventario():
    return render_template("Administrador/inventario.html")

@app.route("/reportes")
def reportes():
    return render_template("Administrador/reportesGenerales.html")

@app.route("/usuarios")
def usuarios():
    return render_template("Administrador/usuarios.html")
    

if __name__ == "__main__":
    app.run(debug=True)
