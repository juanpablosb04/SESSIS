from django.db import models
from empleados.models import Empleado  # Importamos modelo Empleado

# Modelo de Usuario
class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    id_empleado = models.ForeignKey(
        Empleado,
        on_delete=models.CASCADE,
        db_column='id_empleado'  # 🔹 Nombre exacto en SQL Server
    )
    id_rol = models.IntegerField()
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=100)
    estado = models.CharField(max_length=50)

    class Meta:
        db_table = 'Usuarios'  # Tabla exacta en SQL Server

    def __str__(self):
        return self.email


# Modelo de Auditoría
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
    id_empleado = models.IntegerField(null=True)
    id_rol = models.IntegerField(null=True)
    email = models.CharField(max_length=150, null=True)
    estado = models.CharField(max_length=50, null=True)

    class Meta:
        db_table = 'Usuarios_Auditoria_TB'
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.accion} - {self.usuario_afectado}"
