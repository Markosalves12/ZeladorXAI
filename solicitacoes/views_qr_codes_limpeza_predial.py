from django.shortcuts import render, redirect, reverse
from empresasecundario.utils import define_empresas
from permissionscontrol.utils import validate_permissions
from utils.views import generic_view, GenericIfDeleteView, GenericDeleteView, edit_generic_view, gerneric_alter_status
from solicitacoes.models import QRCodeAreaLimpezaPredial
from solicitacoes.forms_limpeza_predial import QRCodeAreaLimpezaPredialForms


# Create your views here.
def qr_codes_limpeza_predial(request, userid):
    empresas = define_empresas(request=request, userid=userid)
    empresas_primarias_ids = empresas['empresas_primarias_ids']
    empresas_secundarias_ids = empresas['empresas_secundarias_ids']
    setores = empresas['setores']

    tipos = [
        {'nome': 'QR Code            ', 'link': ''},
    ]

    if setores['habilitar_jardinagem_secundaria'] and setores['habilitar_jardinagem']:
        tipos.insert(1, {'nome': 'Jardinagem', 'link': reverse('qr_codes_jardinagem', kwargs={'userid': userid})})
    else:
        return redirect('qr_codes_limpeza_predial', userid)

    if setores['habilitar_limpeza_secundaria'] and setores['habilitar_limpeza']:
        tipos.insert(2,
                     {'nome': 'Limpeza predial', 'link': reverse('qr_codes_limpeza_predial', kwargs={'userid': userid})})

    permission_view = validate_permissions(
        request=request,
        userid=userid,
        permission_type='limpeza_predial',
        permission_to_access=['422: Pode visualizar QR codes']
    )

    permission_edit = validate_permissions(
        request=request,
        userid=userid,
        permission_type='limpeza_predial',
        permission_to_access=['421: Pode editar QR codes']
    )

    permission_crate = validate_permissions(
        request=request,
        userid=userid,
        permission_type='limpeza_predial',
        permission_to_access=['420: Pode criar QR codes']
    )

    colunas = [
        {'nome': 'id', 'label': '#', 'largura': '10px'},
        {'nome': 'Areas', 'label': 'Área'},
        {'nome': 'codigo', 'label': 'Código'},
        {'nome': 'imagem_qr', 'label': 'QR código'},
        {'nome': 'status', 'label': 'status'},
    ]

    return generic_view(
        request=request,
        model=QRCodeAreaLimpezaPredial.objects.filter(
            Areas__localidade__unidade__empresasecundaria__empresaprimaria__id_random__in=empresas_primarias_ids,
            Areas__localidade__unidade__empresasecundaria__id_random__in=empresas_secundarias_ids,
        ).distinct(),
        form_class=QRCodeAreaLimpezaPredialForms,
        template_name='DataTableAndForms/ViewQRcodesLP.html',
        columns=colunas,
        edition_rout='editar_qr_codes_limpeza_predial',
        history_rout='historico_de_servicos_areas_jardinagem',
        app_name='QR Codes disponiveis',
        form_search=QRCodeAreaLimpezaPredialForms(request=request, userid=userid, type='search'),
        sform_search=True,
        filtro_mapeamento={
            'Areas': 'Areas__id',
        },
        text_button_open_modal='Criar QR code',
        text_button_save='Salvar QR',
        header_model='Nova código QR',
        redirect_url=reverse('qr_codes_limpeza_predial', kwargs={'userid': userid}),
        link_tipos=tipos,
        permission_view=permission_view,
        permission_edit=permission_edit,
        permission_crate=permission_crate,
        userid=userid,
    )


