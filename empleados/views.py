# empleados/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Empleado, EmpleadosAuditoria
from config.decorators import role_required
import re


@role_required(["Administrador"])
def empleados_view(request):
    empleados = Empleado.objects.all().order_by("nombre_completo")

    if request.method == "POST":
        action = request.POST.get("action")

        # ---------------- CREAR ----------------
        if action == "crear":
            nombre = request.POST.get("nombre_completo", "").strip()
            email = request.POST.get("email", "").strip()
            cedula = request.POST.get("cedula", "").strip()
            telefono = request.POST.get("telefono", "").strip()
            direccion = request.POST.get("direccion", "").strip()
            fecha = request.POST.get("fecha_contratacion", "").strip()  # 'YYYY-MM-DD'

            if not nombre or not email or not cedula or not fecha:

                messages.error(request, "⚠️ Nombre, correo, cédula y fecha son obligatorios.")
            elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                messages.error(request, "⚠️ El correo no tiene un formato válido.", extra_tags='crear')
            elif Empleado.objects.filter(email=email).exists():
                messages.error(request, "⚠️ El correo ya está registrado.", extra_tags='crear')
            elif Empleado.objects.filter(cedula=cedula).exists():
                messages.error(request, "⚠️ La cédula ya está registrada.", extra_tags='crear')


            else:
                empleado = Empleado(
                    nombre_completo=nombre,
                    email=email,
                    cedula=cedula,
                    telefono=telefono or None,
                    direccion=direccion or None,
                    fecha_contratacion=fecha,
                )

                empleado._usuario_email = request.session.get("usuario_email")  # 👈 para signals
                empleado.save()
                messages.success(request, "✅ Empleado creado correctamente.", extra_tags='crear')


        # ---------------- EDITAR ----------------
        elif action == "editar":
            empleado_id = request.POST.get("empleado_id")
            empleado = get_object_or_404(Empleado, id_empleado=empleado_id)

            nuevo_nombre = request.POST.get("nombre_completo", "").strip()
            nuevo_email = request.POST.get("email", "").strip()
            nueva_cedula = request.POST.get("cedula", "").strip()
            nuevo_telefono = request.POST.get("telefono", "").strip()
            nueva_direccion = request.POST.get("direccion", "").strip()
            nueva_fecha = request.POST.get("fecha_contratacion", "").strip()


            if not nuevo_nombre or not nuevo_email or not nueva_cedula or not nueva_fecha:
                messages.error(request, "⚠️ Nombre, correo, cédula y fecha son obligatorios.", extra_tags='editar')
            elif not re.match(r"[^@]+@[^@]+\.[^@]+", nuevo_email):
                messages.error(request, "⚠️ El correo no tiene un formato válido.", extra_tags='editar')
            elif Empleado.objects.filter(email=nuevo_email).exclude(id_empleado=empleado.id_empleado).exists():
                messages.error(request, "⚠️ Ese correo ya está en uso.", extra_tags='editar')
            elif Empleado.objects.filter(cedula=nueva_cedula).exclude(id_empleado=empleado.id_empleado).exists():
                messages.error(request, "⚠️ Esa cédula ya está en uso.", extra_tags='editar')
            else:
                empleado.nombre_completo = nuevo_nombre
                empleado.email = nuevo_email
                empleado.cedula = nueva_cedula
                empleado.telefono = nuevo_telefono or None
                empleado.direccion = nueva_direccion or None
                empleado.fecha_contratacion = nueva_fecha
                empleado._usuario_email = request.session.get("usuario_email")
                empleado.save()

                messages.success(request, "✏️ Empleado editado correctamente.", extra_tags='editar')



        # ---------------- ELIMINAR ----------------
        elif action == "eliminar":
            empleado_id = request.POST.get("empleado_id")
            empleado = get_object_or_404(Empleado, id_empleado=empleado_id)
            empleado._usuario_email = request.session.get("usuario_email")  # 👈 para signals
            empleado.delete()

            messages.success(request, "🗑️ Empleado eliminado correctamente.", extra_tags='eliminar')


        return redirect("empleados")

    return render(request, "empleados/empleados.html", {"empleados": empleados})


# -------------------------------
# AUDITORÍA DE UN EMPLEADO
# -------------------------------
@role_required(["Administrador"])
def auditoria_empleado(request, empleado_id):
    # (si tu login propio usa sesión, puedes validar aquí también)
    # if not request.session.get("usuario_id"):
    #     return redirect("login")

    empleado = get_object_or_404(Empleado, id_empleado=empleado_id)
    auditoria = EmpleadosAuditoria.objects.filter(empleado=empleado).order_by("-fecha")

    return render(
        request,
        "empleados/auditoria_empleado.html",
        {
            "empleado": empleado,
            "auditoria": auditoria,
        },
    )

