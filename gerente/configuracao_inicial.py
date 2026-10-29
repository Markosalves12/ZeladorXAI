"""Configuração inicial de um gerente: settings de notificação e registros de permissão.

Idempotente: pode ser chamada várias vezes sem duplicar registros. É usada pela
interface, pelo sinal post_save (cobre createsuperuser, shell e admin) e pelo
comando `configurar_gerentes` para usuários antigos.
"""


def configurar_gerente(gerente):
    from settings.models import (SettingServicosGerenteJardinagem,
                                 SettingServicosGerenteLimpezaPredial)
    from permissionscontrol.models import (PermissionsAccessJardinagem,
                                           PermissionsAccessLimpezaPredial,
                                           PermissionsAccessEspecials)
    criados = 0
    for modelo in (SettingServicosGerenteJardinagem, SettingServicosGerenteLimpezaPredial,
                   PermissionsAccessJardinagem, PermissionsAccessLimpezaPredial,
                   PermissionsAccessEspecials):
        if not modelo.objects.filter(Gerente=gerente).exists():
            modelo.objects.create(Gerente=gerente)
            criados += 1
    return criados
