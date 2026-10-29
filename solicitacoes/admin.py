from django.contrib import admin
from solicitacoes.models import (QRCodeAreaJardinagem, SolicitacoesJardinagem,
                                 QRCodeAreaLimpezaPredial, SolicitacoesLimpezaPredial)

# Register your models here.
class QRCodeAreaJardinagemAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_random', 'Areas', 'imagem_qr', 'status', )
    list_display_links = ('id', 'id_random', 'Areas', 'imagem_qr', 'status', )
    search_fields = ('id', 'id_random', 'Areas', 'imagem_qr', 'status', )
    list_filter = ('id', 'id_random', 'Areas', 'imagem_qr', 'status', )

    list_per_page = 20



class SolicitacoesJardinagemAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_random', 'Areas', 'qrcode', 'status', 'data_criacao', 'criado_por', 'aprovado_por', )
    list_display_links = ('id', 'id_random', 'Areas', 'qrcode', 'status', 'data_criacao', 'criado_por', 'aprovado_por', )
    search_fields = ('id_random', 'Areas', 'qrcode', 'status', 'data_criacao', 'criado_por', 'aprovado_por')
    list_filter = ('id_random', 'Areas', 'qrcode', 'status', 'data_criacao', 'criado_por', 'aprovado_por')

    list_per_page = 20


class QRCodeAreaLimpezaPredialAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_random', 'Areas', 'imagem_qr', 'status', )
    list_display_links = ('id', 'id_random', 'Areas', 'imagem_qr', 'status', )
    search_fields = ('id', 'id_random', 'Areas', 'imagem_qr', 'status', )
    list_filter = ('id', 'id_random', 'Areas', 'imagem_qr','status', )

    list_per_page = 20



class SolicitacoesLimpezaPredialAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_random', 'Areas', 'qrcode', 'status', 'data_criacao', 'criado_por', 'aprovado_por', )
    list_display_links = ('id', 'id_random', 'Areas', 'qrcode', 'status', 'data_criacao', 'criado_por', 'aprovado_por', )
    search_fields = ('id_random', 'Areas', 'qrcode', 'status', 'data_criacao', 'criado_por', 'aprovado_por')
    list_filter = ('id_random', 'Areas', 'qrcode', 'status', 'data_criacao', 'criado_por', 'aprovado_por')

    list_per_page = 20

admin.site.register(QRCodeAreaJardinagem, QRCodeAreaJardinagemAdmin)
admin.site.register(SolicitacoesJardinagem, SolicitacoesJardinagemAdmin)
admin.site.register(QRCodeAreaLimpezaPredial, QRCodeAreaLimpezaPredialAdmin)
admin.site.register(SolicitacoesLimpezaPredial, SolicitacoesLimpezaPredialAdmin)