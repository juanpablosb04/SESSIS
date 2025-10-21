from django.db import models
from clientes.models import Clientes

class Cita(models.Model):
    id_cita = models.AutoField(primary_key=True)
    cliente = models.ForeignKey(Clientes, on_delete=models.CASCADE, db_column='id_cliente')
    fecha_cita = models.DateField(db_column='fecha_cita')
    hora_inicio = models.TimeField(db_column='hora_inicio')
    hora_finalizacion = models.TimeField(db_column='hora_finalizacion', null=True, blank=True)
    motivo = models.CharField(max_length=200, db_column='motivo', null=True, blank=True)
    descripcion = models.TextField(db_column='descripcion', null=True, blank=True)  # <-- NUEVO CAMPO

    class Meta:
        db_table = 'Citas'
        managed = False

    def __str__(self):
        return f"Cita con {self.cliente} el {self.fecha_cita} a las {self.hora_inicio}"
