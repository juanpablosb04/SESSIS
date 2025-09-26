from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.timezone import now
from .models import Clientes, ClientesAuditoria


def registrar_auditoria(cliente, accion, usuario):
    ClientesAuditoria.objects.create(   # 👈 aquí corregido
        cliente=cliente,
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
    registrar_auditoria(instance, 'ELIMINAR', usuario)
