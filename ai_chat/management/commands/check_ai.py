from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from ai_chat.lmstudio import request_json, ModelError
from django.conf import settings

class Command(BaseCommand):
    help = 'Verifica banco e modelos do LM Studio sem criar serviços ou enviar e-mail.'
    def handle(self, *args, **options):
        connection.ensure_connection()
        self.stdout.write('Banco conectado.')
        try:
            ids = [row['id'] for row in request_json('/models').get('data', [])]
        except ModelError as exc:
            raise CommandError(str(exc))
        if settings.LMSTUDIO_CHAT_MODEL not in ids:
            raise CommandError('LMSTUDIO_CHAT_MODEL não está entre os modelos disponíveis: ' + ', '.join(ids))
        self.stdout.write(self.style.SUCCESS('Modelo de conversa disponível. Teste uma pergunta na interface.'))
