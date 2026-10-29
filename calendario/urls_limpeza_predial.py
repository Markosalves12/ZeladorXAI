from django.urls import path
from calendario.views_limpeza_predial import calendario_limpeza_predial

urlpatterns = [
    path('calendario-limpeza-predial/<str:userid>', calendario_limpeza_predial, name='calendario_limpeza_predial'),
    # path('tabeladedados', tabeladedados, name='tabeladedados')
]