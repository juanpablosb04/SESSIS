# clientes/models.py
from django.db import models
from cuentas.models import Usuarios
from ubicaciones.models import Ubicaciones


# ==========================
#  Tabla: dbo.Clientes (SQL Server existente)
# ==========================
class Clientes(models.Model):
    id_cliente = models.AutoField(primary_key=True)

    nombre_completo = models.CharField(
        max_length=200,
        db_collation='Modern_Spanish_CI_AS'
    )
    email = models.CharField(
        unique=True,
        max_length=150,
        db_collation='Modern_Spanish_CI_AS'
    )
    cedula = models.CharField(
        unique=True,
        max_length=50,
        db_collation='Modern_Spanish_CI_AS'
    )
    telefono = models.CharField(
        max_length=50,
        db_collation='Modern_Spanish_CI_AS',
        blank=True,
        null=True
    )

    # FK Ubicación (nullable)
    id_ubicacion = models.ForeignKey(
        Ubicaciones,
        on_delete=models.DO_NOTHING,
        db_column='id_ubicacion',
        blank=True,
        null=True
    )

    # Baja lógica -> ahora mapea al campo BIT [estado] en SQL Server
    estado = models.BooleanField(db_column='estado', default=True)

    class Meta:
        managed = False                # No crear/alterar la tabla desde Django
        db_table = 'Clientes'          # Nombre exacto en SQL Server

    def __str__(self) -> str:
        return f"{self.nombre_completo} ({self.cedula})"

    @property
    def estado_text(self) -> str:
        """Conveniencia para mostrar 'Activo'/'Inactivo' en templates."""
        return "Activo" if self.estado else "Inactivo"


# ==========================
#  Tabla: dbo.CLIENTES_AUDITORIA_TB (SQL Server existente)
# ==========================
class ClientesAuditoria(models.Model):
    id_auditoria = models.AutoField(primary_key=True)

    # FK al cliente: SET_NULL para no romper auditorías antiguas
    cliente = models.ForeignKey(
        Clientes,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='auditorias',
        db_column='cliente_id'
    )

    # FK al usuario ejecutor (si existe)
    usuario = models.ForeignKey(
        Usuarios,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='usuario_id'
    )

    # También guardamos el correo en texto plano por si la FK no resuelve
    usuario_email = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_column='usuario_email'
    )

    # CREAR / MODIFICAR / CAMBIAR_ESTADO / (ELIMINAR si quedó histórico)
    accion = models.CharField(max_length=50)
    fecha = models.DateTimeField(auto_now_add=True)

    # Snapshot de los datos del cliente al momento de la acción
    nombre_completo = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=150, null=True, blank=True)
    cedula = models.CharField(max_length=50, null=True, blank=True)
    telefono = models.CharField(max_length=50, null=True, blank=True)
    # Guardamos el nombre de la ubicación como “residencia”
    residencia = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'Clientes_Auditoria_TB'   # tabla de auditoria

    def __str__(self) -> str:
        nombre = self.cliente.nombre_completo if self.cliente else "Cliente eliminado"
        return f"{self.accion} - {nombre} ({self.fecha})"



