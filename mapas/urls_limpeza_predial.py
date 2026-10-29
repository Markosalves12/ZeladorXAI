from django.urls import path
from mapas.views_limpeza_predial import mapas_limpeza_predial

urlpatterns = [
    path('mapas-limpeza_predial/<str:userid>', mapas_limpeza_predial, name='mapas_limpeza_predial'),
    # path('tabeladedados', tabeladedados, name='tabeladedados')
]