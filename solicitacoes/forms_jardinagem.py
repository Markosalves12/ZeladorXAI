from django import forms
from areas.models_jardinagem import AreasJardins
from empresasecundario.utils import define_empresas
from solicitacoes.models import QRCodeAreaJardinagem, SolicitacoesJardinagem
from areas.models_jardinagem import AreasJardins

class QRCodeAreaJardinagemForms(forms.ModelForm):
    def __init__(self, *args, request, userid=str, type='creat/edit', **kwargs):
        super(QRCodeAreaJardinagemForms, self).__init__(*args, **kwargs)
        # Excluir serviços com status 'Desmobilizado' do queryset
        # Ajustar o queryset do campo 'empresaprimaria'
        empresas = define_empresas(request=request, userid=userid)
        empresas_primarias_ids = empresas['empresas_primarias_ids']
        empresas_secundarias_ids = empresas['empresas_secundarias_ids']

        if userid and type=='creat/edit':
            self.fields['Areas'] = forms.ModelChoiceField(
                queryset=AreasJardins.objects.filter(
                    localidade__unidade__empresasecundaria__empresaprimaria__id_random__in=empresas_primarias_ids,
                    localidade__unidade__empresasecundaria__id_random__in=empresas_secundarias_ids,
                    localidade__unidade__empresasecundaria__status__in=['Mobilizado'],
                    status__in=['Mobilizado'],
                    localidade__status__in=['Mobilizado'],
                    localidade__unidade__status__in=['Mobilizado']
                ).distinct(),
                widget=forms.Select(
                    attrs={
                        'class': 'form-control',
                    }
                ),
                label='Área',
                required=True  # ou False, conforme sua lógica
            )

        if type == 'search':
            for field_name, field in self.fields.items():
                field.required = False

            self.fields['Areas'] = forms.ModelChoiceField(
                queryset=AreasJardins.objects.filter(
                    localidade__unidade__empresasecundaria__empresaprimaria__id_random__in=empresas_primarias_ids,
                    localidade__unidade__empresasecundaria__id_random__in=empresas_secundarias_ids,
                ).distinct(),
                widget=forms.Select(
                    attrs={
                        'class': 'form-control',
                        'style': (
                            'max-height: 40px; overflow-y: auto; max-width: 300px; '
                            'white-space: normal; word-wrap: break-word; overflow-wrap: break-word;'
                        )
                    }
                ),
                label='Área',
                required=False  # ou False, conforme sua lógica
            )

    class Meta:
        model = QRCodeAreaJardinagem
        fields = ['Areas', ]

        labels = {
            'Areas': 'Área',
        }

        widgets = {

        }



class SolicitacoesJardinagemForms(forms.ModelForm):
    def __init__(self, *args, request, id_random=str, userid=str, type='creat/edit',**kwargs):
        super(SolicitacoesJardinagemForms, self).__init__(*args, **kwargs)
        self.fields['Areas'] = forms.ModelChoiceField(
            queryset=AreasJardins.objects.filter(
                id_random = id_random,
                status__in=['Mobilizado'],
            ).distinct(),
            widget=forms.Select(
                attrs={
                    'class': 'form-control',
                }
            ),
            label='Área',
            required=True  # ou False, conforme sua lógica
        )

    class Meta:
        model = SolicitacoesJardinagem
        fields = ['Areas', 'descricao']

        labels = {
            'Areas': 'Área',
            'descricao': 'Descrição'
        }

        widgets = {
            'descricao': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
        }