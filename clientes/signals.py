# clientes/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.timezone import now
from .models import Clientes, ClientesAuditoria
from cuentas.models import Usuarios  # tu modelo real

def registrar_auditoria(cliente, accion, usuario_email, include_fk=True):
    """
    Registra auditoría en dbo.CLIENTES_AUDITORIA_TB.
    - include_fk=False si el cliente ya fue borrado (DELETE).
    """
    user_inst = None
    if usuario_email:
        user_inst = Usuarios.objects.filter(email=usuario_email).first()

    ClientesAuditoria.objects.create(
        cliente=cliente if include_fk else None,
        usuario=user_inst,                 
        usuario_email=usuario_email,       
        accion=accion,
        fecha=now(),
        nombre_completo=cliente.nombre_completo,
        email=cliente.email,
        cedula=cliente.cedula,
        telefono=cliente.telefono,
        residencia=cliente.id_ubicacion.nombre if cliente.id_ubicacion else None,
    )

@receiver(post_save, sender=Clientes)
def auditar_cliente_guardado(sender, instance, created, **kwargs):
    accion = "CREAR" if created else "MODIFICAR"
    usuario_email = getattr(instance, "_usuario_email", None)
    registrar_auditoria(instance, accion, usuario_email, include_fk=True)

@receiver(post_delete, sender=Clientes)
def auditar_cliente_eliminado(sender, instance, **kwargs):
    usuario_email = getattr(instance, "_usuario_email", None)
    registrar_auditoria(instance, "ELIMINAR", usuario_email, include_fk=False)
