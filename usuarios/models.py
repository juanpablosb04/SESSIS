from django.db import models
from empleados.models import Empleado
import roles

class AuditoriaUsuario(models.Model):
    id_auditoria = models.AutoField(primary_key=True)
    
    # Apuntamos directamente al modelo de la otra APP
    usuario_afectado = models.ForeignKey(
        'cuentas.Usuarios', 
        on_delete=models.SET_NULL,
        null=True,
        related_name='auditoria_afectado'
    )
    usuario_accion = models.ForeignKey(
        'cuentas.Usuarios',
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
        db_table = 'USUARIOS_AUDITORIA_TB'
        ordering = ['-fecha']

    # Propiedades (se mantienen igual, Django las resolverá desde 'cuentas.Usuarios')
    @property
    def empleado(self):
        try:
            return self.usuario_afectado.id_empleado.nombre_completo
        except:
            return "Desconocido"

    @property
    def nombre_rol(self):
    # Diccionario para traducir el número a texto
        roles = {1: "Administrador", 2: "Oficial"}
    
    # Buscamos directamente el número guardado en la auditoría
        return roles.get(self.id_rol, "Desconocido")

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
