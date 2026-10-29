from django import template

register = template.Library()

@register.simple_tag
def calcular_total_solicitacoes(habilitar_jardinagem, n_jardinagem, habilitar_limpeza, n_limpeza):
    total = 0
    if habilitar_jardinagem:
        total += n_jardinagem
    if habilitar_limpeza:
        total += n_limpeza
    return total