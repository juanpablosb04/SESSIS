from django.shortcuts import render

# Vista de prueba para Registrar Empleado
def registrar_empleado(request):
    # Aquí normalmente procesarías el formulario, pero por ahora solo renderizamos el HTML
    return render(request, 'empleados/empleados.html')
