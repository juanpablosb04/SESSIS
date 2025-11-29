from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Inventario
from ubicaciones.models import Ubicaciones
from config.decorators import role_required


@role_required(["Administrador"])
def inventarios_view(request):
    # Traemos todos los inventarios junto con su ubicación
    inventarios = Inventario.objects.select_related("id_ubicacion").all()
    ubicaciones = Ubicaciones.objects.all()

    if request.method == 'POST':
        action = request.POST.get('action')

        # -------- CREAR --------
        if action == 'crear':
            id_inventario = request.POST.get('id_inventario')
            nombre = request.POST.get('nombre')
            descripcion = request.POST.get('descripcion')
            estado = request.POST.get('estado')
            id_ubicacion = request.POST.get('id_ubicacion')

            if not id_inventario or not nombre or not id_ubicacion:
                messages.error(request, "⚠️ ID, nombre y ubicación son obligatorios", extra_tags='crear alert-error')
            elif Inventario.objects.filter(id_inventario=id_inventario).exists():
                messages.error(request, "⚠️ Ese ID de inventario ya existe", extra_tags='crear alert-error')
            else:
                ubicacion = get_object_or_404(Ubicaciones, id_ubicacion=id_ubicacion)
                Inventario.objects.create(
                    id_inventario=id_inventario,
                    nombre=nombre,
                    descripcion=descripcion,
                    estado=estado,
                    id_ubicacion=ubicacion
                )
                messages.success(request, "✅ Equipo de inventario creado correctamente", extra_tags='crear alert-success')

        # -------- EDITAR --------
        elif action == 'editar':
            inventario_id = request.POST.get('inventario_id')
            inventario = get_object_or_404(Inventario, id_inventario=inventario_id)

            nuevo_id = request.POST.get('id_inventario')
            nuevo_nombre = request.POST.get('nombre')
            nueva_descripcion = request.POST.get('descripcion')
            nuevo_estado = request.POST.get('estado')
            nuevo_ubicacion_id = request.POST.get('id_ubicacion')

            if nuevo_id and Inventario.objects.filter(id_inventario=nuevo_id).exclude(id_inventario=inventario.id_inventario).exists():
                messages.error(request, "⚠️ Ese ID ya está en uso por otro inventario", extra_tags='editar alert-error')
            else:
                inventario.id_inventario = nuevo_id or inventario.id_inventario
                inventario.nombre = nuevo_nombre
                inventario.descripcion = nueva_descripcion
                inventario.estado = nuevo_estado
                if nuevo_ubicacion_id:
                    inventario.id_ubicacion = get_object_or_404(Ubicaciones, id_ubicacion=nuevo_ubicacion_id)
                inventario.save()
                messages.success(request, "✏️ Inventario editado correctamente", extra_tags='editar alert-success')

    return render(request, 'inventarios/inventario.html', {
        'inventarios': inventarios,
        'ubicaciones': ubicaciones  # enviar al template
    })
