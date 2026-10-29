from areas.models_jardinagem import AreasJardins
import uuid
import qrcode
from django.db import models
from django.core.files.base import ContentFile
from io import BytesIO
from gerente.models import Gerente
from utils.utils import generate_id_random
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import VerticalGradiantColorMask
from PIL import Image, ImageDraw, ImageFont
from areas.models_limpeza_predial import AreaLimpezaPredial

# Create your models here.
class QRCodeAreaJardinagem(models.Model):
    id_random = models.CharField(
        unique=True,
        default=generate_id_random,
        max_length=20
    )

    Areas = models.ForeignKey(
        to=AreasJardins,
        on_delete=models.CASCADE
    )

    codigo = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    imagem_qr = models.ImageField(
        upload_to="qrcodes/jardinagem",
        null=True,
        blank=True
    )


    status_options = [
        ('Mobilizado', 'Mobilizado'),
        ('Desmobilizado', 'Desmobilizado'),
    ]

    status = models.CharField(
        max_length=60,
        blank=False,
        null=False,
        choices=status_options,
        default='Mobilizado'
    )

    def save(self, *args, **kwargs):
        if not self.imagem_qr:
            # 1. Criar QR Code com gradiente vertical verde
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(
                f"https://zeladorx-971186eceb54.herokuapp.com/solicitar-servico-jardinagem/{self.id_random}/{self.Areas.id_random}/"
            )
            qr.make(fit=True)

            qr_img = qr.make_image(
                image_factory=StyledPilImage,
                color_mask=VerticalGradiantColorMask(
                    top_color=(0, 200, 0),  # Verde mais claro em cima
                    bottom_color=(0, 100, 0)  # Verde mais escuro embaixo
                )
            ).convert("RGB")

            # 2. Preparar para desenhar texto
            draw = ImageDraw.Draw(qr_img)
            try:
                font_title = ImageFont.truetype("arial.ttf", 36)
                font_sub = ImageFont.truetype("arial.ttf", 28)
            except:
                font_title = ImageFont.load_default()
                font_sub = ImageFont.load_default()

            # Nome da área (linha superior)
            area_nome = getattr(self.Areas, "nome", "") or ""
            bbox_area = draw.textbbox((0, 0), area_nome, font=font_sub) if area_nome else (0, 0, 0, 0)
            area_width = bbox_area[2] - bbox_area[0]
            area_height = bbox_area[3] - bbox_area[1]

            # Linha 2: ZeladorX
            text1 = "ZeladorX"
            bbox1 = draw.textbbox((0, 0), text1, font=font_title)
            text1_width = bbox1[2] - bbox1[0]
            text1_height = bbox1[3] - bbox1[1]

            # Buscar nome da empresa
            nome_empresa = (
                               self.Areas.localidade.unidade.empresasecundaria
                               .values_list("empresaprimaria__nome", flat=True)
                               .first()
                           ) or ""

            # Linha 3: Em parceria com {empresa}
            text2 = f"Em parceria com {nome_empresa}" if nome_empresa else ""
            bbox2 = draw.textbbox((0, 0), text2, font=font_sub) if text2 else (0, 0, 0, 0)
            text2_width = bbox2[2] - bbox2[0]
            text2_height = bbox2[3] - bbox2[1]

            # 3. Criar nova imagem com espaço para os textos (em cima e embaixo)
            extra_height_top = area_height + 20
            extra_height_bottom = text1_height + text2_height + 40
            new_img = Image.new(
                "RGB",
                (qr_img.width, qr_img.height + extra_height_top + extra_height_bottom),
                "white"
            )
            # Colar QR no centro vertical
            new_img.paste(qr_img, (0, extra_height_top))

            # 4. Desenhar textos centralizados
            draw_new = ImageDraw.Draw(new_img)

            # Área (em cima do QR)
            if area_nome:
                x_area = (new_img.width - area_width) // 2
                y_area = 10
                draw_new.text((x_area, y_area), area_nome, font=font_sub, fill=(0, 0, 0))

            # "ZeladorX" (abaixo do QR)
            x1 = (new_img.width - text1_width) // 2
            y1 = extra_height_top + qr_img.height + 10
            draw_new.text((x1, y1), text1, font=font_title, fill=(0, 0, 0))

            # "Em parceria com ..."
            if text2:
                x2 = (new_img.width - text2_width) // 2
                y2 = y1 + text1_height + 10
                draw_new.text((x2, y2), text2, font=font_sub, fill=(80, 80, 80))

            # 5. Salvar no campo imagem_qr
            buf = BytesIO()
            new_img.save(buf, format="PNG")
            self.imagem_qr.save(f"{self.codigo}.png", ContentFile(buf.getvalue()), save=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo} | {self.Areas}"



