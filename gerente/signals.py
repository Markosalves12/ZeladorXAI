from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from gerente.models import Gerente
from gerente.configuracao_inicial import configurar_gerente


@receiver(post_save, sender=Gerente, dispatch_uid='gerente_configuracao_inicial')
def criar_configuracao_inicial(sender, instance, created, raw=False, **kwargs):
    # raw=True em loaddata: não mexer. Só na criação; não envia e-mail.
    if created and not raw:
        transaction.on_commit(lambda: configurar_gerente(instance))
