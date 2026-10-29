from django.http import HttpResponse, Http404
import requests
from io import BytesIO
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def generic_export_qr_code_png(
    request,
    *,
    model,
    id_random: str,
    filename_prefix: str
):
    try:
        qr_code = model.objects.get(id_random=id_random)
    except model.DoesNotExist:
        raise Http404("QR Code não encontrado.")

    # abre o arquivo salvo no ImageField
    qr_code.imagem_qr.open("rb")

    # cria a resposta HTTP com o arquivo
    response = HttpResponse(qr_code.imagem_qr.read(), content_type="image/png")
    response["Content-Disposition"] = (
        f'attachment; filename="qr_code_{filename_prefix}_{qr_code.codigo}.png"'
    )

    return response




def generic_export_qr_code_pdf(
    request,
    *,
    model,
    id_random: str,
    filename_prefix: str
):
    try:
        qr_code = model.objects.get(id_random=id_random)
    except model.DoesNotExist:
        raise Http404("QR Code não encontrado.")

    # URL do arquivo salvo no model
    url_qr_code = qr_code.imagem_qr.url

    # Baixar a imagem a partir da URL
    response_img = requests.get(request.build_absolute_uri(url_qr_code))
    img = Image.open(BytesIO(response_img.content))

    # Criar buffer do PDF
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    # Definir posição e tamanho da imagem no PDF
    width, height = A4
    img_width, img_height = img.size

    # Redimensionar proporcionalmente para caber no A4
    max_width = width * 0.6
    max_height = height * 0.6
    scale = min(max_width / img_width, max_height / img_height)
    img_width = int(img_width * scale)
    img_height = int(img_height * scale)

    # Inserir imagem centralizada
    x = (width - img_width) / 2
    y = (height - img_height) / 2
    p.drawInlineImage(img, x, y, img_width, img_height)

    # Finalizar PDF
    p.showPage()
    p.save()

    buffer.seek(0)

    # Resposta HTTP com o PDF
    response = HttpResponse(buffer, content_type="application/pdf")
    response['Content-Disposition'] = (
        f'attachment; filename="qr_code_{filename_prefix}_{qr_code.codigo}.pdf"'
    )

    return response