class SolicitacoesJardinagem(models.Model):
    STATUS_CHOICES = [
        ("Pendente", "Pendente"),
        ("Aprovado", "Aprovado"),
        ("Rejeitado", "Rejeitado"),
    ]

    id_random = models.CharField(
        unique=True,
        default=generate_id_random,
        max_length=20
    )

    Areas = models.ForeignKey(
        to=AreasJardins,
        on_delete=models.CASCADE
    )

    qrcode = models.ForeignKey(
        to=QRCodeAreaJardinagem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    descricao = models.TextField(
        max_length=2000,
        null=False,
        blank=False,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pendente"
    )

    data_criacao = models.DateTimeField(
        auto_now_add=True
    )

    criado_por = models.ForeignKey(
        to=Gerente,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="rUSERCreator"
    )

    aprovado_por = models.ForeignKey(
        to=Gerente,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="rUSERAprovals"
    )

    def __str__(self):
        return f"{self.descricao[0:15]} | {self.Areas}"




class QRCodeAreaLimpezaPredial(models.Model):
    id_random = models.CharField(
        unique=True,
        default=generate_id_random,
        max_length=20
    )

    Areas = models.ForeignKey(
        to=AreaLimpezaPredial,
        on_delete=models.CASCADE
    )

    codigo = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    imagem_qr = models.ImageField(
        upload_to="qrcodes/limpeza_predial",
        null=True,
        blank=True
    )

    status_options = [
        ('Mobilizado', 'Mobilizado'),
        ('Desmobilizado', 'Desmobilizado'),
    ]

    status = models.CharField(
        max_length=60,
        blank=False,
        null=False,
        choices=status_options,
        default='Mobilizado'
    )

    def save(self, *args, **kwargs):
        if not self.imagem_qr:
            # 1. Criar QR Code com gradiente vertical azul
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(
                f"https://zeladorx-971186eceb54.herokuapp.com/solicitar-servico-limpeza-predial/{self.id_random}/{self.Areas.id_random}/"
            )
            qr.make(fit=True)

            qr_img = qr.make_image(
                image_factory=StyledPilImage,
                color_mask=VerticalGradiantColorMask(
                    top_color=(0, 0, 139),  # DarkBlue
                    bottom_color=(25, 25, 112)  # MidnightBlue
                )
            ).convert("RGB")

            # 2. Preparar para desenhar textos
            draw = ImageDraw.Draw(qr_img)
            try:
                font_title = ImageFont.truetype("arial.ttf", 36)
                font_sub = ImageFont.truetype("arial.ttf", 28)
            except:
                font_title = ImageFont.load_default()
                font_sub = ImageFont.load_default()

            # Nome da área (linha superior)
            area_nome = getattr(self.Areas, "nome", "") or ""
            bbox_area = draw.textbbox((0, 0), area_nome, font=font_sub) if area_nome else (0, 0, 0, 0)
            area_width = bbox_area[2] - bbox_area[0]
            area_height = bbox_area[3] - bbox_area[1]

            # Texto 1: ZeladorX
            text1 = "ZeladorX"
            bbox1 = draw.textbbox((0, 0), text1, font=font_title)
            text1_width = bbox1[2] - bbox1[0]
            text1_height = bbox1[3] - bbox1[1]

            # Buscar nome da empresa
            nome_empresa = (
                               self.Areas.localidade.unidade.empresasecundaria
                               .values_list("empresaprimaria__nome", flat=True)
                               .first()
                           ) or ""

            # Texto 2: Em parceria com {empresa}
            text2 = f"Em parceria com {nome_empresa}" if nome_empresa else ""
            bbox2 = draw.textbbox((0, 0), text2, font=font_sub) if text2 else (0, 0, 0, 0)
            text2_width = bbox2[2] - bbox2[0]
            text2_height = bbox2[3] - bbox2[1]

            # 3. Criar nova imagem com espaço para textos em cima e embaixo
            extra_height_top = area_height + 20
            extra_height_bottom = text1_height + text2_height + 40
            new_img = Image.new(
                "RGB",
                (qr_img.width, qr_img.height + extra_height_top + extra_height_bottom),
                "white"
            )
            new_img.paste(qr_img, (0, extra_height_top))

            # 4. Desenhar textos centralizados
            draw_new = ImageDraw.Draw(new_img)

            # Nome da área (em cima do QR)
            if area_nome:
                x_area = (new_img.width - area_width) // 2
                y_area = 10
                draw_new.text((x_area, y_area), area_nome, font=font_sub, fill=(0, 0, 0))

            # "ZeladorX" (abaixo do QR)
            x1 = (new_img.width - text1_width) // 2
            y1 = extra_height_top + qr_img.height + 10
            draw_new.text((x1, y1), text1, font=font_title, fill=(0, 0, 0))

            # "Em parceria com ..."
            if text2:
                x2 = (new_img.width - text2_width) // 2
                y2 = y1 + text1_height + 10
                draw_new.text((x2, y2), text2, font=font_sub, fill=(80, 80, 80))

            # 5. Salvar no campo imagem_qr
            buf = BytesIO()
            new_img.save(buf, format="PNG")
            self.imagem_qr.save(f"{self.codigo}.png", ContentFile(buf.getvalue()), save=False)

        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.codigo} | {self.Areas}"



class SolicitacoesLimpezaPredial(models.Model):
    STATUS_CHOICES = [
        ("Pendente", "Pendente"),
        ("Aprovado", "Aprovado"),
        ("Rejeitado", "Rejeitado"),
    ]

    id_random = models.CharField(
        unique=True,
        default=generate_id_random,
        max_length=20
    )

    Areas = models.ForeignKey(
        to=AreaLimpezaPredial,
        on_delete=models.CASCADE
    )

    qrcode = models.ForeignKey(
        to=QRCodeAreaLimpezaPredial,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    descricao = models.TextField(
        max_length=2000,
        null=False,
        blank=False,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pendente"
    )

    data_criacao = models.DateTimeField(
        auto_now_add=True
    )

    criado_por = models.ForeignKey(
        to=Gerente,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="rUSERCreatorlo"
    )

    aprovado_por = models.ForeignKey(
        to=Gerente,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="rUSERAprovalslp"
    )

    def __str__(self):
        return f"{self.descricao[0:15]} | {self.Areas}"