# empleados/urls.py
from django.urls import path
from .views import empleados_view, auditoria_empleado
from . import views

urlpatterns = [
    path('', empleados_view, name='empleados'),
    path('auditoria/<int:empleado_id>/', auditoria_empleado, name='auditoria_empleado'),
    path("horas-extras/", views.horas_extras_admin, name="horasExtras"),
    path( "auditoria/horas-extras/<int:empleado_id>/", views.auditoria_horas_extras_por_empleado, 
         name="auditoria_horas_extras_por_empleado", ),
    path('mis-horas-extras/', views.consultar_horas_extras_oficial, name='consultarHorasExtras'),
    path('verAsistenciaOficiales/', views.ver_asistencia_Empleados, name='verAsistenciaOficiales'),
]
