# empleados/models.py
from django.db import models


class Empleado(models.Model):
    id_empleado = models.AutoField(primary_key=True)
    nombre_completo = models.CharField(max_length=200, db_collation='Modern_Spanish_CI_AS')
    email = models.CharField(unique=True, max_length=150, db_collation='Modern_Spanish_CI_AS')
    cedula = models.CharField(unique=True, max_length=50, db_collation='Modern_Spanish_CI_AS')
    telefono = models.CharField(max_length=50, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)
    direccion = models.CharField(max_length=250, db_collation='Modern_Spanish_CI_AS', blank=True, null=True)
    fecha_contratacion = models.DateField()

    class Meta:
        managed = False
        db_table = 'Empleado'


class EmpleadosAuditoria(models.Model):
    id_auditoria = models.AutoField(primary_key=True)

    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='auditorias',
        db_column='empleado_id'
    )
    # 👇 referencia por string para evitar circular import
    usuario = models.ForeignKey(
        'cuentas.Usuarios',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        db_column='usuario_id'
    )
    usuario_email = models.CharField(max_length=255, null=True, blank=True, db_column='usuario_email')

    accion = models.CharField(max_length=50)
    fecha = models.DateTimeField(auto_now_add=True)

    # snapshot
    nombre_completo = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=150, null=True, blank=True)
    cedula = models.CharField(max_length=50, null=True, blank=True)
    telefono = models.CharField(max_length=50, null=True, blank=True)
    direccion = models.CharField(max_length=250, null=True, blank=True)
    fecha_contratacion = models.DateField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'Empleados_Auditoria_TB'

    def __str__(self):
        n = self.empleado.nombre_completo if self.empleado else "Empleado eliminado"
        return f"{self.accion} - {n} ({self.fecha})"

# --HORAS EXTRAS--
class HorasExtras(models.Model):
    id_hora_extra = models.AutoField(primary_key=True)

    empleado = models.ForeignKey(
        Empleado,
        models.DO_NOTHING,
        db_column='id_empleado'
    )
    fecha = models.DateField()

    # 👇 clave: 2 decimales
    cantidad_horas = models.DecimalField(
        db_column='cantidad_horas',
        max_digits=5,
        decimal_places=2
    )

    justificacion = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        db_collation='Modern_Spanish_CI_AS'
    )
    estado = models.CharField(max_length=20, db_collation='Modern_Spanish_CI_AS')

    class Meta:
        managed = False
        db_table = 'HorasExtras'

# === Auditoría de Horas Extras ===
class HorasExtrasAuditoria(models.Model):
    id_auditoria = models.AutoField(primary_key=True)

    # vínculos (SET_NULL para no romper histórico)
    hora_extra = models.ForeignKey(
        'HorasExtras',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        db_column='hora_extra_id',
        related_name='auditorias'
    )
    empleado = models.ForeignKey(
        'Empleado',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        db_column='empleado_id'
    )

    # quién ejecutó (si no se resuelve usuario, guardamos el correo en texto)
    usuario_email = models.CharField(max_length=255, null=True, blank=True)

    # CREAR / MODIFICAR / ELIMINAR
    accion = models.CharField(max_length=50)
    fecha = models.DateTimeField(auto_now_add=True)

    # snapshot del registro
    empleado_nombre = models.CharField(max_length=255, null=True, blank=True)
    empleado_cedula = models.CharField(max_length=50, null=True, blank=True)
    fecha_registro = models.DateField(null=True, blank=True)
    cantidad_horas = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    justificacion = models.TextField(null=True, blank=True)
    estado = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'HorasExtras_Auditoria_TB'

    def __str__(self):
        return f"{self.accion} - {self.empleado_nombre or 'Empleado'} ({self.fecha})"

