# empleados/views.py
from django.shortcuts import render, get_object_or_404, redirect
from decimal import Decimal, InvalidOperation
import re
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Empleado, EmpleadosAuditoria, Asistencia
from config.decorators import role_required
from datetime import datetime , date
from django.utils import timezone
from django.db.models import Q
from .models import (
    Empleado,
    EmpleadosAuditoria,
    HorasExtras,
    HorasExtrasAuditoria,
)

# =========================
# Utilidades
# =========================
def _to_decimal(val: str) -> Decimal:
    if val is None:
        raise InvalidOperation()
    return Decimal(str(val).strip().replace(",", "."))

def _parse_bool(value, fallback=False):
    if value is None:
        return fallback
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value != 0
    if isinstance(value, str):
        value = value.strip().lower()
        if value in ("1", "true", "t", "yes", "y", "on", "activo", "active"):
            return True
        if value in ("0", "false", "f", "no", "n", "off", "inactivo", "inactive"):
            return False
    return fallback


# =========================
# Empleados (CRUD básico)
# =========================
@role_required(["Administrador"])
def empleados_view(request):
    empleados_qs = Empleado.objects.all().order_by("nombre_completo")

    paginator = Paginator(empleados_qs, 5)
    page_number = request.GET.get("page")
    empleados = paginator.get_page(page_number)

    if request.method == "POST":
        action = request.POST.get("action")

        # -------- CREAR --------
        if action == "crear":
            nombre    = request.POST.get("nombre_completo", "").strip()
            email     = request.POST.get("email", "").strip()
            cedula    = request.POST.get("cedula", "").strip()
            telefono  = request.POST.get("telefono", "").strip()
            direccion = request.POST.get("direccion", "").strip()
            fecha_s   = request.POST.get("fecha_contratacion", "").strip()

            if not nombre or not email or not cedula or not fecha_s:
                messages.error(request, "⚠️ Nombre, correo, cédula y fecha son obligatorios.", extra_tags="crear alert-error")

            elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                messages.error(request, "⚠️ El correo no tiene un formato válido.", extra_tags="crear alert-error")

            elif Empleado.objects.filter(email=email).exists():
                messages.error(request, "⚠️ El correo ya está registrado.", extra_tags="crear alert-error")

            elif Empleado.objects.filter(cedula=cedula).exists():
                messages.error(request, "⚠️ La cédula ya está registrada.", extra_tags="crear alert-error")

            else:
                # Parsear fecha y bloquear futuras (admite YYYY-MM-DD y dd/mm/YYYY)
                fecha_dt = None
                for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
                    try:
                        fecha_dt = datetime.strptime(fecha_s, fmt).date()
                        break
                    except ValueError:
                        continue

                if not fecha_dt:
                    messages.error(request, "⚠️ La fecha de contratación no es válida.", extra_tags="crear alert-error")
                else:
                    hoy = timezone.localdate()
                    if fecha_dt > hoy:
                        messages.error(request, "⚠️ La fecha de contratación no puede ser futura.", extra_tags="crear alert-error")
                    else:
                        Empleado.objects.create(
                            nombre_completo=nombre,
                            email=email,
                            cedula=cedula,
                            telefono=telefono or None,
                            direccion=direccion or None,
                            fecha_contratacion=fecha_dt,
                        )
                        empleado._usuario_email=request.session.get("usuario_email")
                        empleado.save()
                        messages.success(request, "✅ Empleado creado correctamente.", extra_tags="crear alert-success")
                        return redirect("empleados")  # evita reenvío y muestra el message

        # -------- EDITAR --------
        elif action == "editar":
            empleado_id = request.POST.get("empleado_id")
            empleado = get_object_or_404(Empleado, id_empleado=empleado_id)

            nuevo_nombre    = request.POST.get("nombre_completo", "").strip()
            nuevo_email     = request.POST.get("email", "").strip()
            nueva_cedula    = request.POST.get("cedula", "").strip()
            nuevo_telefono  = request.POST.get("telefono", "").strip()
            nueva_direccion = request.POST.get("direccion", "").strip()
            nueva_fecha_s   = request.POST.get("fecha_contratacion", "").strip()

            if not nuevo_nombre or not nuevo_email or not nueva_cedula or not nueva_fecha_s:
                messages.error(request, "⚠️ Nombre, correo, cédula y fecha son obligatorios.", extra_tags="editar alert-error")

            elif not re.match(r"[^@]+@[^@]+\.[^@]+", nuevo_email):
                messages.error(request, "⚠️ El correo no tiene un formato válido.", extra_tags="editar alert-error")

            elif Empleado.objects.filter(email=nuevo_email).exclude(id_empleado=empleado.id_empleado).exists():
                messages.error(request, "⚠️ Ese correo ya está en uso.", extra_tags="editar alert-error")

            elif Empleado.objects.filter(cedula=nueva_cedula).exclude(id_empleado=empleado.id_empleado).exists():
                messages.error(request, "⚠️ Esa cédula ya está en uso.", extra_tags="editar alert-error")

            else:
                nueva_fecha_dt = None
                for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
                    try:
                        nueva_fecha_dt = datetime.strptime(nueva_fecha_s, fmt).date()
                        break
                    except ValueError:
                        continue

                if not nueva_fecha_dt:
                    messages.error(request, "⚠️ La fecha de contratación no es válida.", extra_tags="editar alert-error")
                else:
                    hoy = timezone.localdate()
                    if nueva_fecha_dt > hoy:
                        messages.error(request, "⚠️ La fecha de contratación no puede ser futura.", extra_tags="editar alert-error")
                    else:
                        empleado.nombre_completo    = nuevo_nombre
                        empleado.email              = nuevo_email
                        empleado.cedula             = nueva_cedula
                        empleado.telefono           = nuevo_telefono or None
                        empleado.direccion          = nueva_direccion or None
                        empleado.fecha_contratacion = nueva_fecha_dt
                        
                        empleado._usuario_email=request.session.get("usuario_email")
                        empleado.save()
                        messages.success(request, "✏️ Empleado editado correctamente.", extra_tags="editar alert-success")
                        return redirect("empleados")

        # -------- CAMBIAR ESTADO (Activo/Inactivo) --------
        elif action == "cambiar_estado":
            empleado_id = request.POST.get("empleado_id")
            empleado = get_object_or_404(Empleado, id_empleado=empleado_id)

            raw = request.POST.get("estado", request.POST.get("activo"))
            nuevo_estado = _parse_bool(raw, fallback=not empleado.estado)

            empleado.estado = nuevo_estado
            empleado.save()
            messages.success(
                request,
                f"🔁 Estado del empleado actualizado a {'Activo' if nuevo_estado else 'Inactivo'} correctamente",
                extra_tags="editar alert-success",
            )
            return redirect("empleados")

    # today => para usar como max en el input date (evita popups y fechas futuras en el front)
    return render(
        request,
        "empleados/empleados.html",
        {"empleados": empleados, "page_obj": empleados, "today": date.today()},
    )
