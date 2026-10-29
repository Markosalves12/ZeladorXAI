from utils.utils import filtrar_unicos
from areas.models_limpeza_predial import AreaLimpezaPredial
from servicos.utils_limpeza_predial import colect_dados_fato_servico_limpeza_predial
from servicos.forms_limpeza_predial import ServicoLimpezaPredialAgendadoForms
from catalogo_de_servicos.models_limpeza_predial import CatalogodeServicoLimpezaPredial
from utils.views import generic_view_history
from permissionscontrol.utils import validate_permissions
from django.templatetags.static import static


# Create your views here.
def historico_de_servicos_areas_limpeza_predial(request, userid, id_random):
    permission_extract_pdf = validate_permissions(
        request=request,
        userid=userid,
        permission_type='limpeza_predial',
        permission_to_access=['311: Pode extrair relatórios PDF de limpeza predial']
    )

    permission_extract_xlsx = validate_permissions(
        request=request,
        userid=userid,
        permission_type='limpeza_predial',
        permission_to_access=['310: Pode extrair relatórios XLSX de limpeza predial']
    )

    objeto = AreaLimpezaPredial.objects.get(
        id_random=id_random
    )

    objetos = colect_dados_fato_servico_limpeza_predial(
        request=request,
        userid=userid,
        DataDeInicio='None',
        DataDeConclusao='None',
        TipoServico='None',
        Areas='None',
        ServicosEscalados=['None'],
        ColaboradoresEscalados=['None'],
        status=['Concluido']
    ).filter(
        Servico__Areas__id_random=id_random
    ).distinct()

    return generic_view_history(
        request=request,
        userid=userid,
        id_random=id_random,
        app_name=f'Histórico de serviços {objeto.nome}',
        objeto=objeto,
        objetos=objetos,
        type_exibition='fato_limpeza_predial',
        type_export='areas',
        form_search=ServicoLimpezaPredialAgendadoForms(request=request, userid=userid, type='search'),
        sform_search=True,
        filtro_mapeamento={
            'TipoServico': 'Servico__TipoServico',
            'ServicosEscalados': 'Servico__ServicosEscalados__id',
            'DataDeInicio': 'Servico__DataDeInicio',
            'DataDeConclusao': 'Servico__DataDeConclusao',
        },
        export_pdf='exportar_relatorio_de_serivos_na_area_limpeza_predial_pdf',
        export_pdf_with_checklist='exportar_relatorio_de_serivos_na_area_limpeza_predial_pdf_with_checklist',
        export_excel='exportar_relatorio_de_serivos_na_area_limpeza_predial_excel',
        export_excel_with_checklist='exportar_relatorio_de_serivos_na_area_limpeza_predial_excel_with_checklist',
        foto_objeto = objeto.foto.url if objeto.foto and hasattr(objeto.foto, 'url') else static('dist/img/not found.png'),
        Foto=True,
        redirect_close_button='areas_limpeza_predial',
        permission_extract_pdf=permission_extract_pdf,
        permission_extract_xlsx=permission_extract_xlsx,
        url_detalhamento='view_detailing_limpeza_predial',
        url_checklist='view_detailing_checklists_limpeza_predial'
    )


def historico_de_servicos_catologo_de_servicos_limpeza_predial(request, userid, id_random):
    permission_extract_pdf = validate_permissions(
        request=request,
        userid=userid,
        permission_type='limpeza_predial',
        permission_to_access=['311: Pode extrair relatórios PDF de limpeza predial']
    )

    permission_extract_xlsx = validate_permissions(
        request=request,
        userid=userid,
        permission_type='limpeza_predial',
        permission_to_access=['310: Pode extrair relatórios XLSX de limpeza predial']
    )

    objeto = CatalogodeServicoLimpezaPredial.objects.get(
        id_random=id_random
    )

    objetos = colect_dados_fato_servico_limpeza_predial(
        request=request,
        userid=userid,
        DataDeInicio='None',
        DataDeConclusao='None',
        TipoServico='None',
        Areas='None',
        ServicosEscalados=['None'],
        ColaboradoresEscalados=['None'],
        status=['Concluido']
    ).distinct()
    objetos = filtrar_unicos(objetos, Servico__ServicosEscalados__id_random=id_random)

    return generic_view_history(
        request=request,
        userid=userid,
        id_random=id_random,
        app_name=f'Histórico de serviços {objeto.nome}',
        objeto=objeto,
        objetos=objetos,
        type_exibition='fato_limpeza_predial',
        type_export='catalogo_de_servicos',
        form_search=ServicoLimpezaPredialAgendadoForms(request=request, userid=userid, type='search'),
        sform_search=True,
        filtro_mapeamento={
            'Areas': 'Servico__Areas__id',
            'TipoServico': 'Servico__TipoServico',
            'ColaboradoresEscalados': 'Servico__ColaboradoresEscalados__id',
            'DataDeInicio': 'Servico__DataDeInicio',
            'DataDeConclusao': 'Servico__DataDeConclusao'
        },
        export_pdf='exportar_relatorio_de_serivos_na_area_limpeza_predial_pdf',
        export_pdf_with_checklist='exportar_relatorio_de_serivos_na_area_limpeza_predial_pdf_with_checklist',
        export_excel='exportar_relatorio_de_serivos_na_area_limpeza_predial_excel',
        export_excel_with_checklist='exportar_relatorio_de_serivos_na_area_limpeza_predial_excel_with_checklist',
        foto_objeto=None,
        Foto=False,
        redirect_close_button='catalogo_de_servicos_limpeza_predial',
        permission_extract_pdf=permission_extract_pdf,
        permission_extract_xlsx=permission_extract_xlsx,
        url_detalhamento='view_detailing_limpeza_predial',
        url_checklist='view_detailing_checklists_limpeza_predial'
    )
