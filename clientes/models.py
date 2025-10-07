from django.db import models
from cuentas.models import Usuarios
from ubicaciones.models import Ubicaciones

class Clientes(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    nombre_completo = models.CharField(max_length=200, db_collation='Modern_Spanish_CI_AS')
    email = models.CharField(unique=True, max_length=150, db_collation='Modern_Spanish_CI_AS')
    cedula = models.CharField(unique=True, max_length=50, db_collation='Modern_Spanish_CI_AS')
    telefono = models.CharField(max_length=50, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)
    id_ubicacion = models.ForeignKey('ubicaciones.Ubicaciones', models.DO_NOTHING, db_column='id_ubicacion', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Clientes'

    def __str__(self):
        return f"{self.nombre_completo} ({self.cedula})"


class ClientesAuditoria(models.Model):
    id_auditoria = models.AutoField(primary_key=True)

    cliente = models.ForeignKey(
        Clientes,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='auditorias',
        db_column='cliente_id'
    )
    usuario = models.ForeignKey(
        Usuarios,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        db_column='usuario_id'
    )

    # además guardas el correo plano
    usuario_email = models.CharField(max_length=255, null=True, blank=True, db_column='usuario_email')

    accion = models.CharField(max_length=50)
    fecha = models.DateTimeField(auto_now_add=True)

    # snapshot
    nombre_completo = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=150, null=True, blank=True)
    cedula = models.CharField(max_length=50, null=True, blank=True)
    telefono = models.CharField(max_length=50, null=True, blank=True)
    residencia = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'Clientes_Auditoria_TB'

    def __str__(self):
        n = self.cliente.nombre_completo if self.cliente else "Cliente eliminado"
        return f"{self.accion} - {n} ({self.fecha})"
