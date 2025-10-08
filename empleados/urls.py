# empleados/urls.py
from django.urls import path
from .views import empleados_view, auditoria_empleado

urlpatterns = [
    path('', empleados_view, name='empleados'),
    path('auditoria/<int:empleado_id>/', auditoria_empleado, name='auditoria_empleado'),
]
