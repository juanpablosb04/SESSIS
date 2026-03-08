from django.urls import path
from . import views

urlpatterns = [
    path('registroUbicaciones/', views.registro_ubicaciones_view, name='registroUbicaciones'),
    path('consultaUbicaciones/', views.consulta_ubicaciones_view, name='consultaUbicaciones'),
]