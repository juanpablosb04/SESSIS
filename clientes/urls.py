# clientes/urls.py
from django.urls import path
from .views import clientes_view, auditoria_cliente

urlpatterns = [
    path("", clientes_view, name="clientes"),
    path("auditoria/<int:cliente_id>/", auditoria_cliente, name="auditoria_cliente"),
]

