from django.apps import AppConfig


class GerenteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gerente'

    def ready(self):
        from gerente import signals  # noqa: F401
