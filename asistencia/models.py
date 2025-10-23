from django.db import models

# Create your models here.
class Asistencia(models.Model):
    id_asistencia = models.AutoField(primary_key=True)
    id_empleado = models.ForeignKey('empleados.Empleado', on_delete=models.DO_NOTHING, db_column='id_empleado')
    turno_ingreso = models.DateTimeField()
    turno_salida = models.DateTimeField(blank=True, null=True)
    id_ubicacion = models.ForeignKey('ubicaciones.Ubicaciones', on_delete=models.DO_NOTHING, db_column='id_ubicacion')
    observaciones = models.CharField(max_length=250, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)
    estado = models.CharField(max_length=20, default='En curso')

    class Meta:
        managed = False
        db_table = 'Asistencia'