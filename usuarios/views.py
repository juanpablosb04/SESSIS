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

    usuarios = Usuario.objects.all().order_by("email")

    paginator = Paginator(usuarios, 5)
    page_number = request.GET.get("page")
    usuarios = paginator.get_page(page_number)

    if request.method == "POST":
        action = request.POST.get("action")
        usuario_actual = None 

        # =============================
        # VALIDACIONES GENERALES
        # =============================
        email = request.POST.get("email", "").strip()
        id_empleado = request.POST.get("id_empleado")
        id_rol = request.POST.get("id_rol")
        estado = request.POST.get("estado", "")

        # Email vacío
        if not email:
            messages.error(request, "❌ El email es obligatorio.", extra_tags='crear alert-error')
            return redirect("lista_usuarios")

        # Validación email básico
        if "@" not in email or "." not in email:
            messages.error(request, "❌ Debes ingresar un email válido.", extra_tags='crear alert-error')
            return redirect("lista_usuarios")

        # Empleado obligatorio
        if not id_empleado:
            messages.error(request, "❌ Debes seleccionar un empleado.", extra_tags='crear alert-error')
            return redirect("lista_usuarios")

        # Rol obligatorio
        if not id_rol:
            messages.error(request, "❌ Debes seleccionar un rol.", extra_tags='crear alert-error')
            return redirect("lista_usuarios")

        # Estado obligatorio
        if not estado:
            messages.error(request, "❌ Debes seleccionar un estado.", extra_tags='crear alert-error')
            return redirect("lista_usuarios")

        # ============================================
        # CREAR USUARIO
        # ============================================
        if action == "crear":
            password = request.POST.get("password")

            # Contraseña obligatoria
            if not password:
                messages.error(request, "❌ La contraseña es obligatoria.", extra_tags='crear alert-error')
                return redirect("lista_usuarios")

            # Email único
            if Usuario.objects.filter(email=email).exists():
                messages.error(request, "❌ Ya existe un usuario con este email.", extra_tags='crear alert-error')
                return redirect("lista_usuarios")

            # OPCIONAL: un empleado no puede tener 2 usuarios
            if Usuario.objects.filter(id_empleado=id_empleado).exists():
                messages.error(request, "❌ Este empleado ya tiene un usuario asociado.", extra_tags='crear alert-error')
                return redirect("lista_usuarios")

            # Crear usuario
            usuario = Usuario.objects.create(
                id_empleado_id=int(id_empleado),
                id_rol=int(id_rol),
                email=email,
                password=make_password(password),   # ← ENCRIPTAR
                estado=estado,
                password_temp=True
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

            messages.success(request, "✅ Usuario creado correctamente.", extra_tags='crear alert-success')
            return redirect("lista_usuarios")

        # ============================================
        # EDITAR USUARIO
        # ============================================
        elif action == "editar":
            usuario = get_object_or_404(Usuario, id_usuario=request.POST["usuario_id"])

            usuario_logueado_id = request.session.get("usuario_id")

            # =======================
            # 🚫 NO PERMITIR AUTO-INACTIVARSE
            # =======================
            if usuario_logueado_id and int(usuario_logueado_id) == usuario.id_usuario and estado == "Inactivo":
                messages.error(
                    request,
                    "❌ No puedes inactivar tu propio usuario mientras estás logeado con el.",
                    extra_tags='editar alert-error'
                )
                return redirect("lista_usuarios")

            nueva_password = request.POST.get("password")

            # Validación: email único en actualización
            if Usuario.objects.filter(email=email).exclude(id_usuario=usuario.id_usuario).exists():
                messages.error(request, "❌ Ya existe otro usuario con este email.", extra_tags='editar alert-error')
                return redirect("lista_usuarios")

            usuario.id_empleado_id = int(id_empleado)
            usuario.id_rol = int(id_rol)
            usuario.email = email

            # Cambiar contraseña solo si el usuario ingresó una nueva
            if nueva_password and nueva_password != "********":
                usuario.password = make_password(nueva_password)

            usuario.estado = estado
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

            messages.success(request, "✏️ Usuario editado correctamente.", extra_tags='editar alert-success')
            return redirect("lista_usuarios")

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
    
    paginator = Paginator(auditoria, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "usuarios/auditoria_usuario.html",
        {"usuario": usuario, "auditoria": auditoria, "page_obj": page_obj,}
    )

