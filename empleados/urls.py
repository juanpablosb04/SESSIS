from django.urls import path
from . import views

urlpatterns = [
    path('', views.empleados_view, name='empleados'),  # vista principal, lista y crear
]
