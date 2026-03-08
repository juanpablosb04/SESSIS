from django.db import models
from ubicaciones.models import Ubicaciones

class Inventario(models.Model):
    id_inventario = models.CharField(primary_key=True, max_length=50, db_collation='Modern_Spanish_CI_AS')
    nombre = models.CharField(max_length=150, db_collation='Modern_Spanish_CI_AS')
    descripcion = models.CharField(max_length=250, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)
    estado = models.CharField(max_length=50, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)
    id_ubicacion = models.ForeignKey('ubicaciones.Ubicaciones', models.DO_NOTHING, db_column='id_ubicacion')

    class Meta:
        managed = False
        db_table = 'Inventario'