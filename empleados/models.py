from django.db import models


class Empleado(models.Model):
    id_empleado = models.AutoField(primary_key=True)
    nombre_completo = models.CharField(max_length=200, db_collation='Modern_Spanish_CI_AS')
    email = models.CharField(unique=True, max_length=150, db_collation='Modern_Spanish_CI_AS')
    cedula = models.CharField(unique=True, max_length=50, db_collation='Modern_Spanish_CI_AS')
    telefono = models.CharField(max_length=50, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)
    direccion = models.CharField(max_length=250, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)
    fecha_contratacion = models.DateField()

    class Meta:
        managed = False
        db_table = 'Empleado'