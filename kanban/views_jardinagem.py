from django.shortcuts import render, reverse, redirect
from servicos.models_jardinagem import ServicoJardinagemAgendado
from servicos.forms_jardinagem import ServicoJaridinagemAgendadoForms
from django.db.models.functions import Now
from django.db.models import F, ExpressionWrapper, IntegerField
from gerente.models import Gerente
from permissionscontrol.utils import validate_permissions, verify_login
from utils.utils import aplicar_filtros_dinamicos, filtrar_unicos
from empresasecundario.utils import define_empresas
from django.db.models import Func

# Create your views here.
def kanban_jardinagem(request, userid):
    if not request.user.is_authenticated:
        return redirect('logout')

    block = verify_login(request=request, userid=userid)

    if block == True:
        return redirect('logout')

    empresas = define_empresas(request=request, userid=userid)
    empresas_primarias_ids = empresas['empresas_primarias_ids']
    empresas_secundarias_ids = empresas['empresas_secundarias_ids']
    setores = empresas['setores']

    tipos = [
        {'nome': 'Kanban de serviços', 'link': ''},
    ]

    if setores['habilitar_jardinagem_secundaria'] and setores['habilitar_jardinagem']:
        tipos.insert(1, {'nome': 'Jardinagem', 'link': reverse('kanban_jardinagem', kwargs={'userid': userid})})
    else:
        return redirect('kanban_limpeza_predial', userid)

    if setores['habilitar_limpeza_secundaria'] and setores['habilitar_limpeza']:
        tipos.insert(2, {'nome': 'Limpeza predial', 'link': reverse('kanban_limpeza_predial', kwargs={'userid': userid})})


    permission_view = validate_permissions(
        request=request,
        userid=userid,
        permission_type='jardinagem',
        permission_to_access=['322: Pode visualizar serviços agendados']
    )

    permission_edit = validate_permissions(
        request=request,
        userid=userid,
        permission_type='jardinagem',
        permission_to_access=['321: Pode editar serviços agendados']
    )

    permission_crate = validate_permissions(
        request=request,
        userid=userid,
        permission_type='jardinagem',
        permission_to_access=['320: Pode agendar novos serviços']
    )

    permission_accompany = validate_permissions(
        request=request,
        userid=userid,
        permission_type='jardinagem',
        permission_to_access=['324: Pode acompanhar serviços agendados']
    )

    permission_cancel = validate_permissions(
        request=request,
        userid=userid,
        permission_type='jardinagem',
        permission_to_access=['328: Pode cancelar serviços agendados']
    )

    permission_acompleshed = validate_permissions(
        request=request,
        userid=userid,
        permission_type='jardinagem',
        permission_to_access=['326 Pode concluir serviços em andamento']
    )

    filtro_mapeamento = {
        'Areas': 'Areas__id',
        'TipoServico': 'TipoServico',
        'ServicosEscalados': 'ServicosEscalados__id',
        'ColaboradoresEscalados': 'ColaboradoresEscalados__id',
        'DataDeInicio': 'DataDeInicio',
        'DataDeConclusao': 'DataDeConclusao'
    }

    auto_acompleshed = validate_permissions(
        request=request,
        userid=userid,
        permission_type='jardinagem',
        permission_to_access=['361: Pode acompanhar serviços agendados para si próprio']
    )

    class DaysDifference(Func):
        function = 'EXTRACT'
        template = "%(function)s(DAY FROM %(expressions)s)"

    # Base queryset
    agendado_queryset = ServicoJardinagemAgendado.objects.filter(
        Areas__localidade__unidade__empresasecundaria__empresaprimaria__id_random__in=empresas_primarias_ids,
        Areas__localidade__unidade__empresasecundaria__id_random__in=empresas_secundarias_ids,
    )

    # Verificação de permissões
    gerente = Gerente.objects.get(id_random=userid)
    if auto_acompleshed and not gerente.is_superuser:
        agendado_queryset = filtrar_unicos(agendado_queryset, ColaboradoresEscalados__id_random__in=[userid, 'MuUe1D3pvT3v'])
    # Adicionando anotações e refinamento final
    agendado = agendado_queryset.annotate(
        data_atual=Now(),
        status_agendamento=ExpressionWrapper(
            DaysDifference(F('DataDeInicio') - F('data_atual')),
            output_field=IntegerField()
        )
    ).distinct()

    if request.method == 'GET':
        get_data = request.GET.dict()
        agendado = aplicar_filtros_dinamicos(agendado, get_data, filtro_mapeamento)

    return render(
        request=request,
        template_name='agendamentos/kanban.html',
        context={
            'formatted_events': agendado,
            'app_name': 'Quadro Kanban Jardinagem',
            'link_tipos': tipos,
            'url_agendamento': 'agendar_servico_jardinagem',
            'url_acompanhamento': 'realizar_servico_jardinagem_agendado',
            'url_edicao': 'editar_servico_jardinagem_agendado',
            'url_cancelamento': 'cancelar_servico_jardinagem',
            'url_conclusao': 'concluir_servico_jardinagem',
            'url_detalhamento': 'view_detailing_jardinagem',
            'url_checklist': 'checklists_jardinagem',
            'form_search': ServicoJaridinagemAgendadoForms(request=request, userid=userid, type='search'),
            'sform_search': True,
            'allowed_fields': list(filtro_mapeamento.keys()),
            'permission_view': permission_view,
            'permission_edit': permission_edit,
            'permission_crate': permission_crate,
            'permission_accompany': permission_accompany,
            'permission_cancel': permission_cancel,
            'permission_acompleshed': permission_acompleshed
        }
    )