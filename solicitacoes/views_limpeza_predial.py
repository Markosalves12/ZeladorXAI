from django.shortcuts import render, redirect, get_object_or_404
from empresasecundario.utils import define_empresas
from permissionscontrol.utils import validate_permissions, verify_login
from utils.views import generic_view, edit_generic_view
from solicitacoes.models import SolicitacoesLimpezaPredial, QRCodeAreaLimpezaPredial
from solicitacoes.forms_limpeza_predial import QRCodeAreaLimpezaPredialForms, SolicitacoesLimpezaPredialForms
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from servicos.forms_limpeza_predial import ServicoLimpezaPredialAgendadoForms


# Create your views here.
def solicitacoes_limpeza_predial(request, userid):
    empresas = define_empresas(request=request, userid=userid)
    empresas_primarias_ids = empresas['empresas_primarias_ids']
    empresas_secundarias_ids = empresas['empresas_secundarias_ids']
    setores = empresas['setores']

    tipos = [
        {'nome': 'Tipo de solicitação', 'link': ''},
    ]

    if setores['habilitar_jardinagem_secundaria'] and setores['habilitar_jardinagem']:
        tipos.insert(1, {'nome': 'Jardinagem', 'link': reverse('solicitacoes_jardinagem', kwargs={'userid': userid})})
    else:
        return redirect('solicitacoes_limpeza_predial', userid)

    if setores['habilitar_limpeza_secundaria'] and setores['habilitar_limpeza']:
        tipos.insert(2,
                     {'nome': 'Limpeza predial', 'link': reverse('solicitacoes_limpeza_predial', kwargs={'userid': userid})})

    permission_view = validate_permissions(
        request=request,
        userid=userid,
        permission_type='limpeza_predial',
        permission_to_access=['432: Pode visualizar solicitacoes']
    )

    permission_edit = validate_permissions(
        request=request,
        userid=userid,
        permission_type='jardinagem',
        permission_to_access=['431: Pode editar solicitacoes']
    )

    colunas = [
        {'nome': 'id', 'label': '#', 'largura': '10px'},
        {'nome': 'Areas', 'label': 'Área'},
        {'nome': 'descricao', 'label': 'Descrição'},
        {'nome': 'data_criacao', 'label': 'Data de criação'},
        {'nome': 'criado_por', 'label': 'Criado por'},
        {'nome': 'aprovado_por', 'label': 'Aprovador'},
        {'nome': 'status', 'label': 'status'},
        {'nome': 'acoes', 'label': 'Ações'},
    ]

    return generic_view(
        request=request,
        model=SolicitacoesLimpezaPredial.objects.filter(
            Areas__localidade__unidade__empresasecundaria__empresaprimaria__id_random__in=empresas_primarias_ids,
            Areas__localidade__unidade__empresasecundaria__id_random__in=empresas_secundarias_ids,
        ).distinct(),
        form_class=QRCodeAreaLimpezaPredialForms,
        template_name='DataTableAndForms/DataTableAndForms.html',
        columns=colunas,
        edition_rout='editar_solicitacao_limpeza_predial',
        history_rout='historico_de_servicos_areas_jardinagem',
        app_name='Solicitações limpeza predial',
        form_search=QRCodeAreaLimpezaPredialForms(request=request, userid=userid, type='search'),
        sform_search=True,
        filtro_mapeamento={
            'Areas': 'Areas__id',
        },
        text_button_open_modal='',
        text_button_save='',
        header_model='',
        redirect_url=reverse('solicitacoes_limpeza_predial', kwargs={'userid': userid}),
        link_tipos=tipos,
        permission_view=permission_view,
        permission_edit=permission_edit,
        permission_crate=False,
        userid=userid,
    )



