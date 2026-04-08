# views/asistencia
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.db.models import Sum

from datetime import datetime, time
from decimal import Decimal
from io import BytesIO

from empleados.models import Empleado
from ubicaciones.models import Ubicaciones
from .models import Asistencia
from config.decorators import role_required

# --- HELPERS INICIALES ---

def determinar_turno_actual():
    hora = datetime.now().hour
    if 6 <= hora < 14:
        return "06-14"
    elif 14 <= hora < 22:
        return "14-22"
    else:
        return "22-06"

def obtener_empleado_desde_sesion(request):
    """
    Obtiene el empleado usando el email de la sesión. 
    Usa importación interna para prevenir Error 500 por ciclos.
    """
    email_login = request.session.get("usuario_email")
    if not email_login:
        return None
    
    try:
        from cuentas.models import Usuarios
        user_obj = Usuarios.objects.filter(email=email_login).select_related('id_empleado').first()
        return user_obj.id_empleado if user_obj else None
    except Exception:
        return None

# --- VISTAS DE REGISTRO ---

@role_required(["Oficial"])
def registrar_asistencia_view(request):
    ubicaciones = Ubicaciones.objects.all().order_by('nombre')
    today = timezone.localdate()
    empleado = obtener_empleado_desde_sesion(request)

    if not empleado:
        messages.error(request, "Error: Usuario sin empleado vinculado.")
        return redirect("inicio")

    if request.method == "POST":
        id_ubicacion = request.POST.get("id_ubicacion", "").strip()
        observaciones = request.POST.get("observaciones", "").strip()
        ubicacion = get_object_or_404(Ubicaciones, id_ubicacion=id_ubicacion)

        try:
            nueva_asistencia = Asistencia.objects.create(
                id_empleado=empleado,
                id_ubicacion=ubicacion,
                turno_ingreso=timezone.now(),
                observaciones=observaciones or None,
                estado='En curso'
            )
            messages.success(request, f"✅ Registrado a las {timezone.localtime(nueva_asistencia.turno_ingreso).strftime('%H:%M:%S')}.", extra_tags='crear alert-success')
        except Exception as e:
            messages.error(request, f"⚠️ Error: {str(e)}", extra_tags='crear alert-error')
        return redirect("registrarAsistencia")

    return render(request, "asistencia/registrarAsistencia.html", {"ubicaciones": ubicaciones, "today": today})

@role_required(["Oficial"])
def asistencias_activas_view(request):
    empleado = obtener_empleado_desde_sesion(request)
    if not empleado:
        messages.error(request, "No se encontró empleado.")
        return redirect("inicio")

    asistencias = Asistencia.objects.filter(id_empleado=empleado, estado='En curso').order_by('turno_ingreso')

    if request.method == "POST":
        accion = request.POST.get("accion")
        id_asistencia = request.POST.get("id_asistencia")
        asistencia = get_object_or_404(Asistencia, id_asistencia=id_asistencia)

        if accion == "salida":
            asistencia.turno_salida = timezone.now()
            asistencia.estado = 'Finalizado'
            asistencia.save()
            messages.success(request, "✅ Turno finalizado", extra_tags='editar alert-success')
        elif accion == "editar":
            asistencia.observaciones = request.POST.get("observaciones", "").strip() or None
            asistencia.save()
            messages.success(request, "✅ Actualizado", extra_tags='editar alert-success')
        return redirect("consultarAsistencia")

    return render(request, "asistencia/consultarAsistencia.html", {"asistencias": asistencias})

# --- LÓGICA DE FILTRADO Y EXPORTACIÓN ---

DATE_FORMATS = ("%Y-%m-%d", "%d/%m/%Y")

def parse_date(s: str):
    if not s: return None
    s = s.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError: continue
    return None

def make_aware_dt(d, end=False):
    if not d: return None
    naive = datetime.combine(d, time.max if end else time.min)
    return timezone.make_aware(naive, timezone.get_current_timezone())

