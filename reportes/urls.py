from django.urls import path
from . import views

urlpatterns = [
    # Oficial/Admin (formulario + lista propia)
    path("incidentes/", views.reporte_incidentes_view, name="reporteIncidentes"),

    # Ver foto (segura, sin exponer URL directa del archivo)
    path("incidentes/foto/<int:id_reporte>/", views.ver_foto_incidente_view, name="verFotoIncidente"),

    # Panel ADMIN (lista con filtros)
    path("incidentes/admin/", views.reportes_incidentes_admin_view, name="reportesIncidentesAdmin"),

    # Exportación PDF para ADMIN
    path("incidentes/admin/pdf/", views.reportes_incidentes_admin_pdf, name="reportesIncidentesAdminPDF"),
]
