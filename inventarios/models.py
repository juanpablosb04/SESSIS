from django.db import models
from ubicaciones.models import Ubicaciones

class Inventario(models.Model):
    id_inventario = models.CharField(primary_key=True, max_length=50)
    nombre = models.CharField(max_length=150)
    descripcion = models.CharField(max_length=250, blank=True, null=True)
    estado = models.CharField(max_length=50, blank=True, null=True)
    id_ubicacion = models.ForeignKey('ubicaciones.Ubicaciones', models.DO_NOTHING, db_column='id_ubicacion')

    class Meta:
        managed = True
        db_table = 'Inventario'