from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Usuarios
from citas.models import Cita
from datetime import date
import smtplib
import string
import random
from email.mime.text import MIMEText

# ==========================
# LOGIN
# ==========================
def user_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            usuario = Usuarios.objects.get(email=email, password=password, estado="activo")
            # Guardar sesión manualmente
            request.session["usuario_id"] = usuario.id_usuario
            request.session["usuario_email"] = usuario.email
            request.session["usuario_rol"] = usuario.id_rol.nombre_rol
            # Redirige a inicio
            return redirect("inicio")
        except Usuarios.DoesNotExist:
            messages.error(request, "Correo o contraseña incorrectos")

    return render(request, "cuentas/index.html")


# ==========================
# INICIO
# ==========================
def inicio(request):
    if not request.session.get("usuario_id"):
        return redirect("login")

    # Construir notificación de citas
    notificacion = {
        "estado": "ok",
        "cantidad": 0,
        "mensaje": None,
    }

    try:
        rol = request.session.get("usuario_rol")

        if rol == "Administrador":
            citas_hoy = Cita.objects.filter(fecha_cita=date.today())
        else:
            citas_hoy = Cita.objects.none()

        cantidad = citas_hoy.count()
        notificacion['cantidad'] = cantidad

        if cantidad == 0:
            notificacion['estado'] = 'sin_citas'
            notificacion['mensaje'] = "No tienes citas programadas para hoy."
        else:
            notificacion['estado'] = 'ok'
            notificacion['mensaje'] = f"Tienes {cantidad} cita{'s' if cantidad>1 else ''} programada{'s' if cantidad>1 else ''} para hoy."

    except Exception as e:
        notificacion['estado'] = 'error'
        notificacion['mensaje'] = "No fue posible cargar las citas."

    return render(request, "cuentas/inicio.html", {"notificacion_citas": notificacion})


# ==========================
# LOGOUT
# ==========================
def user_logout(request):
    request.session.flush()
    return redirect("login")


# ==========================
# RECUPERAR CONTRASEÑA
# ==========================
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
            return redirect('login')
        except Usuarios.DoesNotExist:
            messages.error(request, "El correo no existe en el sistema.")
            return redirect('recuperar')
    
    return render(request, 'cuentas/recuperarContrasena.html')


def generar_contrasena(longitud=8):
    caracteres = string.ascii_letters + string.digits
    return ''.join(random.choice(caracteres) for _ in range(longitud))


def enviar_correo_gmail(destinatario, contrasena_nueva):
    remitente = "sistemasessis@gmail.com"
    password = "fpkl szho vbmk vssi"
    
    asunto = "Recuperación de contraseña SESSIS"
    cuerpo = f"Hola,\n\nTu nueva contraseña es: {contrasena_nueva}\n\nCambia tu contraseña después de iniciar sesión."

    mensaje = MIMEText(cuerpo)
    mensaje['Subject'] = asunto
    mensaje['From'] = remitente
    mensaje['To'] = destinatario

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(remitente, password)
    server.send_message(mensaje)
    server.quit()
