from django.db import models

# Create your models here.
class Ubicaciones(models.Model):
    id_ubicacion = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200, db_collation='Modern_Spanish_CI_AS')
    tipo = models.CharField(max_length=50, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)
    direccion = models.CharField(max_length=250, db_collation='Modern_Spanish_CI_AS')
    imagen_url = models.CharField(max_length=500, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Ubicaciones'