# =========================
# Horas extras (Admin)
# =========================
@role_required(["Administrador"])
def horas_extras_admin(request):
    empleados = Empleado.objects.all().order_by("nombre_completo")

    if request.method == "POST":
        action = (request.POST.get("action") or "crear").strip().lower()

        # ---------- CREAR ----------
        if action == "crear":
            emp_id = request.POST.get("empleado_id")
            fecha = request.POST.get("fecha")
            horas_raw = (request.POST.get("cantidad_horas") or "").strip()
            just = (request.POST.get("justificacion") or "").strip()
            estado = (request.POST.get("estado") or "").strip()

            if not emp_id or not fecha or not horas_raw or not estado:
                messages.error(request, "⚠️ Empleado, fecha, horas y estado son obligatorios.", extra_tags='crear alert-error')
                return redirect("horasExtras")

            empleado = get_object_or_404(Empleado, id_empleado=emp_id)

            # aceptar 3,5 o 3.5
            try:
                horas_dec = Decimal(horas_raw.replace(",", "."))
            except (InvalidOperation, TypeError):
                messages.error(request, "⚠️ La cantidad de horas no es un número válido.", extra_tags='crear alert-error')
                return redirect("horasExtras")

            if horas_dec <= 0:
                messages.error(request, "⚠️ La cantidad de horas debe ser mayor que 0.", extra_tags='crear alert-error')
                return redirect("horasExtras")
            if horas_dec > Decimal("24"):
                messages.error(request, "⚠️ Máximo permitido: 24 horas por registro.", extra_tags='crear alert-error')
                return redirect("horasExtras")

            ESTADOS = {
                "aprobado": "Aprobado",
                "en revisión": "En revisión",
                "en revision": "En revisión",
                "rechazado": "Rechazado",
                "pendiente": "Pendiente",
                "aprobado": "Aprobado",
            }
            estado_norm = ESTADOS.get(estado.lower(), estado)

            # ¡Crear en dos pasos para setear _usuario_email antes del save!
            registro = HorasExtras(
                empleado=empleado,
                fecha=fecha,
                cantidad_horas=horas_dec,
                justificacion=just or None,
                estado=estado_norm,
            )
            registro._usuario_email = request.session.get("usuario_email")
            registro.save()

            messages.success(request, "✅ Horas extras registradas correctamente.", extra_tags='crear alert-success')
            return redirect("horasExtras")

        # ---------- EDITAR (opcional, si ya lo usas desde el modal) ----------
        elif action == "editar":
            he_id = request.POST.get("hora_extra_id")
            emp_id = request.POST.get("empleado_id")
            fecha = request.POST.get("fecha")
            horas_raw = (request.POST.get("cantidad_horas") or "").strip()
            just = (request.POST.get("justificacion") or "").strip()
            estado = (request.POST.get("estado") or "").strip()

            registro = get_object_or_404(HorasExtras, id_hora_extra=he_id)
            empleado = get_object_or_404(Empleado, id_empleado=emp_id)

            try:
                horas_dec = Decimal(horas_raw.replace(",", "."))
            except (InvalidOperation, TypeError):
                messages.error(request, "⚠️ La cantidad de horas no es un número válido.", extra_tags='editar alert-error')
                return redirect("horasExtras")

            ESTADOS = {
                "aprobado": "Aprobado",
                "en revisión": "En revisión",
                "en revision": "En revisión",
                "rechazado": "Rechazado",
                "pendiente": "Pendiente",
            }
            estado_norm = ESTADOS.get(estado.lower(), estado)
            registro.empleado = empleado
            registro.fecha = fecha
            registro.cantidad_horas = horas_dec
            registro.justificacion = just or None
            registro.estado = estado_norm
            registro._usuario_email = request.session.get("usuario_email")
            registro.save()

            messages.success(request, "✏️ Registro actualizado.", extra_tags='editar alert-success')
            return redirect("horasExtras")

        # ---------- CUALQUIER OTRA ACCIÓN ----------
        else:
            messages.error(request, "Acción no soportada.", extra_tags='editar')
            return redirect("horasExtras")

    # GET -> historial para la tabla
    registros_qs = (
    HorasExtras.objects
    .select_related("empleado")
    .order_by("-fecha", "-id_hora_extra")
    )

    paginator_registros = Paginator(registros_qs, 5)
    page_number_reg = request.GET.get("page")
    registros = paginator_registros.get_page(page_number_reg)

    return render(
    request,
    "empleados/horasExtras.html",
    {"empleados": empleados, "registros": registros},
)

