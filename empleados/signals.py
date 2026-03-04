# empleados/signals.py
from __future__ import annotations

from django.apps import apps
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import (
    Empleado,
    EmpleadosAuditoria,
    HorasExtras,
    HorasExtrasAuditoria,
)


# =========================
# Utilidades
# =========================
def _get_usuario_instance_by_email(usuario_email: str | None):
    """
    Resuelve la FK a cuentas.Usuarios de forma perezosa para
    evitar importaciones circulares. Devuelve None si no existe.
    """
    if not usuario_email:
        return None
    Usuarios = apps.get_model('cuentas', 'Usuarios')  # lazy import
    return Usuarios.objects.filter(email=usuario_email).first()


# =========================
# Auditoría: Empleado
# =========================
def registrar_auditoria_empleado(
    empleado: Empleado,
    accion: str,
    usuario_email: str | None,
    include_fk: bool = True,
):
    """
    Crea un registro en dbo.Empleados_Auditoria_TB.
    - include_fk=False cuando el empleado ya fue borrado (DELETE).
    """
    usuario_inst = _get_usuario_instance_by_email(usuario_email)

    EmpleadosAuditoria.objects.create(
        empleado=empleado if include_fk else None,
        usuario=usuario_inst,
        usuario_email=usuario_email,
        accion=accion,
        # fecha -> auto_now_add en el modelo
        # snapshot
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
    registrar_auditoria_empleado(instance, accion, usuario_email, include_fk=True)


@receiver(post_delete, sender=Empleado)
def auditar_empleado_eliminado(sender, instance: Empleado, **kwargs):
    usuario_email = getattr(instance, "_usuario_email", None)  # la vista lo setea antes de delete()
    registrar_auditoria_empleado(instance, "ELIMINAR", usuario_email, include_fk=False)


# =========================
# Auditoría: Horas Extras
# =========================
def _auditar_horas_extras(instancia: HorasExtras, accion: str):
    """
    Inserta una fila en dbo.HorasExtras_Auditoria_TB con snapshot del registro.
    El correo del ejecutor se pasa desde la vista en _usuario_email.
    """
    empleado = instancia.empleado  # FK Empleado (puede existir o no según el histórico deseado)
    HorasExtrasAuditoria.objects.create(
        hora_extra=instancia,
        empleado=empleado,
        usuario_email=getattr(instancia, "_usuario_email", None),

        accion=accion,
        # fecha -> auto_now_add en el modelo

        # snapshot
        empleado_nombre=getattr(empleado, "nombre_completo", None),
        empleado_cedula=getattr(empleado, "cedula", None),
        fecha_registro=instancia.fecha,
        cantidad_horas=instancia.cantidad_horas,
        justificacion=instancia.justificacion,
        estado=instancia.estado,
    )


@receiver(post_save, sender=HorasExtras)
def horas_extras_post_save(sender, instance: HorasExtras, created: bool, **kwargs):
    _auditar_horas_extras(instance, "CREAR" if created else "MODIFICAR")


@receiver(post_delete, sender=HorasExtras)
def horas_extras_post_delete(sender, instance: HorasExtras, **kwargs):
    _auditar_horas_extras(instance, "ELIMINAR")

