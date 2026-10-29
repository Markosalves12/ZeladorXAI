from django.urls import path
from calendario.views_jardinagem import calendario_jardinagem

urlpatterns = [
    path('calendario-jardinagem/<str:userid>', calendario_jardinagem, name='calendario_jardinagem'),
    # path('tabeladedados', tabeladedados, name='tabeladedados')
]