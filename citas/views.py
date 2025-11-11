from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Cita
from clientes.models import Clientes
from config.decorators import role_required

# ======================================================
# REGISTRAR CITAS
# ======================================================
@role_required(["Administrador"])
def registrar_citas(request):
    if not request.session.get("usuario_id"):
        return redirect("login")

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "crear":
            fecha = request.POST.get("fecha_cita")
            if fecha:
                # Crear cita asociada al usuario que la registra
                Cita.objects.create(
                    cliente_id=int(request.POST["id_cliente"]),
                    usuario_id=request.session["usuario_id"],  # Asociar usuario logueado
                    fecha_cita=fecha,
                    hora_inicio=request.POST.get("hora_inicio") or None,
                    hora_finalizacion=request.POST.get("hora_finalizacion") or None,
                    motivo=request.POST.get("motivo"),
                    descripcion=request.POST.get("descripcion")
                )
                return redirect("citas:consultarCitas")

    clientes = Clientes.objects.all()
    return render(request, "citas/registrarCitas.html", {"clientes": clientes})


# ======================================================
# CONSULTAR, EDITAR Y ELIMINAR CITAS
# ======================================================
@role_required(["Administrador"])
def consultar_citas(request):
    if not request.session.get("usuario_id"):
        return redirect("login")

    usuario_id = request.session.get("usuario_id")
    now = timezone.localtime()
    today = now.date()
    current_time = now.time()

    # =========================
    # Acciones POST: editar o eliminar
    # =========================
    if request.method == "POST":
        action = request.POST.get("action")

        if action == "editar":
            cita = get_object_or_404(Cita, id_cita=request.POST.get("cita_id"))

            fecha = request.POST.get("fecha_cita")
            if fecha:
                cita.fecha_cita = fecha

            cita.cliente_id = int(request.POST.get("id_cliente"))
            cita.hora_inicio = request.POST.get("hora_inicio") or None
            cita.hora_finalizacion = request.POST.get("hora_finalizacion") or None
            cita.motivo = request.POST.get("motivo")
            cita.descripcion = request.POST.get("descripcion")
            cita.save()

            return redirect('citas:consultarCitas')

        elif action == "eliminar":
            cita = get_object_or_404(Cita, id_cita=request.POST.get("cita_id"))
            cita.delete()
            return redirect('citas:consultarCitas')

    # =========================
    # Filtrar solo citas activas para este usuario
    # =========================
    citas_activas = (
        Cita.objects.filter(usuario_id=usuario_id, fecha_cita__gt=today) |
        Cita.objects.filter(usuario_id=usuario_id, fecha_cita=today, hora_finalizacion__gte=current_time)
    )

    clientes = Clientes.objects.all()
    return render(request, "citas/consultarCitas.html", {
        "citas": citas_activas,
        "clientes": clientes
    })