# =====================================================
# Revisar Asistencia de Empleados
# =====================================================
@role_required(["Administrador"])
def ver_asistencia_Empleados(request):
    empleados = Empleado.objects.all().order_by('nombre_completo')
    asistencias = Asistencia.objects.select_related('id_empleado', 'id_ubicacion').all().order_by('-turno_ingreso')

    empleado_id = request.GET.get("id_empleado", "").strip()
    fecha_inicio = request.GET.get("fecha_inicio", "").strip()
    fecha_fin = request.GET.get("fecha_fin", "").strip()

    filtros = Q()
    if empleado_id:
        filtros &= Q(id_empleado__id_empleado=empleado_id)
    if fecha_inicio:
        filtros &= Q(turno_ingreso__date__gte=fecha_inicio)
    if fecha_fin:
        filtros &= Q(turno_ingreso__date__lte=fecha_fin)

    if filtros:
        asistencias = asistencias.filter(filtros)

    context = {
        "empleados": empleados,
        "asistencias": asistencias,
        "empleado_seleccionado": empleado_id,
    }
    return render(request, "empleados/verAsistenciaOficiales.html", context)


# =========================
# Auditoría
# =========================
@role_required(["Administrador"])
def auditoria_empleado(request, empleado_id):
    if not request.session.get("usuario_id"):
        return redirect("login")
    
    empleado = get_object_or_404(Empleado, id_empleado=empleado_id)
    auditoria = EmpleadosAuditoria.objects.filter(empleado=empleado).order_by("-fecha")

    paginator = Paginator(auditoria, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "empleados/auditoria_empleado.html",
        {"empleado": empleado,
          "page_obj": page_obj},
    )

