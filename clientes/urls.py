# Clientes/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Lista + crear + editar + eliminar clientes
    path('', views.clientes_view, name='clientes'),

    # Auditoría de un cliente específico
    path('auditoria/<int:cliente_id>/', views.auditoria_cliente, name='auditoria_cliente'),
]
