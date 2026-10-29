from django.shortcuts import render, reverse, redirect
from servicos.forms_limpeza_predial import ServicoLimpezaPredialAgendadoForms
from permissionscontrol.utils import validate_permissions, verify_login
from utils.utils import aplicar_filtros_dinamicos
from empresasecundario.utils import define_empresas
from servicos.utils_limpeza_predial import query_servicos_limpeza_predial_agendados_anotados
from utils.utils import paginate
from dashboards.data_visualization_jardinagem import data_visualization_jardinagem_graphs

def mapas_limpeza_predial(request, userid):
    if not request.user.is_authenticated:
        return redirect('logout')

    block = verify_login(request=request, userid=userid)

    if block == True:
        return redirect('logout')

    empresas = define_empresas(request=request, userid=userid)
    setores = empresas['setores']

    tipos = [
        {'nome': 'Mapa de serviços', 'link': ''},
    ]

    if setores['habilitar_jardinagem_secundaria'] and setores['habilitar_jardinagem']:
        tipos.insert(1, {'nome': 'Jardinagem', 'link': reverse('mapas_jardinagem', kwargs={'userid': userid})})

    if setores['habilitar_limpeza_secundaria'] and setores['habilitar_limpeza']:
        tipos.insert(2, {'nome': 'Limpeza predial', 'link': reverse('mapas_limpeza_predial', kwargs={'userid': userid})})
    else:
        return redirect('mapas_jardinagem', userid)

    permission_view = validate_permissions(
        request=request,
        userid=userid,
        permission_type='limpeza_predial',
        permission_to_access=['322: Pode visualizar serviços agendados']
    )

    permission_crate = validate_permissions(
        request=request,
        userid=userid,
        permission_type='limpeza_predial',
        permission_to_access=['320: Pode agendar novos serviços']
    )

    filtro_mapeamento = {
        'Areas': 'Areas__id',
        'TipoServico': 'TipoServico',
        'ServicosEscalados': 'ServicosEscalados__id',
        'DataDeInicio': 'DataDeInicio',
        'DataDeConclusao': 'DataDeConclusao'
    }

    agendado = query_servicos_limpeza_predial_agendados_anotados(
        request,
        userid,
        status_list=['Agendado', 'Em andamento']
    )

    if request.method == 'GET':
        get_data = request.GET.dict()
        agendado = aplicar_filtros_dinamicos(agendado, get_data, filtro_mapeamento)


    agendado = paginate(
        request=request,
        data_objects=agendado,
        per_page=15
    )

    fig_mapa_localidades = data_visualization_jardinagem_graphs(
        request, userid, agendado
    ).create_fig_maps_distrubuiton_services_by_status(
        name_fig='fig_mapa_localidades'
    )

    return render(
        request=request,
        template_name='agendamentos/mapas.html',
        context={
            'app_name': 'Mapa de serviços Limpeza Predial',
            'link_tipos': tipos,
            'url_agendamento': 'agendar_servico_limpeza_predial',
            'form_search': ServicoLimpezaPredialAgendadoForms(request=request, userid=userid, type='search'),
            'sform_search': True,
            'allowed_fields': list(filtro_mapeamento.keys()),
            'permission_view': permission_view,
            'permission_crate': permission_crate,
            **fig_mapa_localidades,
        }
    )
