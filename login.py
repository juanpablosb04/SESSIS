from flask import Blueprint, render_template, request, redirect, url_for
from db import get_connection

login_bp = Blueprint("login", __name__)

@login_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        email = request.form.get("username")   # viene del input name="username"
        contrasena = request.form.get("password")  # viene del input name="password"

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM Usuarios WHERE email=? AND password=?", (email, contrasena)
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            return redirect(url_for("inicio"))
        else:
            return "❌ Usuario o contraseña incorrectos"

    # Si GET → muestra login
    return render_template("index.html")
