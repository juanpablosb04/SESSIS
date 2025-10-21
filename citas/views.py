from django.shortcuts import render, get_object_or_404, redirect
from .models import Cita
from clientes.models import Clientes

# ======================================================
# REGISTRAR CITAS
# ======================================================
def registrar_citas(request):
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "crear":
            fecha = request.POST.get("fecha_cita")
            if fecha:
                Cita.objects.create(
                    cliente_id=int(request.POST["id_cliente"]),
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
def consultar_citas(request):
    if request.method == "POST":
        action = request.POST.get("action")

        if action == "editar":
            cita = get_object_or_404(Cita, id_cita=request.POST.get("cita_id"))

            # Solo actualizar fecha si viene valor
            fecha = request.POST.get("fecha_cita")
            if fecha:
                cita.fecha_cita = fecha

            cita.cliente_id = int(request.POST.get("id_cliente"))

            # Solo sobrescribimos horas si vienen valores
            hora_inicio = request.POST.get("hora_inicio")
            if hora_inicio:
                cita.hora_inicio = hora_inicio

            hora_finalizacion = request.POST.get("hora_finalizacion")
            if hora_finalizacion:
                cita.hora_finalizacion = hora_finalizacion

            cita.motivo = request.POST.get("motivo")
            cita.descripcion = request.POST.get("descripcion")
            cita.save()

            return redirect('citas:consultarCitas')

    citas = Cita.objects.all()
    clientes = Clientes.objects.all()
    return render(request, "citas/consultarCitas.html", {"citas": citas, "clientes": clientes})