def editar_solicitacao_limpeza_predial(request, userid, id_random):
    permission_edit = validate_permissions(
        request=request,
        userid=userid,
        permission_type='limpeza_predial',
        permission_to_access=['431: Pode editar solicitacoes']
    )

    permission_exclude = validate_permissions(
        request=request,
        userid=userid,
        permission_type='limpeza_predial',
        permission_to_access=['433: Pode excluir solicitacoes']
    )

    permission_desmobilize = validate_permissions(
        request=request,
        userid=userid,
        permission_type='limpeza_predial',
        permission_to_access=['434: Pode Rejeitar/aceitar solicitacoes']
    )

    permission_rehabilitate = validate_permissions(
        request=request,
        userid=userid,
        permission_type='limpeza_predial',
        permission_to_access=['434: Pode Rejeitar/aceitar solicitacoes']
    )

    area = SolicitacoesLimpezaPredial.objects.get(id_random=id_random).Areas.id_random

    return edit_generic_view(
        request=request,
        model_class=SolicitacoesLimpezaPredial,
        form_class=SolicitacoesLimpezaPredialForms,
        template_name='DataTableAndForms/EditObjectsExterns.html',
        id_random=id_random,
        app_name='Editar solicitação',
        redirect_url_name=reverse('editar_solicitacao_limpeza_predial', kwargs={'userid': userid, 'id_random': id_random}),
        redirect_close_button=reverse('servicos_agendados_limpeza_predial', kwargs={'userid': userid}),
        permission_edit=permission_edit,
        permission_exclude=permission_exclude,
        permission_desmobilize=permission_desmobilize,
        permission_rehabilitate=permission_rehabilitate,
        url_rehabilitate=reverse(
            'accept_solicitacao_limpeza_predial',
            kwargs={
                'userid': userid,
                'id_random': id_random,
            }
        ),
        url_desmobilize=reverse(
            'reject_solicitacao_limpeza_predial',
            kwargs={
                'userid': userid,
                'id_random': id_random,
            }
        ),
        userid=userid,
        url_if_delete=reverse(
            'IfDeleteServicoAgendadoLimpezaPredial',
            kwargs={
                'userid': userid,
                'id_random': id_random,
            }
        ),
        id_random_especial=area
    )




def solicitar_servico_limpeza_predial(request, id_randomqr, id_randomarea):
    # Carrega o formulário (GET inicial)
    forms = SolicitacoesLimpezaPredialForms(request=request, id_random=id_randomarea)

    # Recupera o QR Code pelo id_random
    try:
        qr_code = QRCodeAreaLimpezaPredial.objects.get(id_random=id_randomqr)
        if qr_code.status == "Desmobilizado":
            raise QRCodeAreaLimpezaPredial.DoesNotExist

    except QRCodeAreaLimpezaPredial.DoesNotExist:
        # Caso não exista, renderiza a página customizada
        return render(
            request,
            'DataTableAndForms/QRcodeNotFound.html',
            status=404,  # mantém status HTTP correto,
            context={
                'app_name': 'Solicitar serviço de limpeza predial',
            }
        )

    # Pegando todas as empresas primárias associadas
    nome_empresa = (
        qr_code.Areas.localidade.unidade.empresasecundaria
        .values_list("empresaprimaria__nome", flat=True)
        .first()
    )

    if request.method == 'POST':
        form = SolicitacoesLimpezaPredialForms(
            request.POST,
            request.FILES,
            request=request,
            id_random=id_randomarea
        )

        if form.is_valid():
            solicitacao = form.save(commit=False)

            # 🔹 Preenche campos automáticos
            if request.user.is_authenticated:
                solicitacao.criado_por = request.user
            else:
                solicitacao.criado_por = None  # caso queira permitir anônimo

            solicitacao.data_criacao = timezone.now()
            solicitacao.qrcode = qr_code

            solicitacao.save()

            messages.success(request, 'Solicitação concluída com sucesso!')

            return redirect('solicitar_servico_limpeza_predial', id_randomqr, id_randomarea)

        messages.error(request, 'Algo deu errado ao salvar a solicitação.')

    # 🔹 Botão de fechar depende do login
    redirect_close_button = (
        reverse('servicos_agendados_limpeza_predial', kwargs={'userid': request.user.id_random})
        if request.user.is_authenticated else None
    )

    return render(
        request,
        template_name='DataTableAndForms/CreateObjectExterns.html',
        context={
            'forms': forms,
            'app_name': 'Solicitar serviço de limpeza predial',
            'redirect_close_button': redirect_close_button,
            'redirect_url_name': reverse('solicitar_servico_limpeza_predial', args=[id_randomqr, id_randomarea]),
            'text_button_save': 'Solicitar Serviço',
            'permission_crate': True,
            "em_parceria": nome_empresa
        }
    )


