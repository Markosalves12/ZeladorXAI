"""Read-only catalogue of family tables exposed to the assistant and the local MCP.

Each entry declares the model, the lookup(s) that tie a row to an authorized
EmpresaSecundaria, and an allowlist of fields. Anything not listed here
(passwords, reset tokens, files, other managers' permissions) is never exposed.
"""
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from uuid import UUID

from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Count, Q

from areas.models_jardinagem import AreasJardins
from areas.models_limpeza_predial import AreaLimpezaPredial
from catalogo_de_servicos.models_jardinagem import CatalogodeServicoJardinagem
from catalogo_de_servicos.models_limpeza_predial import CatalogodeServicoLimpezaPredial
from checklists.models import CheckListJardinagem, CheckListLimpezaPredial
from empresaprimaria.models import EmpresaPrimaria
from empresasecundario.models import EmpresaSecundaria
from localidade.models_Jardinagem import LocalidadeJardiangem
from localidade.models_limpeza_predial import LocalidadeLimpezaPredial
from permissionscontrol.models import (PermissionsAccessEspecials, PermissionsAccessJardinagem,
    PermissionsAccessLimpezaPredial)
from servicos.models_jardinagem import (FatoServicoJardinagem, ServicoJardinagemAgendado,
    ServicoJardinagemConfigurado)
from servicos.models_limpeza_predial import (FatoServicoLimpezaPredial, ServicoLimpezaPredialAgendado,
    ServicoLimpezaPredialConfigurado)
from settings.models import SettingServicosGerenteJardinagem, SettingServicosGerenteLimpezaPredial
from solicitacoes.models import (QRCodeAreaJardinagem, QRCodeAreaLimpezaPredial, SolicitacoesJardinagem,
    SolicitacoesLimpezaPredial)
from terrenos.models import Terreno
from unidade.models import Unidade
from vegetacao.models import CatalogoVegetacao

J, L = 'jardinagem', 'limpeza_predial'
SECTOR = {J: 'Jardinagem', L: 'Limpeza predial'}


def T(label, model, vertical, scope, fields, search=None, date_field=None, group=('status',)):
    """scope: lookups (prefix to EmpresaSecundaria) that must ALL match authorized companies."""
    return {'label': label, 'model': model, 'vertical': vertical, 'scope': scope, 'fields': fields,
            'search': search, 'date': date_field, 'group': group}


