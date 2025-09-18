from flask import Flask, render_template
from login import login_bp 

app = Flask(__name__)

# Registrar el blueprint del login
app.register_blueprint(login_bp)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/inicio")
def inicio():
    return render_template("inicio.html")

if __name__ == "__main__":
    app.run(debug=True)
