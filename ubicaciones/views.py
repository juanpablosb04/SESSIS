from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Ubicaciones
from config.decorators import role_required

@role_required(["Administrador"])
def registro_ubicaciones_view(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        tipo = request.POST.get('tipo')
        direccion = request.POST.get('direccion')
        imagen_url = request.POST.get('imagen_url')

        if not nombre or not direccion:
            messages.error(request, "⚠️ Nombre y dirección son obligatorios", extra_tags='crear')
        else:
            Ubicaciones.objects.create(
                nombre=nombre,
                tipo=tipo,
                direccion=direccion,
                imagen_url=imagen_url
            )
            messages.success(request, "✅ Ubicación registrada correctamente", extra_tags='crear')
            return redirect('registroUbicaciones')

    return render(request, 'ubicaciones/registroUbicaciones.html')


@role_required(["Administrador"])
def consulta_ubicaciones_view(request):
    ubicaciones = Ubicaciones.objects.all()

    if request.method == 'POST':
        action = request.POST.get('action')
        ubicacion_id = request.POST.get('ubicacion_id')
        ubicacion = get_object_or_404(Ubicaciones, id_ubicacion=ubicacion_id)

        if action == 'eliminar':
            ubicacion.delete()
            messages.success(request, "🗑️ Ubicación eliminada correctamente")
            return redirect('consultaUbicaciones')

        elif action == 'editar':
            # Actualizar los campos
            ubicacion.nombre = request.POST.get('nombre')
            ubicacion.tipo = request.POST.get('tipo')
            ubicacion.direccion = request.POST.get('direccion')
            ubicacion.imagen_url = request.POST.get('imagen_url')
            ubicacion.save()
            messages.success(request, "✏️ Ubicación actualizada correctamente", extra_tags='editar')
            return redirect('consultaUbicaciones')

    return render(request, 'ubicaciones/consultaUbicaciones.html', {
        'ubicaciones': ubicaciones
    })

