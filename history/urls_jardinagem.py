from django.urls import path
from history.views_jardinagem import historico_de_servicos_areas_jardinagem, historico_de_servicos_catologo_de_servicos_jardinagem


urlpatterns = [
    # rota na raiz do sistema
    path(
        'historico-de-servicos-areas-jardinagem/<str:userid>/<str:id_random>/',
         historico_de_servicos_areas_jardinagem,
         name='historico_de_servicos_areas_jardinagem'
    ),
    path(
        'historico-de-servicos-catologo-de-servicos-jardinagem/<str:userid>/<str:id_random>',
         historico_de_servicos_catologo_de_servicos_jardinagem,
         name='historico_de_servicos_catologo_de_servicos_jardinagem'
    ),
]