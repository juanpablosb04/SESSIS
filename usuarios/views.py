from django.shortcuts import render, get_object_or_404, redirect
from .models import Usuario, AuditoriaUsuario
from config.decorators import role_required
from empleados.models import Empleado

# Lista de roles
ROLES = [
    (1, "Administrador"),
    (2, "Oficial")
]

# ========================
# LISTA, CREAR, EDITAR, ELIMINAR USUARIOS
# ========================
@role_required(["Administrador"])
def lista_usuarios(request):
    if request.method == "POST":
        action = request.POST.get("action")
        usuario_actual = None  # Aquí puedes poner el usuario logueado si tienes auth

        if action == "crear":
            usuario = Usuario.objects.create(
                id_empleado_id=int(request.POST["id_empleado"]),
                id_rol=int(request.POST["id_rol"]),
                email=request.POST["email"],
                password=request.POST["password"],
                estado=request.POST.get("estado", "Activo")
            )

            # Registrar auditoría
            AuditoriaUsuario.objects.create(
                usuario_afectado=usuario,
                usuario_accion=usuario_actual,
                accion="CREAR",
                id_empleado=usuario.id_empleado.id_empleado,
                id_rol=usuario.id_rol,
                email=usuario.email,
                estado=usuario.estado
            )

        elif action == "editar":
            usuario = get_object_or_404(Usuario, id_usuario=request.POST["usuario_id"])
            usuario.id_empleado_id = int(request.POST["id_empleado"])
            usuario.id_rol = int(request.POST["id_rol"])
            usuario.email = request.POST["email"]

            # 🔹 Mantener contraseña si el input está vacío
            nueva_password = request.POST["password"]
            if nueva_password.strip():  # Solo actualiza si tiene valor
                usuario.password = nueva_password

            usuario.estado = request.POST.get("estado", "")
            usuario.save()

            # Registrar auditoría
            AuditoriaUsuario.objects.create(
                usuario_afectado=usuario,
                usuario_accion=usuario_actual,
                accion="EDITAR",
                id_empleado=usuario.id_empleado.id_empleado,
                id_rol=usuario.id_rol,
                email=usuario.email,
                estado=usuario.estado
            )

        elif action == "eliminar":
            usuario = get_object_or_404(Usuario, id_usuario=request.POST["usuario_id"])
            # Registrar auditoría antes de eliminar
            AuditoriaUsuario.objects.create(
                usuario_afectado=usuario,
                usuario_accion=usuario_actual,
                accion="ELIMINAR",
                id_empleado=usuario.id_empleado.id_empleado,
                id_rol=usuario.id_rol,
                email=usuario.email,
                estado=usuario.estado
            )
            usuario.delete()

        return redirect("lista_usuarios")

    usuarios = Usuario.objects.all()
    empleados = Empleado.objects.all()
    return render(
        request,
        "usuarios/usuarios.html",
        {"usuarios": usuarios, "empleados": empleados, "roles": ROLES}
    )


# ========================
# AUDITORÍA DE UN USUARIO
# ========================
@role_required(["Administrador"])
def auditoria_usuario(request, id_usuario):
    usuario = get_object_or_404(Usuario, id_usuario=id_usuario)
    auditoria = AuditoriaUsuario.objects.filter(usuario_afectado=usuario).order_by('-fecha')
    return render(
        request,
        "usuarios/auditoria_usuario.html",
        {"usuario": usuario, "auditoria": auditoria}
    )
