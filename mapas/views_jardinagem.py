from django.shortcuts import render, reverse, redirect
from servicos.forms_jardinagem import ServicoJaridinagemAgendadoForms
from permissionscontrol.utils import validate_permissions, verify_login
from utils.utils import aplicar_filtros_dinamicos
from empresasecundario.utils import define_empresas
from dashboards.data_visualization_jardinagem import data_visualization_jardinagem_graphs
from servicos.utils_jardinagem import query_servicos_jardinagem_agendados_anotados, colect_dados_agendamentos_jardinagem
from utils.utils import paginate

# Create your views here.
def mapas_jardinagem(request, userid):
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
    else:
        return redirect('mapas_limpeza_predial', userid)

    if setores['habilitar_limpeza_secundaria'] and setores['habilitar_limpeza']:
        tipos.insert(2,
                     {'nome': 'Limpeza predial', 'link': reverse('mapas_limpeza_predial', kwargs={'userid': userid})})

    permission_view = validate_permissions(
        request=request,
        userid=userid,
        permission_type='jardinagem',
        permission_to_access=['322: Pode visualizar serviços agendados']
    )

    permission_crate = validate_permissions(
        request=request,
        userid=userid,
        permission_type='jardinagem',
        permission_to_access=['320: Pode agendar novos serviços']
    )

    filtro_mapeamento = {
        'Areas': 'Areas__id',
        'TipoServico': 'TipoServico',
        'ServicosEscalados': 'ServicosEscalados__id',
        'ColaboradoresEscalados': 'ColaboradoresEscalados__id',
        'DataDeInicio': 'DataDeInicio',
        'DataDeConclusao': 'DataDeConclusao'
    }

    # Base queryset
    agendado = query_servicos_jardinagem_agendados_anotados(
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
            'app_name': 'Mapa de serviços Jardinagem',
            'link_tipos': tipos,
            'url_agendamento': 'agendar_servico_jardinagem',
            'form_search': ServicoJaridinagemAgendadoForms(request=request, userid=userid, type='search'),
            'sform_search': True,
            'allowed_fields': list(filtro_mapeamento.keys()),
            'permission_view': permission_view,
            'permission_crate': permission_crate,
            **fig_mapa_localidades,
        }
    )
