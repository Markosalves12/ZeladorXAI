from utils.utils import filtrar_unicos
from areas.models_jardinagem import AreasJardins
from servicos.models_jardinagem import ServicoJardinagemAgendado
from servicos.forms_jardinagem import ServicoJaridinagemAgendadoForms
from catalogo_de_servicos.models_jardinagem import CatalogodeServicoJardinagem
from utils.views import generic_view_history
from permissionscontrol.utils import validate_permissions
from django.templatetags.static import static


# Create your views here.
def historico_de_servicos_areas_jardinagem(request, userid, id_random):
    permission_extract_pdf = validate_permissions(
        request=request,
        userid=userid,
        permission_type='jardinagem',
        permission_to_access=['311: Pode extrair relatórios PDF de jardinagem']
    )

    permission_extract_xlsx = validate_permissions(
        request=request,
        userid=userid,
        permission_type='jardinagem',
        permission_to_access=['310: Pode extrair relatórios XLSX de jardinagem']
    )

    objeto = AreasJardins.objects.get(
        id_random=id_random
    )

    objetos = ServicoJardinagemAgendado.objects.filter(
        Areas__id_random=id_random,
        status__in=['Concluido']
    )

    return generic_view_history(
        request=request,
        userid=userid,
        id_random=id_random,
        app_name=f'Histórico de serviços {objeto.nome}',
        objeto=objeto,
        objetos=objetos,
        type_exibition='jardinagem_agendado',
        type_export='areas',
        form_search=ServicoJaridinagemAgendadoForms(request=request, userid=userid, type='search'),
        sform_search=True,
        filtro_mapeamento={
            'TipoServico': 'TipoServico',
            'ServicosEscalados': 'ServicosEscalados__id',
            'ColaboradoresEscalados': 'ColaboradoresEscalados__id',
            'DataDeInicio': 'DataDeInicio',
            'DataDeConclusao': 'DataDeConclusao',
        },
        export_pdf='exportar_relatorio_de_serivos_na_area_jardinagem_pdf',
        export_pdf_with_checklist='exportar_relatorio_de_serivos_na_area_jardinagem_pdf_with_checklist',
        export_excel='exportar_relatorio_de_serivos_na_area_Jardinagem_excel',
        export_excel_with_checklist='exportar_relatorio_de_serivos_na_area_Jardinagem_excel_with_checklist',
        foto_objeto=objeto.foto.url if objeto.foto and hasattr(objeto.foto, 'url') else static('dist/img/not found.png'),
        Foto=True,
        redirect_close_button='areas_jardins',
        permission_extract_pdf=permission_extract_pdf,
        permission_extract_xlsx=permission_extract_xlsx,
        url_detalhamento='view_detailing_jardinagem',
        url_checklist='view_detailing_checklists_jardinagem'
    )


def historico_de_servicos_catologo_de_servicos_jardinagem(request, userid, id_random):
    permission_extract_pdf = validate_permissions(
        request=request,
        userid=userid,
        permission_type='jardinagem',
        permission_to_access=['311: Pode extrair relatórios PDF de jardinagem']
    )

    permission_extract_xlsx = validate_permissions(
        request=request,
        userid=userid,
        permission_type='jardinagem',
        permission_to_access=['310: Pode extrair relatórios XLSX de jardinagem']
    )

    objeto = CatalogodeServicoJardinagem.objects.get(
        id_random=id_random
    )

    objetos = ServicoJardinagemAgendado.objects.filter(
        status__in=['Concluido']
    )
    objetos = filtrar_unicos(objetos, ServicosEscalados__id_random=id_random)

    return generic_view_history(
        request=request,
        userid=userid,
        id_random=id_random,
        app_name=f'Histórico de serviços {objeto.nome}',
        objeto=objeto,
        objetos=objetos,
        type_exibition='jardinagem_agendado',
        type_export='catalogo_de_servicos',
        form_search=ServicoJaridinagemAgendadoForms(request=request, userid=userid, type='search'),
        sform_search=True,
        filtro_mapeamento={
            'Areas': 'Areas__id',
            'TipoServico': 'TipoServico',
            'ColaboradoresEscalados': 'ColaboradoresEscalados__id',
            'DataDeInicio': 'DataDeInicio',
            'DataDeConclusao': 'DataDeConclusao'
        },
        export_pdf='exportar_relatorio_de_serivos_na_area_jardinagem_pdf',
        export_pdf_with_checklist='exportar_relatorio_de_serivos_na_area_jardinagem_pdf_with_checklist',
        export_excel='exportar_relatorio_de_serivos_na_area_Jardinagem_excel',
        export_excel_with_checklist='exportar_relatorio_de_serivos_na_area_Jardinagem_excel_with_checklist',
        foto_objeto=None,
        Foto=False,
        redirect_close_button='catalogo_de_servicos_jardinagem',
        permission_extract_pdf=permission_extract_pdf,
        permission_extract_xlsx=permission_extract_xlsx,
        url_detalhamento='view_detailing_jardinagem',
        url_checklist='view_detailing_checklists_jardinagem'
    )
