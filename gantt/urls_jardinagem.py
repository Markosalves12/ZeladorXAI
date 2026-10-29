from django.urls import path
from gantt.views_jardinagem import gantt_jardinagem

urlpatterns = [
    path('gantt-jardinagem/<str:userid>', gantt_jardinagem, name='gantt_jardinagem'),
    # path('tabeladedados', tabeladedados, name='tabeladedados')
]