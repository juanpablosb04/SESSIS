# clientes/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now

from .models import Clientes, ClientesAuditoria


def _get_usuario_by_email(usuario_email):
    """
    Busca el usuario por email en tu modelo real.
    Lo importamos dentro de la función para evitar problemas de importación/ciclos.
    """
    if not usuario_email:
        return None
    try:
        from cuentas.models import Usuarios  # tu modelo real de usuarios
    except Exception:
        return None
    return Usuarios.objects.filter(email=usuario_email).first()


def registrar_auditoria(cliente, accion, usuario_email, include_fk=True):
    """
    Registra en CLIENTES_AUDITORIA_TB.
    - include_fk=True: guarda FK al cliente (CREAR/MODIFICAR/CAMBIAR_ESTADO).
      (Si algún día quisieras registrar un borrado lógico sin FK, podrías pasar False.)
    """
    user_inst = _get_usuario_by_email(usuario_email)

    ClientesAuditoria.objects.create(
        cliente=cliente if include_fk else None,
        usuario=user_inst,
        usuario_email=usuario_email,
        accion=accion,
        fecha=now(),

        # Snapshot del cliente en el momento de la acción
        nombre_completo=cliente.nombre_completo,
        email=cliente.email,
        cedula=cliente.cedula,
        telefono=cliente.telefono,
        # Guardamos el nombre de la ubicación como “residencia” (tal como venías haciéndolo)
        residencia=(cliente.id_ubicacion.nombre if getattr(cliente, "id_ubicacion", None) else None),
    )


@receiver(post_save, sender=Clientes)
def auditar_cliente_guardado(sender, instance, created, **kwargs):
    """
    - CREAR si es nuevo.
    - Si en la vista seteas `instance._accion_audit = "CAMBIAR_ESTADO"`, se usa eso.
    - En cualquier otro update normal: MODIFICAR.
    """
    usuario_email = getattr(instance, "_usuario_email", None)

    if created:
        accion = "CREAR"
    else:
        accion = getattr(instance, "_accion_audit", None) or "MODIFICAR"

    registrar_auditoria(instance, accion, usuario_email, include_fk=True)