@role_required(["Administrador"])
def auditoria_horas_extras_por_empleado(request, empleado_id):
    """
    Muestra la auditoría de horas extra de un empleado específico.
    Requiere el modelo HorasExtrasAuditoria con campos:
      - empleado (FK Empleado, nullable)
      - usuario_email (char, nullable)
      - accion (char)
      - fecha (datetime)
      - fecha_registro (date), cantidad_horas (decimal), justificacion (char), estado (char)  # snapshot
    """
    empleado = get_object_or_404(Empleado, id_empleado=empleado_id)
    logs = (
        HorasExtrasAuditoria.objects
        .filter(empleado=empleado)
        .order_by("-fecha")[:300]
    )

    paginator = Paginator(logs, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "empleados/auditoria_horas_extras.html",
        {"empleado": empleado, "logs": logs, "page_obj": page_obj},
    )

# =========================
# Consultar horas extras (Oficial)

@role_required(["Oficial"])
def consultar_horas_extras_oficial(request):
    usuario_email = request.session.get("usuario_email")
    empleado = Empleado.objects.filter(email=usuario_email).first() if usuario_email else None

    if not empleado:
        messages.warning(
            request,
            "No se encontró un empleado asociado a tu cuenta. "
            "Contacta al administrador para vincular tu usuario con un empleado."
        )
        registros = []
        total_horas_aprobadas = Decimal("0")
        ultima_actualizacion = timezone.now().date()
        page_obj = []
    else:
        # Traer TODOS los registros
        registros_qs = (
            HorasExtras.objects
            .select_related("empleado")
            .filter(empleado=empleado)
            .order_by("-fecha", "-id_hora_extra")
        )

        # ---- PAGINACIÓN ----
        paginator = Paginator(registros_qs, 5)  # 10 registros por página
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        # Suma solo horas aprobadas
        total_horas_aprobadas = (
            HorasExtras.objects
            .filter(empleado=empleado, estado__iexact="Aprobado")
            .aggregate(suma=Sum("cantidad_horas"))
            .get("suma") or Decimal("0")
        )

        # Última actualización
        ultimo = registros_qs.first()
        ultima_actualizacion = ultimo.fecha if ultimo else timezone.now().date()

    return render(
        request,
        "empleados/consultarHorasExtras.html",
        {
            "empleado": empleado,
            "page_obj": page_obj,               # <- se usa en el HTML
            "registros": page_obj.object_list,  # <- solo los de la página actual
            "total_horas": total_horas_aprobadas,
            "ultima_actualizacion": ultima_actualizacion,
        },
    )
