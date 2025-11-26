# cuentas/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import update_session_auth_hash
from django.utils import timezone
from .models import Usuarios
from citas.models import Cita
from email.mime.text import MIMEText
import smtplib
import string
import random
import re
from django.db.models import Q
from datetime import date


# ======================================================
# Requisitos minimos para la contrasena
# ======================================================

def validar_contrasena_segura(password):
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    return True

# ======================================================
# LOGIN
# ======================================================
def user_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            usuario = Usuarios.objects.get(email=email, estado="activo")

            # Validar contraseña hasheada
            if not check_password(password, usuario.password):
                messages.error(request, "Correo o contraseña incorrectos.")
                return redirect("login")

            # Guardar sesión
            request.session["usuario_id"] = usuario.id_usuario
            request.session["usuario_email"] = usuario.email
            request.session["usuario_rol"] = usuario.id_rol.nombre_rol

            # ------------ SOLUCIÓN ----------------
            # Verificar si el usuario tiene clave temporal
            if usuario.password_temp == True:
                return redirect("cambiar_contrasena")
            # --------------------------------------

            return redirect("inicio")

        except Usuarios.DoesNotExist:
            messages.error(request, "Correo o contraseña incorrectos.")

    return render(request, "cuentas/index.html")


# ======================================================
# INICIO
# ======================================================
def inicio(request):

    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return redirect("login")
    
    from datetime import date
    hoy = date.today()

    citas_hoy = Cita.objects.filter(
        usuario_id=usuario_id,
        fecha_cita=hoy
    ).count()

    # Mostrar solo una vez por sesión
    mostrar_toast = False
    if citas_hoy > 0 and not request.session.get("toast_mostrado", False):
        mostrar_toast = True
        request.session["toast_mostrado"] = True

    return render(request, "cuentas/inicio.html", {
        "citas_hoy": citas_hoy,
        "mostrar_toast": mostrar_toast,
    })



# ======================================================
# LOGOUT
# ======================================================
def user_logout(request):
    request.session.flush()
    return redirect("login")


# ======================================================
# RECUPERAR CONTRASEÑA
# ======================================================
def recuperar_password(request):
    if request.method == "POST":
        email = request.POST.get("username")

        try:
            usuario = Usuarios.objects.get(email=email, estado="activo")

            nueva_contrasena = generar_contrasena()
            usuario.password = make_password(nueva_contrasena)
            usuario.save()

            enviar_correo_gmail(email, nueva_contrasena)

            messages.success(request, "Te hemos enviado una nueva contraseña.")
            return redirect("login")

        except Usuarios.DoesNotExist:
            messages.error(request, "El correo no existe en el sistema.")
            return redirect("recuperar")

    return render(request, "cuentas/recuperarContrasena.html")

# ======================================================
# CAMBIAR CONTRASEÑA
# ======================================================
def cambiarContrasena(request):

    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return redirect("login")

    usuario = Usuarios.objects.get(id_usuario=usuario_id)

    if request.method == "POST":

        old_pass = request.POST.get("old_password")
        nueva_pass = request.POST.get("password")
        confirmar_pass = request.POST.get("password2")

        # 1. Validar campos vacíos
        if not old_pass or not nueva_pass or not confirmar_pass:
            messages.error(request, "Debes completar todos los campos.")
            return redirect("cambiar_contrasena")

        # 2. Verificar que la contraseña temporal sea correcta
        if not check_password(old_pass, usuario.password):
            messages.error(request, "La contraseña temporal es incorrecta.")
            return redirect("cambiar_contrasena")

        # 3. Validar coincidencia
        if nueva_pass != confirmar_pass:
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect("cambiar_contrasena")

        # 4. Reglas de seguridad
        if len(nueva_pass) < 8:
            messages.error(request, "La contraseña debe tener al menos 8 caracteres.")
            return redirect("cambiar_contrasena")

        if not any(c.isdigit() for c in nueva_pass):
            messages.error(request, "La contraseña debe incluir al menos un número.")
            return redirect("cambiar_contrasena")

        if not any(c.isupper() for c in nueva_pass):
            messages.error(request, "La contraseña debe incluir al menos una mayúscula.")
            return redirect("cambiar_contrasena")

        if not any(c.islower() for c in nueva_pass):
            messages.error(request, "La contraseña debe incluir al menos una minúscula.")
            return redirect("cambiar_contrasena")

        # 5. Guardar nueva contraseña encriptada
        usuario.password = make_password(nueva_pass)
        usuario.password_temp = False
        usuario.save()

        messages.success(request, "Tu contraseña ha sido actualizada exitosamente.")
        return redirect("login")

    return render(request, "cuentas/cambiarContrasena.html")




# ======================================================
# FUNCIONES AUXILIARES
# ======================================================


# ======================================================
# GENERAR CONTRASEÑA
# ======================================================
def generar_contrasena(longitud=8):
    caracteres = string.ascii_letters + string.digits
    return "".join(random.choice(caracteres) for _ in range(longitud))

# ======================================================
# ENVIAR CORREO GMAIL
# ======================================================
def enviar_correo_gmail(destinatario, contrasena_nueva):
    remitente = "sistemasessis@gmail.com"
    password = "fpkl szho vbmk vssi"  # Contraseña de aplicación de Gmail

    asunto = "Recuperación de contraseña SESSIS"
    cuerpo = (
        f"Hola,\n\n"
        f"Tu nueva contraseña es: {contrasena_nueva}\n\n"
        f"Por motivos de seguridad, cambia tu contraseña después de iniciar sesión.\n\n"
        f"Atentamente,\nEquipo de Soporte SESSIS"
    )

    mensaje = MIMEText(cuerpo)
    mensaje["Subject"] = asunto
    mensaje["From"] = remitente
    mensaje["To"] = destinatario

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(remitente, password)
        server.send_message(mensaje)
        server.quit()
    except Exception as e:
        print("Error al enviar el correo:", e)
