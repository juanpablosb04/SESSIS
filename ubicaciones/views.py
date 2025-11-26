from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Ubicaciones
from config.decorators import role_required
from django.core.paginator import Paginator

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


from django.core.paginator import Paginator

@role_required(["Administrador"])
def consulta_ubicaciones_view(request):
    ubicaciones_list = Ubicaciones.objects.all().order_by('id_ubicacion')

    # PAGINACIÓN: 6 por página
    paginator = Paginator(ubicaciones_list, 6)
    page_number = request.GET.get('page')
    ubicaciones = paginator.get_page(page_number)

    if request.method == 'POST':
        action = request.POST.get('action')
        ubicacion_id = request.POST.get('ubicacion_id')
        ubicacion = get_object_or_404(Ubicaciones, id_ubicacion=ubicacion_id)

        if action == 'editar':
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