TABLES = {
    'empresas_primarias': T('Clientes (empresas primárias)', EmpresaPrimaria, None, ('pk_primary',),
        {'id': 'id_random', 'nome': 'nome', 'unidades': 'N_unidades', 'status': 'status'}, 'nome'),
    'empresas_secundarias': T('Times (empresas secundárias)', EmpresaSecundaria, None, ('pk',),
        {'id': 'id_random', 'nome': 'nome', 'status': 'status', 'cliente': 'empresaprimaria__nome'}, 'nome',
        group=('status', 'empresaprimaria__nome')),
    'unidades': T('Unidades (cidades/distritos)', Unidade, None, ('empresasecundaria',),
        {'id': 'id_random', 'nome': 'nome', 'status': 'status'}, 'nome'),
}
for v, Loc, Area, Cat, Conf, Ag, Fato, Chk, QR, Sol in (
    (J, LocalidadeJardiangem, AreasJardins, CatalogodeServicoJardinagem, ServicoJardinagemConfigurado,
     ServicoJardinagemAgendado, FatoServicoJardinagem, CheckListJardinagem, QRCodeAreaJardinagem, SolicitacoesJardinagem),
    (L, LocalidadeLimpezaPredial, AreaLimpezaPredial, CatalogodeServicoLimpezaPredial, ServicoLimpezaPredialConfigurado,
     ServicoLimpezaPredialAgendado, FatoServicoLimpezaPredial, CheckListLimpezaPredial, QRCodeAreaLimpezaPredial,
     SolicitacoesLimpezaPredial)):
    area = ('servico__EmpresaSecundaria', 'localidade__unidade__empresasecundaria')
    areas = tuple('Areas__' + s for s in area)
    place = {'area': 'Areas__nome', 'localidade': 'Areas__localidade__nome', 'unidade': 'Areas__localidade__unidade__nome'}
    TABLES.update({
        f'localidades_{v}': T(f'Localidades/bairros ({SECTOR[v]})', Loc, v, ('unidade__empresasecundaria',),
            {'id': 'id_random', 'nome': 'nome', 'unidade': 'unidade__nome', 'status': 'status'}, 'nome',
            group=('status', 'unidade__nome')),
        f'areas_{v}': T(f'Áreas ({SECTOR[v]})', Area, v, area,
            {'id': 'id_random', 'nome': 'nome', 'dimensao': 'dimensao', 'status': 'status', 'servico': 'servico__nome',
             'localidade': 'localidade__nome', 'unidade': 'localidade__unidade__nome',
             **({'terreno': 'Terreno__nome', 'vegetacao': 'vegetacao__nome', 'periodicidade': 'periodicidade'} if v == J else {})},
            'nome', group=('status', 'localidade__unidade__nome', 'servico__nome')),
        f'catalogo_servicos_{v}': T(f'Catálogo de serviços ({SECTOR[v]})', Cat, v, ('EmpresaSecundaria',),
            {'id': 'id_random', 'nome': 'nome', 'status': 'status', 'time': 'EmpresaSecundaria__nome'}, 'nome'),
        f'servicos_configurados_{v}': T(f'Serviços recorrentes configurados ({SECTOR[v]})', Conf, v, areas,
            {'id': 'id_random', 'status': 'status', 'tempo_planejado': 'tempomedioplanejado', **place}, 'Areas__nome'),
        f'servicos_agendados_{v}': T(f'Serviços agendados ({SECTOR[v]})', Ag, v, areas,
            {'id': 'id_random', 'descricao': 'DescricaoDoServico', 'status': 'status', 'tipo': 'TipoServico',
             'inicio': 'DataDeInicio', 'conclusao': 'DataDeConclusao', **place}, 'DescricaoDoServico', 'DataDeInicio',
            group=('status', 'TipoServico', 'Areas__localidade__unidade__nome')),
        f'acompanhamentos_{v}': T(f'Acompanhamentos de serviço ({SECTOR[v]})', Fato, v, tuple('Servico__' + s for s in areas),
            {'id': 'id_random', 'servico': 'Servico__id_random', 'chegada': 'data_hora_chegada_na_area',
             'retorno': 'data_hora_retorno_area', 'responsavel': 'Gerente__username', 'area': 'Servico__Areas__nome'},
            'Servico__DescricaoDoServico', 'data_hora_chegada_na_area', group=('Gerente__username', 'Servico__Areas__nome')),
        f'checklists_{v}': T(f'Checklists ({SECTOR[v]})', Chk, v, tuple('servico_agendado__' + s for s in areas),
            {'id': 'id_random', 'servico': 'servico_agendado__id_random', 'descricao': 'descricao', 'status': 'status',
             'atualizado_em': 'atualizado_em'}, 'descricao', 'atualizado_em'),
        f'qrcodes_{v}': T(f'QR Codes de área ({SECTOR[v]})', QR, v, areas,
            {'id': 'id_random', 'status': 'status', 'area': 'Areas__nome'}, 'Areas__nome'),
        f'solicitacoes_{v}': T(f'Solicitações via QR Code ({SECTOR[v]})', Sol, v, areas,
            {'id': 'id_random', 'descricao': 'descricao', 'status': 'status', 'criado_em': 'data_criacao', **place},
            'descricao', 'data_criacao'),
    })
TABLES['terrenos'] = T('Terrenos (Jardinagem)', Terreno, J, ('EmpresaSecundaria',),
    {'id': 'id_random', 'nome': 'nome', 'status': 'status', 'time': 'EmpresaSecundaria__nome'}, 'nome')
TABLES['vegetacoes'] = T('Vegetações (Jardinagem)', CatalogoVegetacao, J, ('EmpresaSecundaria',),
    {'id': 'id_random', 'nome': 'nome', 'status': 'status', 'time': 'EmpresaSecundaria__nome'}, 'nome')

FILTERS = {'tabela', 'empresa', 'status', 'busca', 'inicio', 'fim', 'limite', 'offset', 'agrupar_por'}


def plain(value):
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    if isinstance(value, timedelta):
        return str(value)
    if isinstance(value, (Decimal, UUID)):
        return str(value)
    return value


