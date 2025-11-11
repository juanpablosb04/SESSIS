# cuentas/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .models import Usuarios
from citas.models import Cita
from email.mime.text import MIMEText
import smtplib
import string
import random
from django.db.models import Q
from datetime import date


# ======================================================
# LOGIN
# ======================================================
def user_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            usuario = Usuarios.objects.get(email=email, password=password, estado="activo")

            # Guardar sesión
            request.session["usuario_id"] = usuario.id_usuario
            request.session["usuario_email"] = usuario.email
            request.session["usuario_rol"] = usuario.id_rol.nombre_rol

            return redirect("inicio")

        except Usuarios.DoesNotExist:
            messages.error(request, "Correo o contraseña incorrectos.")

    return render(request, "cuentas/index.html")


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
            usuario.password = nueva_contrasena
            usuario.save()

            enviar_correo_gmail(email, nueva_contrasena)

            messages.success(request, "Te hemos enviado una nueva contraseña.")
            return redirect("login")

        except Usuarios.DoesNotExist:
            messages.error(request, "El correo no existe en el sistema.")
            return redirect("recuperar")

    return render(request, "cuentas/recuperarContrasena.html")


# ======================================================
# FUNCIONES AUXILIARES
# ======================================================
def generar_contrasena(longitud=8):
    caracteres = string.ascii_letters + string.digits
    return "".join(random.choice(caracteres) for _ in range(longitud))


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
