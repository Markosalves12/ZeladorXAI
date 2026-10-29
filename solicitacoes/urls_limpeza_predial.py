from django.urls import path
from solicitacoes.views_qr_codes_limpeza_predial import (qr_codes_limpeza_predial, IfDeleteQRCodeLimpezaPredial,
                                                         DeleteQRCodeLimpezaPredial, editar_qr_codes_limpeza_predial,
                                                         alterar_status_qr_codes_limpeza_predial)
from solicitacoes.views_limpeza_predial import (solicitacoes_limpeza_predial, solicitar_servico_limpeza_predial,
                                                editar_solicitacao_limpeza_predial, reject_solicitacao_limpeza_predial,
                                                accept_solicitacao_limpeza_predial, confirm_solicitacao_limpeza_predial)
from solicitacoes.views_export_qr_codes_limpeza_predial import (exportar_qr_code_limpeza_predial_pdf,
                                                                exportar_qr_code_limpeza_predial_png)

urlpatterns = [
    path(
        'solicitacoes-servico-limpeza-predial/<str:userid>/',
        solicitacoes_limpeza_predial,
        name='solicitacoes_limpeza_predial'
    ),
    path(
        'QRCODE-limpeza-predial/<str:userid>/',
        qr_codes_limpeza_predial,
        name='qr_codes_limpeza_predial'
    ),
    path(
        'solicitar-servico-limpeza-predial/<str:id_randomqr>/<str:id_randomarea>/',
        solicitar_servico_limpeza_predial,
        name='solicitar_servico_limpeza_predial'
    ),
    path(
        'editar-solicitacao-limpeza-predial/<str:userid>/<str:id_random>/',
        editar_solicitacao_limpeza_predial,
        name='editar_solicitacao_limpeza_predial'
    ),

    path(
        'rejeitar-solicitacao-limpeza-predial/<str:userid>/<str:id_random>/',
        reject_solicitacao_limpeza_predial,
        name='reject_solicitacao_limpeza_predial'
    ),

    path(
        'aceitar-solicitacao-limpeza-predial/<str:userid>/<str:id_random>/',
        accept_solicitacao_limpeza_predial,
        name='accept_solicitacao_limpeza_predial'
    ),
    path(
        'confirmar-solicitacao-limpeza-predial/<str:type>/<str:userid>/<str:id_random>/',
        confirm_solicitacao_limpeza_predial,
        name='confirm_solicitacao_limpeza_predial'
    ),
    path(
        'exportar-QRCODE-limpeza-predial.png/<str:id_random>/',
        exportar_qr_code_limpeza_predial_png,
        name='exportar_qr_code_limpeza_predial_png'
    ),
    path(
        'exportar-QRCODE-limpeza-predial.pdf/<str:id_random>/',
        exportar_qr_code_limpeza_predial_pdf,
        name='exportar_qr_code_limpeza_predial_pdf'
    ),

    path('delete-QRCODE-limpeza-predial/<str:userid>/<str:id_random>/', IfDeleteQRCodeLimpezaPredial, name='IfDeleteQRCodeLimpezaPredial'),
    path('DeleteQRCodeLimpezaPredial/<str:id_random>/', DeleteQRCodeLimpezaPredial, name="DeleteQRCodeLimpezaPredial"),
    path('editar-QRCODE-limpeza-predial/<str:userid>/<str:id_random>', editar_qr_codes_limpeza_predial,
         name='editar_qr_codes_limpeza_predial'),
    path('alterar-status-QRCODE-limpeza-predial/<str:userid>/<str:id_random>/<str:new_status>',
         alterar_status_qr_codes_limpeza_predial,
         name='alterar_status_qr_codes_limpeza_predial'
         ),
]