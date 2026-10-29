from django.shortcuts import get_object_or_404
from gerente.forms_jardinagem import GerenteJardinagemForms
from settings.models import SettingServicosGerenteJardinagem, SettingServicosGerenteLimpezaPredial

def define_setting(request, model_class, email):
    from gerente.configuracao_inicial import configurar_gerente
    configurar_gerente(get_object_or_404(model_class, email=email))
