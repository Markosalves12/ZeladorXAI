from django.urls import path
from gantt.views_limpeza_predial import gantt_limpeza_predial

urlpatterns = [
    path('gantt-limpeza-predial/<str:userid>', gantt_limpeza_predial, name='gantt_limpeza_predial'),
]