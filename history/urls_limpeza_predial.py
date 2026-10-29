from django.urls import path
from history.views_limpeza_predial import (historico_de_servicos_areas_limpeza_predial,
                                           historico_de_servicos_catologo_de_servicos_limpeza_predial)


urlpatterns = [
    # rota na raiz do sistema
    path(
        'historico-de-servicos-areas-limpeza-predial/<str:userid>/<str:id_random>',
         historico_de_servicos_areas_limpeza_predial
         , name='historico_de_servicos_areas_limpeza_predial'
    ),
    path(
        'historico-de-servicos-catologo-de-servicos-limpeza-predial/<str:userid>/<str:id_random>',
        historico_de_servicos_catologo_de_servicos_limpeza_predial,
        name='historico_de_servicos_catologo_de_servicos_limpeza_predial'
    ),
]