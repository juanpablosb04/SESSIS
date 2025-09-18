from flask import Blueprint, render_template, request, redirect, url_for, session
from db import get_connection

login_bp = Blueprint("login", __name__)

@login_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("username")
        contrasena = request.form.get("password")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM Usuarios WHERE email=? AND password=?", (email, contrasena)
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            # Guardar información del usuario en sesión
            session["user_id"] = row[0]  # por ejemplo, el ID del usuario
            return redirect(url_for("inicio"))
        else:
            return "❌ Usuario o contraseña incorrectos"

    return render_template("index.html")

@login_bp.route("/logout")
def logout():
    session.clear()  # elimina todo lo de la sesión
    return redirect(url_for("home"))  # redirige al login


    
