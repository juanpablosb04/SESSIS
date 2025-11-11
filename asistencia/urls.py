# asistencia/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('registrarAsistencia/', views.registrar_asistencia_view, name='registrarAsistencia'),
    path('consultarAsistencia/', views.asistencias_activas_view, name='consultarAsistencia'),
    path('verAsistenciaOficiales/', views.ver_asistencia_oficiales_view, name='verAsistenciaOficiales'),
    path('verAsistenciaOficiales/export/', views.ver_asistencia_oficiales_export, name='verAsistenciaOficialesExport'),
    path('verAsistenciaOficiales/export/pdf/', views.ver_asistencia_oficiales_export_pdf, name='verAsistenciaOficialesExportPDF') # PDF
]
