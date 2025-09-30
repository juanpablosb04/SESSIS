from django.db import models

class Roles(models.Model):
    id_rol = models.AutoField(primary_key=True)
    nombre_rol = models.CharField(max_length=100, db_collation='Modern_Spanish_CI_AS')
    descripcion = models.CharField(max_length=250, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Roles'
