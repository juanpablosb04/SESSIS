from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.forms import PasswordResetForm


# Vista de inicio (inicio.html)
def inicio(request):
    if not request.user.is_authenticated:  # 👈 si no está logueado, redirige al login
        return redirect('login')
    return render(request, 'cuentas/inicio.html')

# Vista de recuperación de contraseña (recuperarContrasena.html)
def recuperar_password(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            # 👇 Aquí podrías configurar envío de correo si quieres
            form.save(request=request)
            messages.success(request, "Si el correo existe, te hemos enviado un enlace de recuperación.")
            return redirect('login')
    else:
        form = PasswordResetForm()
    return render(request, 'cuentas/recuperarContrasena.html', {'form': form})

# Logout
def user_logout(request):
    logout(request)
    return redirect('login')

