from django.db import models

class Roles(models.Model):
    id_rol = models.AutoField(primary_key=True)
    nombre_rol = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=250, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Roles'
