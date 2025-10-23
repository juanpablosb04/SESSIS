# asistencia/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('registrarAsistencia/', views.registrar_asistencia_view, name='registrarAsistencia'),
    path('consultarAsistencia/', views.asistencias_activas_view, name='consultarAsistencia'),
]
