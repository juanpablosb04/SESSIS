from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.db.models import Q
from django.contrib import messages 
from datetime import datetime, time # Necesario para la validación de horas

from .models import Cita
from clientes.models import Clientes
from cuentas.models import Usuarios # Necesario para buscar el usuario
from config.decorators import role_required


def verificar_superposicion(usuario_id, fecha, hora_inicio, hora_finalizacion, cita_id=None):
    """Verifica si una nueva cita se superpone con las existentes del mismo usuario."""
    
    # Convierte las horas de string a objetos time para comparación
    try:
        start_time = time.fromisoformat(hora_inicio)
        end_time = time.fromisoformat(hora_finalizacion)
    except ValueError:
        return "Formato de hora inválido."

    # Si la hora de inicio es igual o posterior a la hora de finalización
    if start_time >= end_time:
        return "La hora de inicio debe ser anterior a la hora de finalización."

    # Filtra citas existentes que se superponen
    # Una superposición ocurre si:
    # 1. El inicio de la nueva cita está entre el inicio y fin de una existente.
    # 2. El fin de la nueva cita está entre el inicio y fin de una existente.
    # 3. La nueva cita envuelve completamente a una existente.
    # 4. Una cita existente envuelve completamente a la nueva.
    
    superposiciones = Cita.objects.filter(
    Q(usuario_id=usuario_id) &
    Q(fecha_cita=fecha) &
    Q(hora_inicio__lt=end_time, hora_finalizacion__gt=start_time)
)
    
    # Excluir la cita actual si estamos editando
    if cita_id:
        superposiciones = superposiciones.exclude(id_cita=cita_id)

    if superposiciones.exists():
        # Obtener los datos de la primera cita con la que se superpone para dar un mejor error
        cita_existente = superposiciones.first()
        hora_existente_inicio = cita_existente.hora_inicio.strftime("%H:%M")
        hora_existente_fin = cita_existente.hora_finalizacion.strftime("%H:%M")
        
        return f"Ya existe una cita programada para el usuario en la fecha {fecha} entre las {hora_existente_inicio} y {hora_existente_fin}."
        
    return None # No hay error de superposición

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
            cliente_id = request.POST.get("id_cliente")
            fecha = request.POST.get("fecha_cita")
            hora_inicio = request.POST.get("hora_inicio")
            hora_finalizacion = request.POST.get("hora_finalizacion")
            motivo = request.POST.get("motivo")
            descripcion = request.POST.get("descripcion")
            usuario_id = request.session["usuario_id"]

            # 1. Validaciones de Campos Vacíos (Obligatorios según el formulario)
            if not cliente_id or not fecha or not hora_inicio or not hora_finalizacion or not motivo:
                messages.error(request, "Error al registrar: Todos los campos obligatorios (Cliente, Fecha, Hora de inicio, Hora de finalización, Motivo) deben estar llenos.", extra_tags="alert-error")
                # Se utiliza el contexto para rellenar los campos que el usuario había enviado (opcional, pero útil)
                clientes = Clientes.objects.all()
                return render(request, "citas/registrarCitas.html", {"clientes": clientes, "datos_anteriores": request.POST})

            # 2. Validación de Superposición y Horas
            error_superposicion = verificar_superposicion(usuario_id, fecha, hora_inicio, hora_finalizacion)
            if error_superposicion:
                messages.error(request, f"Error de horario: {error_superposicion}", extra_tags="alert-error")
                clientes = Clientes.objects.all()
                return render(request, "citas/registrarCitas.html", {"clientes": clientes, "datos_anteriores": request.POST})


            # Si todo es válido, se crea la cita
            Cita.objects.create(
                cliente_id=int(cliente_id),
                usuario_id=usuario_id,  # Asociar usuario logueado
                fecha_cita=fecha,
                hora_inicio=hora_inicio,
                hora_finalizacion=hora_finalizacion,
                motivo=motivo,
                descripcion=descripcion
            )
            messages.success(request, "Cita registrada exitosamente.", extra_tags="alert-success")
            return redirect("citas:consultarCitas")

    clientes = Clientes.objects.all()
    # Pasa un diccionario vacío si no hay datos de formulario anteriores para evitar errores en el template
    return render(request, "citas/registrarCitas.html", {"clientes": clientes, "datos_anteriores": {}})


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
            cita_id = request.POST.get("cita_id")
            cliente_id = request.POST.get("id_cliente")
            fecha = request.POST.get("fecha_cita")
            hora_inicio = request.POST.get("hora_inicio")
            hora_finalizacion = request.POST.get("hora_finalizacion")
            motivo = request.POST.get("motivo")
            descripcion = request.POST.get("descripcion")

            # --- 1. Validaciones de Campos Vacíos (Obligatorios) ---
            if not cliente_id or not fecha or not hora_inicio or not hora_finalizacion or not motivo:
                messages.error(request, "Error al editar: Todos los campos obligatorios deben estar llenos.", extra_tags="alert-error")
                return redirect('citas:consultarCitas')

            # --- 2. Validación de Superposición y Horas ---
            error_superposicion = verificar_superposicion(usuario_id, fecha, hora_inicio, hora_finalizacion, cita_id=cita_id)
            if error_superposicion:
                messages.error(request, f"Error de horario: {error_superposicion}", extra_tags="alert-error")
                return redirect('citas:consultarCitas')

            # --- 3. Buscar y Actualizar Cita ---
            try:
                cita = get_object_or_404(Cita, id_cita=cita_id)
                
                # Opcional: verificar si el cliente existe, aunque el FK debería manejarlo
                Clientes.objects.get(id_cliente=int(cliente_id)) 
                
            except Cita.DoesNotExist:
                messages.error(request, "Error al editar: La cita a modificar no fue encontrada.", extra_tags="alert-error")
                return redirect('citas:consultarCitas')
            except Clientes.DoesNotExist:
                messages.error(request, "Error al editar: El cliente seleccionado no es válido.", extra_tags="alert-error")
                return redirect('citas:consultarCitas')


            # Si todas las validaciones son correctas, se guarda
            cita.fecha_cita = fecha
            cita.cliente_id = int(cliente_id)
            cita.hora_inicio = hora_inicio
            cita.hora_finalizacion = hora_finalizacion
            cita.motivo = motivo
            cita.descripcion = descripcion
            cita.save()

            messages.success(request, "Cita editada exitosamente.", extra_tags="alert-success")
            return redirect('citas:consultarCitas')

        elif action == "eliminar":
            # Si decides usar la funcionalidad de eliminar en el futuro, esta es la lógica
            cita = get_object_or_404(Cita, id_cita=request.POST.get("cita_id"))
            cita.delete()
            messages.success(request, "Cita eliminada exitosamente.", extra_tags="alert-success")
            return redirect('citas:consultarCitas')

    # =========================
    # Filtrar solo citas activas para este usuario
    # =========================
    citas_activas = (
        Cita.objects.filter(usuario_id=usuario_id, fecha_cita__gt=today) |
        Cita.objects.filter(usuario_id=usuario_id, fecha_cita=today, hora_finalizacion__gte=current_time)
    ).order_by('fecha_cita', 'hora_inicio') # Ordenar para mejor visualización

    clientes = Clientes.objects.all()
    return render(request, "citas/consultarCitas.html", {
        "citas": citas_activas,
        "clientes": clientes
    })