def scoped(user, key, args, companies, can_read):
    if key not in TABLES:
        raise ValidationError('Tabela não permitida. Use listar_tabelas.')
    spec = TABLES[key]
    if spec['vertical'] and not can_read(user, spec['vertical']):
        raise PermissionDenied(f'Sem permissão 322 em {SECTOR[spec["vertical"]]}.')
    allowed = companies(user, SECTOR.get(spec['vertical']))
    if args.get('empresa'):
        allowed = allowed.filter(id_random=args['empresa'])
        if not allowed.exists():
            raise PermissionDenied('Empresa fora do seu acesso.')
    model = spec['model']
    condition = Q()
    for lookup in spec['scope']:
        if lookup == 'pk_primary':
            condition &= Q(pk__in=allowed.values('empresaprimaria_id'))
        elif lookup == 'pk':
            condition &= Q(pk__in=allowed.values('pk'))
        else:
            condition &= Q(**{f'{lookup}__in': allowed})
    # Deduplicate by primary key through a subquery so M2M joins never repeat rows.
    qs = model.objects.filter(pk__in=model.objects.filter(condition).values('pk'))
    if args.get('status'):
        if 'status' not in spec['fields'].values():
            raise ValidationError('Esta tabela não tem status.')
        qs = qs.filter(status=str(args['status'])[:40])
    if args.get('busca'):
        if not isinstance(args['busca'], str) or len(args['busca']) > 120:
            raise ValidationError('Busca deve ter até 120 caracteres.')
        if spec['search']:
            qs = qs.filter(**{f'{spec["search"]}__icontains': args['busca']})
    for name, op in (('inicio', 'gte'), ('fim', 'lte')):
        if args.get(name):
            if not spec['date']:
                raise ValidationError('Esta tabela não tem filtro de data.')
            try:
                day = date.fromisoformat(args[name])
            except (TypeError, ValueError):
                raise ValidationError('Data deve usar AAAA-MM-DD.')
            qs = qs.filter(**{f'{spec["date"]}__date__{op}': day})
    return spec, qs


def list_tables(user, can_read):
    rows = []
    for key, spec in TABLES.items():
        if spec['vertical'] and not can_read(user, spec['vertical']):
            continue
        rows.append({'tabela': key, 'descricao': spec['label'], 'campos': list(spec['fields']),
                     'agrupar_por': list(spec['group']), 'filtro_data': bool(spec['date'])})
    return {'tabelas': rows}


def query_table(user, args, companies, can_read):
    args = dict(args)
    limit, offset = args.pop('limite', 25), args.pop('offset', 0)
    if type(limit) is not int or not 1 <= limit <= 100 or type(offset) is not int or not 0 <= offset <= 10000:
        raise ValidationError('Paginação inválida.')
    spec, qs = scoped(user, args.pop('tabela', None), args, companies, can_read)
    names, lookups = zip(*spec['fields'].items())
    order = [spec['date'], 'pk'] if spec['date'] else ['pk']
    rows = [{n: plain(row[l]) for n, l in zip(names, lookups)}
            for row in qs.order_by(*order).values(*lookups)[offset:offset + limit]]
    return {'total': qs.count(), 'offset': offset, 'limite': limit, 'linhas': rows}


def count_table(user, args, companies, can_read):
    args = dict(args)
    group = args.pop('agrupar_por', None)
    spec, qs = scoped(user, args.pop('tabela', None), args, companies, can_read)
    result = {'total': qs.count()}
    if group:
        if group not in spec['group']:
            raise ValidationError('Agrupamento não permitido para esta tabela.')
        result['grupos'] = [{'valor': plain(r[group]), 'total': r['total']}
                            for r in qs.order_by().values(group).annotate(total=Count('pk')).order_by('-total')[:50]]
    return result


def profile(user, companies, can_read):
    teams = companies(user)
    macro = sorted({s for s in teams.values_list('setor__setor', flat=True) if s})
    perms = {}
    for label, access in (('jardinagem', PermissionsAccessJardinagem), ('limpeza_predial', PermissionsAccessLimpezaPredial),
                          ('especiais', PermissionsAccessEspecials)):
        perms[label] = sorted({p for p in access.objects.filter(Gerente=user)
                               .values_list('Permissions__Permissions', flat=True) if p})
    notifications = {}
    for label, model in (('jardinagem', SettingServicosGerenteJardinagem), ('limpeza_predial', SettingServicosGerenteLimpezaPredial)):
        row = model.objects.filter(Gerente=user).values().first()
        notifications[label] = {k: v for k, v in (row or {}).items() if k.startswith('Notification')}
    return {
        'usuario': {'nome': user.username, 'email': user.email, 'superusuario': user.is_superuser, 'status': user.status},
        'macroservicos_habilitados': macro,
        'leitura_de_dados': {v: can_read(user, v) for v in (J, L)},
        'times': [{'id': t['id_random'], 'nome': t['nome'], 'cliente': t['empresaprimaria__nome'],
                   'setores': sorted({s for s in teams.filter(pk=t['pk']).values_list('setor__setor', flat=True) if s})}
                  for t in teams.order_by('nome').values('pk', 'id_random', 'nome', 'empresaprimaria__nome')[:100]],
        'permissoes': perms,
        'notificacoes': notifications,
        'observacao': 'Superusuário dispensa permissões individuais.' if user.is_superuser else
                      'Lista vazia em uma vertical pode significar acesso por exceção (sem registro).',
    }