def editar_qr_codes_limpeza_predial(request, userid, id_random):
    permission_edit = validate_permissions(
        request=request,
        userid=userid,
        permission_type='limpeza_predial',
        permission_to_access=['421: Pode editar QR codes']
    )

    permission_exclude = validate_permissions(
        request=request,
        userid=userid,
        permission_type='limpeza_predial',
        permission_to_access=['423: Pode excluir QR codes']
    )

    permission_desmobilize = validate_permissions(
        request=request,
        userid=userid,
        permission_type='limpeza_predial',
        permission_to_access=['424: Pode desmobilizar QR codes']
    )

    permission_rehabilitate = validate_permissions(
        request=request,
        userid=userid,
        permission_type='limpeza_predial',
        permission_to_access=['425: Pode reabilitar QR codes']
    )

    return edit_generic_view(
        request=request,
        model_class=QRCodeAreaLimpezaPredial,
        form_class=QRCodeAreaLimpezaPredialForms,
        template_name='DataTableAndForms/EditObject.html',
        id_random=id_random,
        app_name='Editar QR code',
        redirect_url_name=reverse('editar_qr_codes_limpeza_predial', kwargs={'userid': userid, 'id_random': id_random}),
        redirect_close_button=reverse('qr_codes_limpeza_predial', kwargs={'userid': userid}),
        permission_edit=permission_edit,
        permission_exclude=permission_exclude,
        permission_desmobilize=permission_desmobilize,
        permission_rehabilitate=permission_rehabilitate,
        url_desmobilize=reverse(
            'alterar_status_qr_codes_limpeza_predial',
            kwargs={
                'userid': userid,
                'id_random': id_random,
                'new_status': 'Desmobilizado',
            }
        ),
        url_rehabilitate=reverse(
            'alterar_status_qr_codes_limpeza_predial',
            kwargs={
                'userid': userid,
                'id_random': id_random,
                'new_status': 'Mobilizado',
            }
        ),
        userid=userid,
        url_if_delete=reverse(
            'IfDeleteQRCodeLimpezaPredial',
            kwargs={
                'userid': userid,
                'id_random': id_random,
            }
        ),
    )


def alterar_status_qr_codes_limpeza_predial(request, userid, id_random, new_status):
    objeto = QRCodeAreaLimpezaPredial.objects.get(id_random=id_random)
    return gerneric_alter_status(
        request=request,
        model_class=QRCodeAreaLimpezaPredial,
        redirect_url_name=reverse('editar_qr_codes_limpeza_predial', kwargs={'userid': userid, 'id_random': id_random}),
        id_random=id_random,
        new_status=new_status,
        userid=userid,
        message=f'{objeto.codigo} reabilitado com sucesso' if new_status == 'Mobilizado' else f'{objeto.codigo} desmobilizado com sucesso'
    )


def IfDeleteQRCodeLimpezaPredial(request, userid, id_random):
    empresas = define_empresas(request=request, userid=request.user.id_random)
    empresas_primarias_ids = empresas["empresas_primarias_ids"]
    empresas_secundarias_ids = empresas["empresas_secundarias_ids"]

    return GenericIfDeleteView(
        request,
        model=QRCodeAreaLimpezaPredial,
        id_random=id_random,
        permission_type='limpeza_predial',
        permission_to_access=['423: Pode excluir QR codes'],
        access_filters={
            "Areas__localidade__unidade__empresasecundaria__empresaprimaria__id_random__in": empresas_primarias_ids,
            "Areas__localidade__unidade__empresasecundaria__id_random__in": empresas_secundarias_ids,
        },
        template_name="DataTableAndForms/IfDelete.html",
        app_name="Deletar QR code limpeza predial",
        url_delete=reverse(
            'DeleteQRCodeLimpezaPredial',
            kwargs={
                'id_random': id_random,
            }
        ),
        redirect_close_button=reverse('qr_codes_limpeza_predial', kwargs={'userid': request.user.id_random})
    )



def DeleteQRCodeLimpezaPredial(request, id_random):
    empresas = define_empresas(request=request, userid=request.user.id_random)
    empresas_primarias_ids = empresas["empresas_primarias_ids"]
    empresas_secundarias_ids = empresas["empresas_secundarias_ids"]

    return GenericDeleteView(
        request,
        model=QRCodeAreaLimpezaPredial,
        id_random=id_random,
        permission_type='limpeza_predial',
        permission_to_access=['423: Pode excluir QR codes'],
        access_filters={
            "Areas__localidade__unidade__empresasecundaria__empresaprimaria__id_random__in": empresas_primarias_ids,
            "Areas__localidade__unidade__empresasecundaria__id_random__in": empresas_secundarias_ids,
        },
        redirect_close_button=reverse('qr_codes_limpeza_predial', kwargs={'userid': request.user.id_random}),
    )