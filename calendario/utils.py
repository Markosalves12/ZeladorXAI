from datetime import timedelta

from django.shortcuts import reverse


def _js_date(data):
    return f"new Date({data.year}, {data.month - 1}, {data.day}, {data.hour}, {data.minute})"


def format_event(servico):
    # Define a cor com base no status_agendamento
    if servico.status == "Em andamento":
        background_color = "#008000"
        border_color = "#008000"
        textColor = "#FFFFFF"

    elif servico.status == "Cancelado":
        background_color = "#808080 "
        border_color = "#808080"
        textColor = "#FFFFFF"

    elif servico.status == "Concluido":
        background_color = "#020d3f  "
        border_color = "#020d3f"
        textColor = "#FFFFFF"

    elif servico.status_agendamento >= 0 and servico.status_agendamento <= 7:
        background_color = "#ffff00"
        border_color = "#ffff00"
        textColor = "#000000"

    elif servico.status_agendamento < 0:
        background_color = "#ff0000"
        border_color = "#ff0000"
        textColor = "#FFFFFF"

    elif servico.status_agendamento > 7:
        background_color = "#14a0b6"
        border_color = "#14a0b6"
        textColor = "#FFFFFF"

    # Serviços ainda não concluídos não têm DataDeConclusao: usa 1h após o início
    inicio = servico.DataDeInicio or servico.DataDeConclusao
    if inicio is None:
        return None
    fim = servico.DataDeConclusao or (inicio + timedelta(hours=1))

    return {
        "id_random": servico.id_random,
        "title": servico.DescricaoDoServico,
        "start": _js_date(inicio),
        "end": _js_date(fim),
        "allDay": "false",
        "backgroundColor": background_color,
        "borderColor": border_color,
        'textColor': textColor,
        'status_agendamento': servico.status_agendamento,
        'status': servico.status,
        'dataconclusao': servico.DataDeConclusao,
    }
