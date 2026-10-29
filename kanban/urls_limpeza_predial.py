from django.urls import path
from kanban.views_limpeza_predial import kanban_limpeza_predial

urlpatterns = [
    path('kanban-board-limpeza-predial/<str:userid>', kanban_limpeza_predial, name='kanban_limpeza_predial'),
    # path('tabeladedados', tabeladedados, name='tabeladedados')
]