def accept_solicitacao_limpeza_predial(request, userid, id_random):
    block = verify_login(request=request, userid=userid)

    if block == True:
        return redirect('logout')

    objeto = SolicitacoesLimpezaPredial.objects.get(id_random=id_random)
    objeto.aprovado_por = request.user
    objeto.status = 'Aprovado'
    objeto.save()

    messages.success(
        request=request,
        message=f'Solicitação {objeto}, aceita!'
    )

    return redirect('confirm_solicitacao_limpeza_predial', "calendario", userid, id_random)



def reject_solicitacao_limpeza_predial(request, userid, id_random):
    block = verify_login(request=request, userid=userid)

    if block == True:
        return redirect('logout')

    objeto = SolicitacoesLimpezaPredial.objects.get(id_random=id_random)
    objeto.status = 'Rejeitado'
    objeto.aprovado_por = request.user
    objeto.save()

    messages.warning(
        request=request,
        message=f'Solicitação {objeto}, rejeitada!'
    )

    return redirect('solicitacoes_limpeza_predial', userid)


def confirm_solicitacao_limpeza_predial(request, type, userid, id_random):
    block = verify_login(request=request, userid=userid)

    if block == True:
        return redirect('logout')

    empresas = define_empresas(request=request, userid=userid)
    setores = empresas['setores']

    tipos = [
        {'nome': 'Agendar serviços', 'link': ''},
    ]

    if setores['habilitar_jardinagem_secundaria'] and setores['habilitar_jardinagem']:
        tipos.insert(
            1,
            {
                'nome': 'Jardinagem',
                'link': reverse(
                    'agendar_servico_jardinagem',
                    kwargs={'type': type, 'userid': userid}
                )
            },
        )
    else:
        return redirect('agendar_servico_jardinagem', type, userid)

    if setores['habilitar_limpeza_secundaria'] and setores['habilitar_limpeza']:
        tipos.insert(
            2,
            {
                'nome': 'Limpeza predial',
                'link': reverse(
                    'agendar_servico_limpeza_predial',
                    kwargs={'type': type, 'userid': userid}
                )
            }
        )

    solicitacao = SolicitacoesLimpezaPredial.objects.get(id_random=id_random)
    Areas = solicitacao.Areas

    forms = ServicoLimpezaPredialAgendadoForms(request=request, userid=userid, initial={'Areas': Areas})

    permission_crate = validate_permissions(
        request=request,
        userid=userid,
        permission_type='limpeza_predial',
        permission_to_access=['320: Pode agendar novos serviços']
    )

    if request.method == 'POST':
        form = ServicoLimpezaPredialAgendadoForms(request.POST, request.FILES, request=request, userid=userid)
        if form.is_valid():
            form.save()
            messages.info(
                request=request,
                message=f'Serviço(s) '
                        f'{", ".join([str(servico) for servico in form.cleaned_data["ServicosEscalados"].all()])} '
                        f'em {form.cleaned_data["Areas"]} agendado.'
            )

            return redirect('agendar_servico_limpeza_predial', type, userid)

        messages.error(
            request=request,
            message=f'Algo de errado'
        )

    redirect_close_button = None

    if type == 'calendario':
        redirect_close_button = reverse('calendario_limpeza_predial', kwargs={'userid': userid})

    return render(
        request=request,
        template_name='DataTableAndForms/CreateObject.html',
        context={
            'forms': forms,
            'app_name': 'Confirmar solicitação de limpeza predial',
            'redirect_close_button': redirect_close_button,
            'redirect_url_name': reverse('agendar_servico_limpeza_predial', kwargs={'type': type, 'userid': userid}),
            'text_button_save': 'Agendar Serviço',
            'link_tipos': tipos,
            'permission_crate': permission_crate,
        }
    )