from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from empleados.models import Empleado
from ubicaciones.models import Ubicaciones
from .models import Asistencia
from config.decorators import role_required
from datetime import datetime


def determinar_turno_actual():
    hora = datetime.now().hour
    if 6 <= hora < 14:
        return "06-14"
    elif 14 <= hora < 22:
        return "14-22"
    else:
        return "22-06"


# Create your views here.
@role_required(["Oficial"])
def registrar_asistencia_view(request):
    ubicaciones = Ubicaciones.objects.all().order_by('nombre')
    today = timezone.localdate().strftime('%Y-%m-%d')

    if request.method == "POST":
        id_ubicacion = request.POST.get("id_ubicacion", "").strip()
        observaciones = request.POST.get("observaciones", "").strip()

        usuario_email = request.session.get("usuario_email")
        empleado = get_object_or_404(Empleado, email=usuario_email)

        ubicacion = get_object_or_404(Ubicaciones, id_ubicacion=id_ubicacion)

        try:
            nueva_asistencia = Asistencia.objects.create(
                id_empleado=empleado,
                id_ubicacion=ubicacion,
                turno_ingreso=datetime.now(),
                observaciones=observaciones or None,
                estado='En curso'
            )
            messages.success(
                request,
                f"✅ Asistencia registrada correctamente a las {nueva_asistencia.turno_ingreso.strftime('%H:%M:%S')}.",
                extra_tags="crear"
            )
        except Exception as e:
            messages.error(request, f"⚠️ Error al registrar asistencia: {str(e)}", extra_tags="crear")

        return redirect("registrarAsistencia")

    context = {
        "ubicaciones": ubicaciones,
        "today": today
    }
    return render(request, "asistencia/registrarAsistencia.html", context)


@role_required(["Oficial"])
def asistencias_activas_view(request):
    usuario_email = request.session.get("usuario_email")
    empleado = get_object_or_404(Empleado, email=usuario_email)

    asistencias = Asistencia.objects.filter(
        id_empleado=empleado,
        estado='En curso'
    ).order_by('turno_ingreso')

    if request.method == "POST":
        accion = request.POST.get("accion")
        id_asistencia = request.POST.get("id_asistencia")
        asistencia = get_object_or_404(Asistencia, id_asistencia=id_asistencia)

        if accion == "salida":
            asistencia.turno_salida = datetime.now()
            asistencia.estado = 'Finalizado'
            asistencia.save()
            messages.success(request, f"✅ Turno finalizado a las {asistencia.turno_salida.strftime('%H:%M:%S')}", extra_tags="crear")
        elif accion == "editar":
            observaciones = request.POST.get("observaciones", "").strip()
            asistencia.observaciones = observaciones or None
            asistencia.save()
            messages.success(request, "✅ Observaciones actualizadas correctamente", extra_tags="crear")

        return redirect("consultarAsistencia")

    return render(request, "asistencia/consultarAsistencia.html", {"asistencias": asistencias})