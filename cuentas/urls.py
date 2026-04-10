from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_login, name='login'),
    path('inicio/', views.inicio, name='inicio'),
    path('logout/', views.user_logout, name='logout'),
    path('recuperar/', views.recuperar_password, name='recuperar'),
    path("actualizar-contrasena/", views.cambiarContrasena, name="cambiar_contrasena"),
]
