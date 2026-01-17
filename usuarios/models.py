from django.db import models
from empleados.models import Empleado

# Modelo Usuario
class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    id_empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, db_column='id_empleado')
    id_rol = models.IntegerField()
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=100)
    estado = models.CharField(max_length=50)
    password_temp = models.BooleanField(default=True)

    class Meta:
        db_table = 'Usuarios'

    def __str__(self):
        return self.email

# Modelo Auditoría
class AuditoriaUsuario(models.Model):
    id_auditoria = models.AutoField(primary_key=True)
    usuario_afectado = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='auditoria_afectado'
    )
    usuario_accion = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='auditoria_accion'
    )
    accion = models.CharField(max_length=50)
    fecha = models.DateTimeField(auto_now_add=True)
    id_empleado = models.IntegerField(null=True)  # Solo guarda el ID, no FK
    id_rol = models.IntegerField(null=True)      # Solo guarda el ID, no FK
    email = models.CharField(max_length=150, null=True)
    estado = models.CharField(max_length=50, null=True)

    class Meta:
        db_table = 'USUARIOS_AUDITORIA_TB'
        ordering = ['-fecha']

    # Propiedades para mostrar nombres sin tocar la DB
    @property
    def empleado(self):
        try:
            return self.usuario_afectado.id_empleado.nombre_completo
        except:
            return "Desconocido"

    @property
    def nombre_rol(self):
        roles = {1: "Administrador", 2: "Oficial"}
        try:
            return roles.get(self.usuario_afectado.id_rol, "Desconocido")
        except:
            return "Desconocido"

    @property
    def usuario_nombre(self):
        try:
            if self.usuario_accion:
                return self.usuario_accion.id_empleado.nombre_completo
            return "Sistema"
        except:
            return "Desconocido"

    def __str__(self):
        return f"{self.accion} - {self.usuario_afectado}"
