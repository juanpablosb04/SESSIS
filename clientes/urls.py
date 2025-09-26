# clientes/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.clientes_view, name='clientes'),
    path('<int:cliente_id>/auditoria/', views.auditoria_cliente, name='auditoria_cliente'),
]
