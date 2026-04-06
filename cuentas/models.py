from django.db import models
from empleados.models import Empleado
from roles.models import Roles

class Usuarios(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    id_empleado = models.ForeignKey(Empleado, models.DO_NOTHING, db_column='id_empleado')
    id_rol = models.ForeignKey(Roles, models.DO_NOTHING, db_column='id_rol')
    email = models.CharField(unique=True, max_length=150)
    password = models.CharField(max_length=150)
    estado = models.CharField(max_length=50, blank=True, null=True)
    password_temp = models.BooleanField(default=True)

    class Meta:
        managed = True
