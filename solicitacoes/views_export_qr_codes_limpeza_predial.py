from solicitacoes.utils import generic_export_qr_code_pdf, generic_export_qr_code_png

def exportar_qr_code_limpeza_predial_png(request, id_random):
    from .models import QRCodeAreaLimpezaPredial
    return generic_export_qr_code_png(
        request,
        model=QRCodeAreaLimpezaPredial,
        id_random=id_random,
        filename_prefix="limpeza_predial"
    )



def exportar_qr_code_limpeza_predial_pdf(request, id_random):
    from .models import QRCodeAreaLimpezaPredial
    return generic_export_qr_code_pdf(
        request,
        model=QRCodeAreaLimpezaPredial,
        id_random=id_random,
        filename_prefix="limpeza_predial"
    )