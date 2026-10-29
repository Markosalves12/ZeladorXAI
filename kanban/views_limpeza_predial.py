from django.shortcuts import render, reverse, redirect
from servicos.models_limpeza_predial import ServicoLimpezaPredialAgendado
from servicos.forms_limpeza_predial import ServicoLimpezaPredialAgendadoForms
from django.db.models.functions import Now
from django.db.models import F, ExpressionWrapper, IntegerField
from permissionscontrol.utils import validate_permissions, verify_login
from utils.utils import aplicar_filtros_dinamicos
from empresasecundario.utils import define_empresas
from django.db.models import Func

def kanban_limpeza_predial(request, userid):
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

    if setores['habilitar_limpeza_secundaria'] and setores['habilitar_limpeza']:
        tipos.insert(2, {'nome': 'Limpeza predial', 'link': reverse('kanban_limpeza_predial', kwargs={'userid': userid})})
    else:
        return redirect('kanban_jardinagem', userid)

    permission_view = validate_permissions(
        request=request,
        userid=userid,
        permission_type='limpeza_predial',
        permission_to_access=['322: Pode visualizar serviços agendados']
    )

    permission_edit = validate_permissions(
        request=request,
        userid=userid,
        permission_type='limpeza_predial',
        permission_to_access=['321: Pode editar serviços agendados']
    )

    permission_crate = validate_permissions(
        request=request,
        userid=userid,
        permission_type='limpeza_predial',
        permission_to_access=['320: Pode agendar novos serviços']
    )

    permission_accompany = validate_permissions(
        request=request,
        userid=userid,
        permission_type='limpeza_predial',
        permission_to_access=['324: Pode acompanhar serviços agendados']
    )

    permission_cancel = validate_permissions(
        request=request,
        userid=userid,
        permission_type='limpeza_predial',
        permission_to_access=['328: Pode cancelar serviços agendados']
    )

    permission_acompleshed = validate_permissions(
        request=request,
        userid=userid,
        permission_type='limpeza_predial',
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

    class DaysDifference(Func):
        function = 'EXTRACT'
        template = "%(function)s(DAY FROM %(expressions)s)"

    agendado = ServicoLimpezaPredialAgendado.objects.filter(
        Areas__localidade__unidade__empresasecundaria__empresaprimaria__id_random__in=empresas_primarias_ids,
        Areas__localidade__unidade__empresasecundaria__id_random__in=empresas_secundarias_ids,
    ).annotate(
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
            'app_name': 'Quadro Kanban Limpeza Predial',
            'link_tipos': tipos,
            'url_agendamento': 'agendar_servico_limpeza_predial',
            'url_acompanhamento': 'realizar_servico_limpeza_predial_agendado',
            'url_edicao': 'editar_servico_limpeza_predial_agendado',
            'url_cancelamento': 'cancelar_servico_limpeza_predial',
            'url_conclusao': 'concluir_servico_limpeza_predial',
            'url_detalhamento': 'view_detailing_limpeza_predial',
            'url_checklist': 'checklists_limpeza_predial',
            'form_search': ServicoLimpezaPredialAgendadoForms(request=request, userid=userid, type='search'),
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
