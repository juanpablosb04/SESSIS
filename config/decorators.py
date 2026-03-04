from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def role_required(allowed_roles=None):

    if allowed_roles is None:
        allowed_roles = []

    def decorator(view_func):

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            # Verificar sesión activa
            if "usuario_id" not in request.session:
                return redirect("login")

            rol = request.session.get("usuario_rol")

            if rol not in allowed_roles:
                messages.error(request, "No tienes permisos para acceder a esta sección.")
                return redirect("sin_permiso")

            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator