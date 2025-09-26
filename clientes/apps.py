from django.apps import AppConfig
from django.apps import AppConfig

class ClientesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'clientes'

class ClientesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'clientes'

    def ready(self):
        import clientes.signals  # 👈 registra los signals al arrancar

