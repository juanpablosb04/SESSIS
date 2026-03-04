from django.urls import path
from . import views

app_name = "citas"

urlpatterns = [
    path("registrar/", views.registrar_citas, name="registrarCitas"),
    path("consultar/", views.consultar_citas, name="consultarCitas"),
]

