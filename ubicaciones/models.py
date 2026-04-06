from django.db import models

# Create your models here.
class Ubicaciones(models.Model):
    id_ubicacion = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    tipo = models.CharField(max_length=50, blank=True, null=True)
    direccion = models.CharField(max_length=250)
    imagen_url = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Ubicaciones'