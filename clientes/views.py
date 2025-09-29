from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Clientes, ClientesAuditoria
from config.decorators import role_required
import re


# -------------------------------
# LISTA, CREAR, EDITAR Y ELIMINAR CLIENTES
# -------------------------------
@role_required(["Administrador"])
def clientes_view(request):
    # 👇 Validación de sesión manual (si no hay usuario -> login)
    if not request.session.get("usuario_id"):
        return redirect("login")

    clientes = Clientes.objects.all()

    if request.method == 'POST':
        action = request.POST.get('action')

        # -------------------------------
        # CREAR CLIENTE
        # -------------------------------
        if action == 'crear':
            nombre = request.POST.get('nombre')
            email = request.POST.get('email')
            cedula = request.POST.get('cedula')
            telefono = request.POST.get('telefono')
            residencia = request.POST.get('residencia')

            # Validaciones
            if not nombre or not email or not cedula:
                messages.error(request, "⚠️ Nombre, email y cédula son obligatorios")
            elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                messages.error(request, "⚠️ El correo no tiene un formato válido")
            elif Clientes.objects.filter(email=email).exists():
                messages.error(request, "⚠️ El correo ya está registrado")
            elif Clientes.objects.filter(cedula=cedula).exists():
                messages.error(request, "⚠️ La cédula ya está registrada")
            else:
                Clientes.objects.create(
                    nombre_completo=nombre,
                    email=email,
                    cedula=cedula,
                    telefono=telefono,
                    residencia=residencia
                )
                messages.success(request, "✅ Cliente creado correctamente")

        # -------------------------------
        # EDITAR CLIENTE
        # -------------------------------
        elif action == 'editar':
            cliente_id = request.POST.get('cliente_id')
            cliente = get_object_or_404(Clientes, id_cliente=cliente_id)

            nuevo_email = request.POST.get('email')
            nueva_cedula = request.POST.get('cedula')

            if Clientes.objects.filter(email=nuevo_email).exclude(id_cliente=cliente.id_cliente).exists():
                messages.error(request, "⚠️ Ese correo ya está en uso")
            elif Clientes.objects.filter(cedula=nueva_cedula).exclude(id_cliente=cliente.id_cliente).exists():
                messages.error(request, "⚠️ Esa cédula ya está en uso")
            else:
                cliente.nombre_completo = request.POST.get('nombre')
                cliente.email = nuevo_email
                cliente.cedula = nueva_cedula
                cliente.telefono = request.POST.get('telefono')
                cliente.residencia = request.POST.get('residencia')
                cliente.save()
                messages.success(request, "✏️ Cliente editado correctamente")

        # -------------------------------
        # ELIMINAR CLIENTE
        # -------------------------------
        elif action == 'eliminar':
            cliente_id = request.POST.get('cliente_id')
            cliente = get_object_or_404(Clientes, id_cliente=cliente_id)
            cliente.delete()
            messages.success(request, "🗑️ Cliente eliminado correctamente")

        # 👇 Siempre redirige a la lista de clientes
        return redirect('clientes')

    # 👇 Render al template que movimos a templates/clientes/
    return render(request, 'clientes/clientes.html', {'clientes': clientes})


# -------------------------------
# VISTA DE AUDITORÍA DE CLIENTES
# -------------------------------
@role_required(["Administrador"])
def auditoria_cliente(request, cliente_id):
    # 👇 Validación de sesión manual
    if not request.session.get("usuario_id"):
        return redirect("login")

    cliente = get_object_or_404(Clientes, id_cliente=cliente_id)
    auditoria = ClientesAuditoria.objects.filter(cliente=cliente).order_by('-fecha')

    # 👇 Render al template que debe estar en templates/clientes/
    return render(request, 'clientes/auditoria_cliente.html', {
        'cliente': cliente,
        'auditoria': auditoria
    })








