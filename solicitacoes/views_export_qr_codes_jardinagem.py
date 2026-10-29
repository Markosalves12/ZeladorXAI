from solicitacoes.utils import generic_export_qr_code_pdf, generic_export_qr_code_png

def exportar_qr_code_jardinagem_png(request, id_random):
    from .models import QRCodeAreaJardinagem
    return generic_export_qr_code_png(
        request,
        model=QRCodeAreaJardinagem,
        id_random=id_random,
        filename_prefix="jardinagem"
    )


def exportar_qr_code_jardinagem_pdf(request, id_random):
    from .models import QRCodeAreaJardinagem
    return generic_export_qr_code_pdf(
        request,
        model=QRCodeAreaJardinagem,
        id_random=id_random,
        filename_prefix="jardinagem"
    )