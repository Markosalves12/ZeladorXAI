"""Shared read-only tool boundary for the browser assistant and local MCP."""
from datetime import date
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import connection, transaction
from django.db.models import Count
from django.utils import timezone
from empresasecundario.models import EmpresaSecundaria
from permissionscontrol.models import PermissionsAccessJardinagem, PermissionsAccessLimpezaPredial
from servicos.models_jardinagem import ServicoJardinagemAgendado
from servicos.models_limpeza_predial import ServicoLimpezaPredialAgendado

VERTICALS = {
    'jardinagem': (ServicoJardinagemAgendado, PermissionsAccessJardinagem, 'Jardinagem'),
    'limpeza_predial': (ServicoLimpezaPredialAgendado, PermissionsAccessLimpezaPredial, 'Limpeza predial'),
}
FILTERS = {'vertical', 'empresa', 'status', 'inicio', 'fim', 'busca'}
STATES = {'Agendado', 'Em andamento', 'Concluido', 'Cancelado', 'Atrasado'}

def require_user(user):
    if not user.is_authenticated or not user.is_active or user.status != 'Mobilizado':
        raise PermissionDenied('Usuário sem acesso ativo.')

def companies(user, sector=None):
    require_user(user)
    own = user.empresasecundaria.filter(status='Mobilizado', empresaprimaria__status='Mobilizado')
    if user.is_superuser:
        own = EmpresaSecundaria.objects.filter(empresaprimaria_id__in=own.values('empresaprimaria_id'),
            status='Mobilizado', empresaprimaria__status='Mobilizado')
    if sector:
        own = own.filter(setor__setor=sector, empresaprimaria__setor__setor=sector)
    return own.distinct()

def can_read(user, vertical):
    require_user(user)
    if vertical not in VERTICALS:
        raise ValidationError('Vertical inválida.')
    access = VERTICALS[vertical][1]
    return user.is_superuser or access.objects.filter(Gerente=user,
        Permissions__Permissions='322: Pode visualizar serviços agendados').exists()

def queryset(user, arguments):
    if set(arguments) - FILTERS:
        raise ValidationError('Filtro não permitido.')
    vertical = arguments.get('vertical', 'jardinagem')
    if not can_read(user, vertical):
        raise PermissionDenied('Sem permissão 322 nesta vertical.')
    model, _, sector = VERTICALS[vertical]
    allowed = companies(user, sector)
    if arguments.get('empresa'):
        allowed = allowed.filter(id_random=arguments['empresa'])
        if not allowed.exists():
            raise PermissionDenied('Empresa fora do seu acesso.')
    # The area service's owning company AND its unit must be authorized.
    qs = model.objects.filter(Areas__servico__EmpresaSecundaria__in=allowed,
        Areas__localidade__unidade__empresasecundaria__in=allowed).distinct()
    state = arguments.get('status')
    if state:
        if state not in STATES:
            raise ValidationError('Status inválido.')
        qs = qs.filter(status='Agendado', DataDeInicio__lt=timezone.now()) if state == 'Atrasado' else qs.filter(status=state)
    for key, op in (('inicio', 'gte'), ('fim', 'lte')):
        if arguments.get(key):
            try:
                day = date.fromisoformat(arguments[key])
            except (ValueError, TypeError):
                raise ValidationError('Data deve usar AAAA-MM-DD.')
            qs = qs.filter(**{f'DataDeInicio__date__{op}': day})
    if arguments.get('inicio') and arguments.get('fim') and arguments['inicio'] > arguments['fim']:
        raise ValidationError('Data final anterior à inicial.')
    if arguments.get('busca'):
        if not isinstance(arguments['busca'], str) or len(arguments['busca']) > 120:
            raise ValidationError('Busca deve ter até 120 caracteres.')
        qs = qs.filter(DescricaoDoServico__icontains=arguments['busca'])
    return qs

def serialize(row):
    return {'id': row.id_random, 'descricao': row.DescricaoDoServico,
        'status': row.status, 'inicio': row.DataDeInicio.isoformat() if row.DataDeInicio else None,
        'conclusao': row.DataDeConclusao.isoformat() if row.DataDeConclusao else None,
        'area': row.Areas.nome, 'localidade': row.Areas.localidade.nome,
        'unidade': row.Areas.localidade.unidade.nome}

def run_tool(user, name, arguments):
    require_user(user)
    if not isinstance(arguments, dict):
        raise ValidationError('Argumentos devem ser um objeto.')
    with transaction.atomic():
        if connection.vendor == 'postgresql':
            with connection.cursor() as cursor:
                cursor.execute('SET TRANSACTION READ ONLY')
                cursor.execute("SET LOCAL statement_timeout = '10000ms'")
        if name == 'listar_empresas':
            if arguments:
                raise ValidationError('Esta ferramenta não recebe filtros.')
            return {'empresas': list(companies(user).order_by('pk').values('id_random', 'nome')[:100]), 'limite': 100}
        if name == 'listar_servicos':
            args = dict(arguments)
            limit, offset = args.pop('limite', 50), args.pop('offset', 0)
            if type(limit) is not int or not 1 <= limit <= 100 or type(offset) is not int or not 0 <= offset <= 10000:
                raise ValidationError('Paginação inválida.')
            qs = queryset(user, args).select_related('Areas__localidade__unidade').order_by('DataDeInicio', 'pk')
            return {'total': qs.count(), 'offset': offset, 'limite': limit,
                'servicos': [serialize(row) for row in qs[offset:offset + limit]]}
        if name == 'resumir_servicos':
            qs = queryset(user, arguments)
            # Count a deduplicated ID subquery, not the original multi-company JOIN.
            unique = qs.model.objects.filter(pk__in=qs.values('pk'))
            return {'total': unique.count(), 'por_status': list(unique.order_by().values('status').annotate(total=Count('pk'))),
                'atrasados': unique.filter(status='Agendado', DataDeInicio__lt=timezone.now()).count()}
        raise ValidationError('Ferramenta não permitida.')

PROPERTIES = {
    'vertical': {'type': 'string', 'enum': list(VERTICALS)},
    'empresa': {'type': 'string', 'description': 'id_random de uma empresa permitida'},
    'status': {'type': 'string', 'enum': sorted(STATES)},
    'inicio': {'type': 'string', 'description': 'Data inicial AAAA-MM-DD, inclusive'},
    'fim': {'type': 'string', 'description': 'Data final AAAA-MM-DD, inclusive'},
    'busca': {'type': 'string', 'maxLength': 120},
}
TOOL_SPECS = [
    {'type': 'function', 'function': {'name': 'listar_empresas', 'description': 'Lista os times acessíveis ao usuário atual.',
        'parameters': {'type': 'object', 'properties': {}, 'additionalProperties': False}}},
    {'type': 'function', 'function': {'name': 'listar_servicos', 'description': 'Lista serviços autorizados, com datas e área. Use paginação; não invente IDs.',
        'parameters': {'type': 'object', 'properties': {**PROPERTIES, 'limite': {'type': 'integer', 'minimum': 1, 'maximum': 100},
            'offset': {'type': 'integer', 'minimum': 0, 'maximum': 10000}}, 'additionalProperties': False}}},
    {'type': 'function', 'function': {'name': 'resumir_servicos', 'description': 'Conta todos os serviços autorizados pelos filtros, sem truncar à página.',
        'parameters': {'type': 'object', 'properties': PROPERTIES, 'additionalProperties': False}}},
]
