from solicitacoes.models import SolicitacoesJardinagem, SolicitacoesLimpezaPredial
from empresasecundario.utils import define_empresas

def solicitacoes_jardinagem(request):
    userid = request.session.get('userid', '')
    empresas = define_empresas(request=request, userid=userid)
    empresas_primarias_ids = empresas['empresas_primarias_ids']
    empresas_secundarias_ids = empresas['empresas_secundarias_ids']

    n_solicitacoes_jardinagem = SolicitacoesJardinagem.objects.filter(
        Areas__localidade__unidade__empresasecundaria__empresaprimaria__id_random__in=empresas_primarias_ids,
        Areas__localidade__unidade__empresasecundaria__id_random__in=empresas_secundarias_ids,
    ).filter(
        status="Pendente"
    ).distinct().count()

    return {
        'n_solicitacoes_jardinagem': n_solicitacoes_jardinagem,
    }

def solicitacoes_limpeza_predial(request):
    userid = request.session.get('userid', '')
    empresas = define_empresas(request=request, userid=userid)
    empresas_primarias_ids = empresas['empresas_primarias_ids']
    empresas_secundarias_ids = empresas['empresas_secundarias_ids']

    n_solicitacoes_limpeza_predial = SolicitacoesLimpezaPredial.objects.filter(
            Areas__localidade__unidade__empresasecundaria__empresaprimaria__id_random__in=empresas_primarias_ids,
            Areas__localidade__unidade__empresasecundaria__id_random__in=empresas_secundarias_ids,
    ).filter(
        status="Pendente"
    ).distinct().count()

    return {
        'n_solicitacoes_limpeza_predial': n_solicitacoes_limpeza_predial,
    }