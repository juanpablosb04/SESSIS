from django.urls import path
from . import views

urlpatterns = [
    path('empleados/', views.registrar_empleado, name='empleados'),
    path('empleados/editar/<int:id_empleado>/', views.editar_empleado, name='editar_empleado'),
    path('empleados/eliminar/<int:id_empleado>/', views.eliminar_empleado, name='eliminar_empleado'),
]
