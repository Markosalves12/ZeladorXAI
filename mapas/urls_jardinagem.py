from django.urls import path
from mapas.views_jardinagem import mapas_jardinagem

urlpatterns = [
    path('mapas-jardinagem/<str:userid>', mapas_jardinagem, name='mapas_jardinagem'),
    # path('tabeladedados', tabeladedados, name='tabeladedados')
]