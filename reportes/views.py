from datetime import datetime
from io import BytesIO

from django.contrib import messages
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from config.decorators import role_required
from empleados.models import Empleado
from .models import ReporteIncidente

from django.core.paginator import Paginator
from datetime import datetime


# -------------------- helpers --------------------
def _empleado_actual(request):
    """
    Obtiene el empleado asociado al email guardado en sesión.
    """
    email = request.session.get("usuario_email")
    if not email:
        return None
    return Empleado.objects.filter(email=email).first()


# -------------------- vistas compartidas --------------------
@role_required(["Administrador", "Oficial"])
def ver_foto_incidente_view(request, id_reporte: int):
    """
    Sirve la imagen del incidente de forma segura.
    - Oficiales: solo su propia foto.
    - Administradores: todas.
    """
    rep = get_object_or_404(ReporteIncidente, pk=id_reporte)

    # Si el rol es Oficial, validamos que la foto sea suya
    try:
        if getattr(request.user, "rol", None) == "Oficial":
            emp = _empleado_actual(request)
            if not emp or rep.id_empleado_id != emp.id_empleado:
                raise Http404("No autorizado.")
    except Exception:
        emp = _empleado_actual(request)
        if not emp or rep.id_empleado_id != emp.id_empleado:
            raise Http404("No autorizado.")

    if not rep.foto:
        raise Http404("Sin foto.")

    # Deja que el navegador detecte el tipo de contenido (image/*)
    return FileResponse(rep.foto.open("rb"))


@role_required(["Oficial", "Administrador"])
def reporte_incidentes_view(request):
    """
    Registrar incidentes y mostrar listado con paginación.
    """
    empleado = _empleado_actual(request)
    if not empleado:
        messages.error(request, "No se encontró el empleado asociado a la sesión.")
        return redirect("inicio")

    # -------------------- POST (crear reporte) --------------------
    if request.method == "POST":
        fecha_evento = request.POST.get("fecha_evento")
        if fecha_evento:
            try:
                fecha_evento = datetime.strptime(fecha_evento, "%Y-%m-%d").date()
            except ValueError:
                fecha_evento = timezone.now().date()
        else:
            fecha_evento = timezone.now().date()

        categoria = request.POST.get("categoria") or ""
        descripcion = request.POST.get("descripcion") or ""
        foto = request.FILES.get("foto")

        ReporteIncidente.objects.create(
            id_empleado=empleado,
            fecha_evento=fecha_evento,
            categoria=categoria,
            descripcion=descripcion,
            foto=foto,
        )

        messages.success(
            request,
            "Incidente registrado correctamente.",
            extra_tags="crear alert-success"
        )
        return redirect("reporteIncidentes")

    # -------------------- LISTADO CON PAGINACIÓN --------------------
    reportes_qs = (
        ReporteIncidente.objects
        .filter(id_empleado=empleado)
        .order_by("-fecha_evento", "-id_reporte")
    )

    paginator = Paginator(reportes_qs, 5)  # <- cantidad por página
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "Empleado/reporteIncidentes.html",
        {
            "page_obj": page_obj,
            "reportes": page_obj.object_list,  # únicamente los visibles en la página
        },
    )

# -------------------- panel administrador --------------------
@role_required(["Administrador"])
def reportes_incidentes_admin_view(request):

    qs = (
        ReporteIncidente.objects
        .select_related("id_empleado")
        .order_by("-fecha_evento", "-id_reporte")
    )

    # Parámetros GET
    emp_id = (request.GET.get("empleado") or "").strip()
    f_ini = (request.GET.get("ini") or "").strip()
    f_fin = (request.GET.get("fin") or "").strip()

    if emp_id:
        qs = qs.filter(id_empleado_id=emp_id)

    if f_ini:
        try:
            fi = datetime.strptime(f_ini, "%Y-%m-%d").date()
            qs = qs.filter(fecha_evento__gte=fi)
        except ValueError:
            pass

    if f_fin:
        try:
            ff = datetime.strptime(f_fin, "%Y-%m-%d").date()
            qs = qs.filter(fecha_evento__lte=ff)
        except ValueError:
            pass

    # 🔥 PAGINACIÓN
    paginator = Paginator(qs, 5)  # 20 por página
    page_number = request.GET.get("page")
    reportes_pag = paginator.get_page(page_number)

    context = {
        "reportes": reportes_pag,   # aquí ya enviamos página, no queryset normal
        "empleados": Empleado.objects.all().order_by("nombre_completo"),
        "paginator": paginator,
    }

    return render(request, "Empleado/reporteIncidentesAdmin.html", context)


@role_required(["Administrador"])
def reportes_incidentes_admin_pdf(request):
    """
    Exporta a PDF la vista ADMIN (con los mismos filtros que la HTML).

    Parámetros GET:
      - empleado
      - ini
      - fin
    """
    try:
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
        from reportlab.lib.styles import getSampleStyleSheet
    except Exception:
        return HttpResponse("Falta instalar reportlab: pip install reportlab", status=500)

    qs = (
        ReporteIncidente.objects
        .select_related("id_empleado")
        .order_by("-fecha_evento", "-id_reporte")
    )

    emp_id = (request.GET.get("empleado") or "").strip()
    f_ini = (request.GET.get("ini") or "").strip()
    f_fin = (request.GET.get("fin") or "").strip()

    if emp_id:
        qs = qs.filter(id_empleado_id=emp_id)

    if f_ini:
        try:
            fi = datetime.strptime(f_ini, "%Y-%m-%d").date()
            qs = qs.filter(fecha_evento__gte=fi)
        except ValueError:
            pass

    if f_fin:
        try:
            ff = datetime.strptime(f_fin, "%Y-%m-%d").date()
            qs = qs.filter(fecha_evento__lte=ff)
        except ValueError:
            pass

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=20,
        rightMargin=20,
        topMargin=20,
        bottomMargin=20,
    )
    styles = getSampleStyleSheet()
    elems = [Paragraph("Reporte de Incidentes (ADMIN)", styles["Title"]), Spacer(1, 10)]

    # Encabezados
    data = [["Fecha", "Empleado", "Categoría", "Descripción", "Foto"]]

    for r in qs:
        fecha = r.fecha_evento.strftime("%d/%m/%Y") if r.fecha_evento else "-"
        empleado_txt = f"{getattr(r.id_empleado, 'cedula', '')} - {getattr(r.id_empleado, 'nombre_completo', '')}"
        desc = (r.descripcion or "")[:150]

        # Intentar miniatura
        foto_cell = "—"
        if r.foto:
            try:
                img = Image(r.foto.path, width=60, height=45)  # pequeño thumbnail
                foto_cell = img
            except Exception:
                foto_cell = "img"

        data.append([fecha, empleado_txt, r.categoria or "-", desc, foto_cell])

    table = Table(data, colWidths=[80, 220, 120, 360, 70], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#374151")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("TEXTCOLOR", (0, 1), (-1, -1), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#4b5563")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#111827"), colors.HexColor("#1f2937")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))

    elems.append(table)
    doc.build(elems)

    pdf = buffer.getvalue()
    buffer.close()
    resp = HttpResponse(pdf, content_type="application/pdf")
    resp["Content-Disposition"] = 'attachment; filename="incidentes_admin.pdf"'
    return resp

