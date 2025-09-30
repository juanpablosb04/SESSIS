from django.shortcuts import redirect

def role_required(allowed_roles=[]):
    """
    Decorador para restringir acceso según el rol del usuario en sesión.
    Uso: @role_required(["Administrador"])
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            rol = request.session.get("usuario_rol", None)
            if rol in allowed_roles:
                return view_func(request, *args, **kwargs)
            return redirect("sin_permiso")
        return wrapper
    return decorator
