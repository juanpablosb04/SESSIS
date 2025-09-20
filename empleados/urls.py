from django.urls import path
from . import views

urlpatterns = [
    path('empleados/', views.registrar_empleado, name='empleados'),
]
