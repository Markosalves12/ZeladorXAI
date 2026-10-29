from django.apps import AppConfig

class AiChatConfig(AppConfig):
    name = 'ai_chat'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        # Shared apps split their models by vertical instead of models.py.
        # Register them without modifying shared apps or their migrations.
        from servicos import models_jardinagem, models_limpeza_predial  # noqa: F401
