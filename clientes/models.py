from django.db import models
from cuentas.models import Usuarios   # tu modelo de usuario personalizado
# -------------------------------
# Modelo principal de Clientes
# -------------------------------
class Clientes(models.Model):
    id_cliente = models.AutoField(primary_key=True)  # Llave primaria autoincremental
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
    residencia = models.CharField(
        max_length=200,
        db_collation='Modern_Spanish_CI_AS',
        blank=True,
        null=True
    )

    class Meta:
        managed = True
        db_table = 'Clientes'  # Nombre exacto de la tabla en SQL Server

    def __str__(self):
        return f"{self.nombre_completo} ({self.cedula})"


# -------------------------------
# Modelo de Auditoría de Clientes
# -------------------------------
class ClientesAuditoria(models.Model):
    id_auditoria = models.AutoField(primary_key=True)

    # 🔹 Ahora usamos SET_NULL para no romper cuando se elimina un cliente
    cliente = models.ForeignKey(
        Clientes,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="auditorias",
        db_column="cliente_id"
    )

    usuario = models.ForeignKey(
        Usuarios,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="usuario_id"
    )  

    accion = models.CharField(max_length=50)  # CREAR, MODIFICAR, ELIMINAR
    fecha = models.DateTimeField(auto_now_add=True)

    # Snapshot de datos del cliente en el momento de la acción
    nombre_completo = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    cedula = models.CharField(max_length=20, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    residencia = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = "CLIENTES_AUDITORIA_TB"

    def __str__(self):
        # 👇 Si cliente fue borrado, evitamos error con "Desconocido"
        cliente_nombre = self.cliente.nombre_completo if self.cliente else "Cliente eliminado"
        return f"{self.accion} - {cliente_nombre} ({self.fecha})"
