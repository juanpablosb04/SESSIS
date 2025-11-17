# clientes/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Clientes, ClientesAuditoria
from ubicaciones.models import Ubicaciones
from django.core.paginator import Paginator
from config.decorators import role_required
import re


def _parse_bool(value, fallback):
    """
    Convierte strings como '1','0','true','false','on','si','sí','activo','inactivo'
    a booleano. Si value es None o no matchea, devuelve 'fallback'.
    """
    if value is None:
        return fallback
    v = str(value).strip().lower()
    if v in ("1", "true", "on", "si", "sí", "activo"):
        return True
    if v in ("0", "false", "off", "no", "inactivo"):
        return False
    return fallback


@role_required(["Administrador"])
def clientes_view(request):
    # Valida sesión (tu login propio)
    if not request.session.get("usuario_id"):
        return redirect("login")

    # Lista de clientes + FK de ubicación
    clientes = (
        Clientes.objects.select_related("id_ubicacion")
        .all()
        .order_by("nombre_completo")
    )
    ubicaciones = Ubicaciones.objects.all().order_by("nombre")
    

    paginator = Paginator(clientes, 5)
    page_number = request.GET.get("page")
    clientes = paginator.get_page(page_number)



    if request.method == "POST":
        action = request.POST.get("action")

        # ---------------- CREAR ----------------
        if action == "crear":
            nombre = request.POST.get("nombre")
            email = request.POST.get("email")
            cedula = request.POST.get("cedula")
            telefono = request.POST.get("telefono")
            id_ubicacion = request.POST.get("id_ubicacion")

            # Validaciones básicas
            if not nombre or not email or not cedula:
                messages.error(request, "⚠️ Nombre, email y cédula son obligatorios", extra_tags='crear')
            elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                messages.error(request, "⚠️ El correo no tiene un formato válido", extra_tags='crear')
            elif Clientes.objects.filter(email=email).exists():
                messages.error(request, "⚠️ El correo ya está registrado", extra_tags='crear')
            elif Clientes.objects.filter(cedula=cedula).exists():
                messages.error(request, "⚠️ La cédula ya está registrada", extra_tags='crear')
            else:
                # Resolver ubicación si viene
                ubic = None
                if id_ubicacion:
                    try:
                        ubic = Ubicaciones.objects.get(id_ubicacion=id_ubicacion)
                    except Ubicaciones.DoesNotExist:
                        messages.warning(
                            request,
                            "La ubicación seleccionada no existe. Se guardará sin ubicación.", extra_tags='crear'
                        )

                cliente = Clientes(
                    nombre_completo=nombre,
                    email=email,
                    cedula=cedula,
                    telefono=telefono,
                    id_ubicacion=ubic,
                )
                # Correo del ejecutor para auditoría en signals
                cliente._usuario_email = request.session.get("usuario_email")
                cliente.save()
                messages.success(request, "✅ Cliente creado correctamente", extra_tags='crear')

        # ---------------- EDITAR ----------------
        elif action == "editar":
            cliente_id = request.POST.get("cliente_id")
            cliente = get_object_or_404(Clientes, id_cliente=cliente_id)

            nuevo_email = request.POST.get("email")
            nueva_cedula = request.POST.get("cedula")
            id_ubicacion = request.POST.get("id_ubicacion")

            if (
                Clientes.objects.filter(email=nuevo_email)
                .exclude(id_cliente=cliente.id_cliente)
                .exists()
            ):
                messages.error(request, "⚠️ Ese correo ya está en uso", extra_tags='editar')
            elif (
                Clientes.objects.filter(cedula=nueva_cedula)
                .exclude(id_cliente=cliente.id_cliente)
                .exists()
            ):
                messages.error(request, "⚠️ Esa cédula ya está en uso", extra_tags='editar')
            else:
                # Resolver ubicación si viene
                ubic = None
                if id_ubicacion:
                    try:
                        ubic = Ubicaciones.objects.get(id_ubicacion=id_ubicacion)
                    except Ubicaciones.DoesNotExist:
                        messages.warning(
                            request,
                            "La ubicación seleccionada no existe. Se guardará sin ubicación.", extra_tags='editar'
                        )
                        ubic = None

                cliente.nombre_completo = request.POST.get("nombre")
                cliente.email = nuevo_email
                cliente.cedula = nueva_cedula
                cliente.telefono = request.POST.get("telefono")
                cliente.id_ubicacion = ubic

                # Correo del ejecutor para auditoría en signals
                cliente._usuario_email = request.session.get("usuario_email")
                cliente.save()
                messages.success(request, "✏️ Cliente editado correctamente", extra_tags='editar')

        # ---------------- CAMBIAR ESTADO (Activo/Inactivo) ----------------
        elif action == "cambiar_estado":
            cliente_id = request.POST.get("cliente_id")
            cliente = get_object_or_404(Clientes, id_cliente=cliente_id)

            # Si el form envía 'estado' lo usamos; si no, hacemos toggle
            # (Por compatibilidad, también aceptamos 'activo')
            raw = request.POST.get("estado", request.POST.get("activo"))
            nuevo_estado = _parse_bool(raw, fallback=not cliente.estado)

            cliente.estado = nuevo_estado
            cliente._usuario_email = request.session.get("usuario_email")  # para auditoría
            cliente.save()

            messages.success(
                request,
                f"🔁 Estado actualizado a {'Activo' if nuevo_estado else 'Inactivo'} correctamente", extra_tags='editar'
            )

        # Redirige siempre para evitar re-envío del form
        return redirect("clientes")

    return render(
        request,
        "clientes/clientes.html",
        {
            "clientes": clientes,
            "ubicaciones": ubicaciones,
        },
    )


# -------------------------------
# AUDITORÍA DE UN CLIENTE
# -------------------------------
@role_required(["Administrador"])
def auditoria_cliente(request, cliente_id):
    if not request.session.get("usuario_id"):
        return redirect("login")

    cliente = get_object_or_404(Clientes, id_cliente=cliente_id)
    auditoria_qs = ClientesAuditoria.objects.filter(cliente=cliente).order_by("-fecha")

    paginator = Paginator(auditoria_qs, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "clientes/auditoria_cliente.html",
        {
            "cliente": cliente,
            "page_obj": page_obj,
        },
    )











