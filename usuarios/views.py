from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Usuario, AuditoriaUsuario
from django.core.paginator import Paginator
from config.decorators import role_required
from empleados.models import Empleado
from django.contrib.auth.hashers import make_password


# Diccionario de roles
ROLES = {
    1: "Administrador",
    2: "Oficial"
}

# ========================
# LISTA, CREAR, EDITAR, ELIMINAR USUARIOS
# ========================
@role_required(["Administrador"])
def lista_usuarios(request):
    if request.method == "POST":
        action = request.POST.get("action")
        usuario_actual = None  # Usuario admin logueado si lo deseas

        # ============================================
        # CREAR USUARIO
        # ============================================
        if action == "crear":
            usuario = Usuario.objects.create(
                id_empleado_id=int(request.POST["id_empleado"]),
                id_rol=int(request.POST["id_rol"]),
                email=request.POST["email"],
                password=make_password(request.POST["password"]),   # ← ENCRIPTAR
                estado=request.POST.get("estado", "Activo"),
                password_temp=True  # ← REQUIERE CAMBIO AL INICIAR
            )

            AuditoriaUsuario.objects.create(
                usuario_afectado=usuario,
                usuario_accion=usuario_actual,
                accion="CREAR",
                id_empleado=usuario.id_empleado.id_empleado,
                id_rol=usuario.id_rol,
                email=usuario.email,
                estado=usuario.estado
            )

            messages.success(request, "✅ Usuario creado correctamente.", extra_tags='crear')

        # ============================================
        # EDITAR USUARIO
        # ============================================
        elif action == "editar":
            usuario = get_object_or_404(Usuario, id_usuario=request.POST["usuario_id"])

            usuario.id_empleado_id = int(request.POST["id_empleado"])
            usuario.id_rol = int(request.POST["id_rol"])
            usuario.email = request.POST["email"]

            nueva_password = request.POST.get("password")


            if nueva_password and nueva_password != "********":
                usuario.password = make_password(nueva_password)

            usuario.estado = request.POST.get("estado", "")
            usuario.save()

            AuditoriaUsuario.objects.create(
                usuario_afectado=usuario,
                usuario_accion=usuario_actual,
                accion="EDITAR",
                id_empleado=usuario.id_empleado.id_empleado,
                id_rol=usuario.id_rol,
                email=usuario.email,
                estado=usuario.estado
            )

            messages.success(request, "✏️ Usuario editado correctamente.", extra_tags='editar')

        return redirect("lista_usuarios")

    usuarios = Usuario.objects.all()
    empleados = Empleado.objects.all()

    return render(
        request,
        "usuarios/usuarios.html",
        {"usuarios": usuarios, "empleados": empleados, "roles": ROLES.items()}
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