def _build_filtered_qs_oficiales(request):
    empleado_actual = obtener_empleado_desde_sesion(request)
    
    empleado_id  = (request.GET.get("id_empleado") or "").strip()
    fecha_inicio = (request.GET.get("fecha_inicio") or "").strip()
    fecha_fin    = (request.GET.get("fecha_fin") or "").strip()

    di = parse_date(fecha_inicio)
    df = parse_date(fecha_fin)
    di_dt = make_aware_dt(di, end=False) if di else None
    df_dt = make_aware_dt(df, end=True)  if df else None

    qs = Asistencia.objects.select_related("id_empleado", "id_ubicacion").all()

    # Seguridad de rol
    es_oficial = (request.session.get("usuario_rol") == "Oficial") or (getattr(request.user, "rol", None) == "Oficial")

    if es_oficial and empleado_actual:
        qs = qs.filter(id_empleado=empleado_actual)
    elif empleado_id:
        qs = qs.filter(id_empleado__pk=empleado_id)

    if di_dt: qs = qs.filter(turno_ingreso__gte=di_dt)
    if df_dt: qs = qs.filter(turno_ingreso__lte=df_dt)

    return qs.order_by("-turno_ingreso"), {"empleado_id": empleado_id, "fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin}, es_oficial, empleado_actual

@role_required(["Administrador"])
def ver_asistencia_oficiales_view(request):
    qs, filtros_ctx, es_oficial, empleado_actual = _build_filtered_qs_oficiales(request)

    if es_oficial and empleado_actual:
        empleados = Empleado.objects.filter(pk=empleado_actual.pk)
    else:
        empleados = Empleado.objects.all().order_by("nombre_completo")

    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    ctx = {"empleados": empleados, "asistencias": page_obj, "page_obj": page_obj, **filtros_ctx}
    return render(request, "empleados/verAsistenciaOficiales.html", ctx)

@role_required(["Administrador"])
def ver_asistencia_oficiales_export(request):
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment
    
    qs, filtros_ctx, _, _ = _build_filtered_qs_oficiales(request)
    wb = Workbook()
    ws = wb.active
    ws.title = "Asistencias"

    headers = ["Fecha", "Empleado", "Hora Entrada", "Hora Salida", "Ubicación", "Observaciones", "Estado"]
    ws.append(headers)

    for c in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=c)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    for a in qs:
        try:
            ing = timezone.localtime(a.turno_ingreso)
            f_ing, h_ing = ing.strftime("%d/%m/%Y"), ing.strftime("%H:%M")
            sal = timezone.localtime(a.turno_salida) if a.turno_salida else None
            h_sal = sal.strftime("%H:%M") if sal else "--:--"
        except:
            f_ing, h_ing, h_sal = "Error", "--:--", "--:--"

        ws.append([
            f_ing,
            f"{a.id_empleado.cedula} - {a.id_empleado.nombre_completo}",
            h_ing, h_sal,
            a.id_ubicacion.nombre if a.id_ubicacion else "N/A",
            a.observaciones or "",
            a.estado,
        ])

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    resp = HttpResponse(buffer.getvalue(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    resp["Content-Disposition"] = 'attachment; filename="asistencias.xlsx"'
    return resp

@role_required(["Administrador"])
def ver_asistencia_oficiales_export_pdf(request):
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.pagesizes import landscape, A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

    # ✅ IMPORTANTE: Usamos el mismo filtro que el Excel
    qs, _, _, _ = _build_filtered_qs_oficiales(request)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_asistencias.pdf"'

    doc = SimpleDocTemplate(response, pagesize=landscape(A4), leftMargin=20, rightMargin=20)
    story = []
    styles = getSampleStyleSheet()
    story.append(Paragraph("<b>Reporte de Asistencias</b>", styles['Title']))
    
    datos = [["Empleado", "Entrada", "Salida", "Ubicación", "Observaciones", "Estado"]]
    style_body = ParagraphStyle(name="body", fontSize=8)

    for a in qs:
        datos.append([
            f"{a.id_empleado.cedula}\n{a.id_empleado.nombre_completo}",
            timezone.localtime(a.turno_ingreso).strftime("%H:%M"),
            timezone.localtime(a.turno_salida).strftime("%H:%M") if a.turno_salida else "--:--",
            a.id_ubicacion.nombre if a.id_ubicacion else "",
            Paragraph(a.observaciones or "-", style_body),
            a.estado,
        ])

    tabla = Table(datos, colWidths=[140, 60, 60, 100, 300, 70], repeatRows=1)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e293b")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(tabla)
    doc.build(story)
    return response
