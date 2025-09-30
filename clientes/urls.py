# Clientes/urls.py
from django.urls import path
from .views import clientes_view, auditoria_cliente  # 👈 import explícito

urlpatterns = [
    path('', clientes_view, name='clientes'),
    path('auditoria/<int:cliente_id>/', auditoria_cliente, name='auditoria_cliente'),
]
