# empleados/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Empleado, EmpleadosAuditoria
from cuentas.models import Usuarios  # si no usas esta FK, puedes quitarlo


def registrar_auditoria(empleado: Empleado, accion: str, usuario_email: str | None, include_fk: bool = True):
    """
    Crea un registro en dbo.Empleados_Auditoria_TB.
    - include_fk=False cuando el empleado ya fue borrado (DELETE).
    """
    usuario_inst = None
    if usuario_email:
        # No levantamos error si no existe el usuario; es opcional
        usuario_inst = Usuarios.objects.filter(email=usuario_email).first()

    EmpleadosAuditoria.objects.create(
        empleado=empleado if include_fk else None,
        usuario=usuario_inst,
        usuario_email=usuario_email,
        accion=accion,
        # 'fecha' se llena con auto_now_add en el modelo
        # ----- snapshot -----
        nombre_completo=empleado.nombre_completo,
        email=empleado.email,
        cedula=empleado.cedula,
        telefono=empleado.telefono,
        direccion=empleado.direccion,
        fecha_contratacion=empleado.fecha_contratacion,
    )


@receiver(post_save, sender=Empleado)
def auditar_empleado_guardado(sender, instance: Empleado, created: bool, **kwargs):
    accion = "CREAR" if created else "MODIFICAR"
    usuario_email = getattr(instance, "_usuario_email", None)  # la vista lo setea antes de save()
    registrar_auditoria(instance, accion, usuario_email, include_fk=True)


@receiver(post_delete, sender=Empleado)
def auditar_empleado_eliminado(sender, instance: Empleado, **kwargs):
    usuario_email = getattr(instance, "_usuario_email", None)  # la vista lo setea antes de delete()
    registrar_auditoria(instance, "ELIMINAR", usuario_email, include_fk=False)
