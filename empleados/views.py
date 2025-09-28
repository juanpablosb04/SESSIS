from django.shortcuts import render, redirect, get_object_or_404
from .forms import EmpleadoForm
from .models import Empleado
from config.decorators import role_required

# Vista de prueba para Registrar Empleado

@role_required(["Administrador"])
def registrar_empleado(request):
    if request.method == 'POST':
        form = EmpleadoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('empleados')  # recarga la misma página
    else:
        form = EmpleadoForm()

    empleados = Empleado.objects.all()  # 🔹 traemos todos los empleados
    return render(request, 'empleados/empleados.html', {
        'form': form,
        'empleados': empleados
    })

@role_required(["Administrador"])
def editar_empleado(request, id_empleado):
    empleado = get_object_or_404(Empleado, id_empleado=id_empleado)
    if request.method == 'POST':
        form = EmpleadoForm(request.POST, instance=empleado)
        if form.is_valid():
            form.save()
            return redirect('empleados')
        else:
            empleados = Empleado.objects.all()
            return render(request, 'empleados/registro.html', {
                'form': form,
                'empleados': empleados
            })
    return redirect('empleados')


@role_required(["Administrador"])
def eliminar_empleado(request, id_empleado):
    empleado = get_object_or_404(Empleado, id_empleado=id_empleado)
    if request.method == 'POST':
        empleado.delete()
        return redirect('empleados')
    return redirect('empleados')