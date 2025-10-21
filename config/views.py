from django.shortcuts import render

def sin_permiso(request):
    return render(request, "sin_permiso.html")