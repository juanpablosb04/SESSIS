# empleados/apps.py
from django.apps import AppConfig

class EmpleadosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "empleados"

    def ready(self):
        # Importa los signals para registrarlos
        import empleados.signals  # noqa: F401
