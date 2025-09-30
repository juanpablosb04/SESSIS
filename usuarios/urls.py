from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_usuarios, name='lista_usuarios'),
    path('auditoria/<int:id_usuario>/', views.auditoria_usuario, name='auditoria_usuario'),
]
