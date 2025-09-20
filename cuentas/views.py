from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.forms import PasswordResetForm
from .models import Usuarios
import smtplib
import string
import random
from email.mime.text import MIMEText

# Vista de login
def user_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            usuario = Usuarios.objects.get(email=email, password=password, estado="activo")
            # Guardar sesión manualmente
            request.session["usuario_id"] = usuario.id_usuario
            request.session["usuario_email"] = usuario.email
            request.session["usuario_rol"] = usuario.id_rol_id
            messages.success(request, f"Bienvenido {usuario.email}")
            return redirect("inicio")
        except Usuarios.DoesNotExist:
            messages.error(request, "Correo o contraseña incorrectos")

    return render(request, "cuentas/index.html")


def inicio(request):
    if not request.session.get("usuario_id"): 
        return redirect("login")
    return render(request, "cuentas/inicio.html")

def user_logout(request):
    request.session.flush()  # borra toda la sesión
    return redirect("login")


def recuperar_password(request):
    if request.method == "POST":
        email = request.POST.get("username")
        try:
            usuario = Usuarios.objects.get(email=email, estado="activo")
            nueva_contrasena = generar_contrasena()
            usuario.password = nueva_contrasena
            usuario.save()

            enviar_correo_gmail(email, nueva_contrasena)

            messages.success(request, "Si el correo existe, te hemos enviado una nueva contraseña.")
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

    # Conexión segura a Gmail
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(remitente, password)
    server.send_message(mensaje)
    server.quit()

