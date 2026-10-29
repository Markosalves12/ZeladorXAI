from django.core.management.base import BaseCommand

from gerente.models import Gerente
from gerente.configuracao_inicial import configurar_gerente


class Command(BaseCommand):
    help = "Cria settings de notificação e registros de permissão faltantes para todos os gerentes (sem duplicar, sem e-mail)."

    def handle(self, *args, **options):
        total = 0
        for gerente in Gerente.objects.all().iterator():
            n = configurar_gerente(gerente)
            if n:
                total += n
                self.stdout.write(f"{gerente.username}: {n} registro(s) criado(s)")
        self.stdout.write(self.style.SUCCESS(f"Concluído. {total} registro(s) criado(s)."))
