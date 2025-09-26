from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.timezone import now
from .models import Clientes, ClientesAuditoria


def registrar_auditoria(cliente, accion, usuario, include_fk=True):
    """
    Registra un evento de auditoría de un cliente.
    - include_fk=True: guarda la relación con cliente (CREAR, MODIFICAR).
    - include_fk=False: cliente eliminado, no guarda FK (solo snapshot).
    """
    ClientesAuditoria.objects.create(
        cliente=cliente if include_fk else None,   # 👈 evitar error en DELETE
        accion=accion,
        nombre_completo=cliente.nombre_completo,
        email=cliente.email,
        cedula=cliente.cedula,
        telefono=cliente.telefono,
        residencia=cliente.residencia,
        usuario=usuario if usuario and getattr(usuario, 'is_authenticated', False) else None,
        fecha=now()
    )


@receiver(post_save, sender=Clientes)
def auditar_cliente_guardado(sender, instance, created, **kwargs):
    accion = 'CREAR' if created else 'MODIFICAR'
    usuario = getattr(instance, '_usuario', None)
    registrar_auditoria(instance, accion, usuario)


@receiver(post_delete, sender=Clientes)
def auditar_cliente_eliminado(sender, instance, **kwargs):
    usuario = getattr(instance, '_usuario', None)
    # 👇 Cliente ya no existe en la FK, solo guardamos snapshot
    registrar_auditoria(instance, 'ELIMINAR', usuario, include_fk=False)
