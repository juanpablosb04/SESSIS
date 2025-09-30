from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Empleado
from config.decorators import role_required
import re

@role_required(["Administrador"])
def empleados_view(request):
    empleados = Empleado.objects.all()

    if request.method == 'POST':
        action = request.POST.get('action')

        # -------------------------------

        if action == 'crear':
            nombre = request.POST.get('nombre_completo')
            email = request.POST.get('email')
            cedula = request.POST.get('cedula')
            telefono = request.POST.get('telefono')
            direccion = request.POST.get('direccion')
            fecha = request.POST.get('fecha_contratacion')

            if not nombre or not email or not cedula or not fecha:
                messages.error(request, "⚠️ Nombre, correo, cédula y fecha son obligatorios")
            elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                messages.error(request, "⚠️ El correo no tiene un formato válido")
            elif Empleado.objects.filter(email=email).exists():
                messages.error(request, "⚠️ El correo ya está registrado")
            elif Empleado.objects.filter(cedula=cedula).exists():
                messages.error(request, "⚠️ La cédula ya está registrada")
            else:
                Empleado.objects.create(
                    nombre_completo=nombre,
                    email=email,
                    cedula=cedula,
                    telefono=telefono,
                    direccion=direccion,
                    fecha_contratacion=fecha
                )
                messages.success(request, "✅ Empleado creado correctamente")

        # -------------------------------

        elif action == 'editar':
            empleado_id = request.POST.get('empleado_id')
            empleado = get_object_or_404(Empleado, id_empleado=empleado_id)

            nuevo_email = request.POST.get('email')
            nueva_cedula = request.POST.get('cedula')

            if Empleado.objects.filter(email=nuevo_email).exclude(id_empleado=empleado.id_empleado).exists():
                messages.error(request, "⚠️ Ese correo ya está en uso")
            elif Empleado.objects.filter(cedula=nueva_cedula).exclude(id_empleado=empleado.id_empleado).exists():
                messages.error(request, "⚠️ Esa cédula ya está en uso")
            else:
                empleado.nombre_completo = request.POST.get('nombre_completo')
                empleado.email = nuevo_email
                empleado.cedula = nueva_cedula
                empleado.telefono = request.POST.get('telefono')
                empleado.direccion = request.POST.get('direccion')
                empleado.fecha_contratacion = request.POST.get('fecha_contratacion')
                empleado.save()
                messages.success(request, "✏️ Empleado editado correctamente")

        # -------------------------------
        elif action == 'eliminar':
            empleado_id = request.POST.get('empleado_id')
            empleado = get_object_or_404(Empleado, id_empleado=empleado_id)
            empleado.delete()
            messages.success(request, "🗑️ Empleado eliminado correctamente")

        return redirect('empleados')

    return render(request, 'empleados/empleados.html', {'empleados': empleados})