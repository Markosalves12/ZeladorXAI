# ZeladorX

**Sistema completo de gestão de zeladoria: jardinagem e limpeza predial.**

O ZeladorX organiza toda a operação de manutenção de áreas: cadastro de empresas, unidades, localidades e áreas, montagem do catálogo de serviços, escala de colaboradores, agendamento automático, execução em campo, checklists, fotos de entrega, relatórios e dashboards. Tudo gira em torno de um **framework interno de Kanban com 6 estágios**.

![Django](https://img.shields.io/badge/Django-5.1-092E20?logo=django)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-psycopg2-4169E1?logo=postgresql)
![Google Cloud Storage](https://img.shields.io/badge/Storage-Google%20Cloud-4285F4?logo=googlecloud)
![Heroku](https://img.shields.io/badge/Deploy-Heroku-430098?logo=heroku)

---

## Sumário

- [Visão geral](#visão-geral)
- [O Kanban de 6 estágios](#o-kanban-de-6-estágios)
- [Ciclo de vida de um serviço](#ciclo-de-vida-de-um-serviço)
- [Módulos](#módulos)
- [Hierarquia de dados](#hierarquia-de-dados)
- [Permissões](#permissões)
- [Stack técnica](#stack-técnica)
- [Instalação local](#instalação-local)
- [Variáveis de ambiente](#variáveis-de-ambiente)
- [Deploy](#deploy)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Segurança](#segurança)

---

## Visão geral

O sistema atende **duas verticais de serviço** com a mesma base de código. Cada módulo tem uma versão `*_jardinagem` e outra `*_limpeza_predial`:

| Vertical | Exemplos de uso |
|---|---|
| **Jardinagem** | Poda, roçada, irrigação, controle de vegetação, manutenção de terrenos |
| **Limpeza predial** | Limpeza de ambientes, banheiros, fachadas, áreas comuns |

Cada empresa cliente pode ativar uma vertical ou as duas (`habilitar_jardinagem`, `habilitar_limpeza`). O menu, o Kanban e os relatórios se ajustam sozinhos a isso.

---

## O Kanban de 6 estágios

O coração do ZeladorX é o quadro Kanban de serviços (`kanban/`). Cada serviço agendado (`ServicoJardinagemAgendado` / `ServicoLimpezaPredialAgendado`) fica em **um de seis estágios**, divididos em dois grupos.

### Estágios automáticos (controlados pela data)

Enquanto o status do serviço é `Agendado`, o sistema calcula no banco a diferença em dias entre a data de início e o momento atual (`status_agendamento = DataDeInicio − Now()`). O serviço muda de coluna **sozinho**, sem ninguém mexer:

| Estágio | Regra | Cor |
|---|---|---|
| **Agendados** | faltam **mais de 7 dias** (`status_agendamento > 7`) | Azul `#14a0b6` |
| **Próximos** | faltam **de 0 a 7 dias** (`0 ≤ status_agendamento ≤ 7`) | Amarelo `#ffff00` |
| **Atrasados** | a data **já passou** e o serviço não começou (`status_agendamento < 0`) | Vermelho `#ff0000` |

### Estágios manuais (controlados pelo andamento)

Esses estágios mudam por ação de um colaborador ou gestor, conforme as permissões de cada um:

| Estágio | Como entra | Cor |
|---|---|---|
| **Em andamento** | o colaborador **inicia o acompanhamento** do serviço na área | Verde `#008000` |
| **Concluído** | o serviço é **finalizado**, com data de conclusão e foto de entrega | Azul-escuro `#020d3f` |
| **Cancelado** | um usuário autorizado **cancela** o serviço | Cinza `#808080` |

```text
              AUTOMÁTICO (por data)                    MANUAL (por andamento)
  ┌────────────┐   ┌────────────┐   ┌────────────┐
  │ Agendados  │──▶│  Próximos  │──▶│ Atrasados  │
  │   > 7 dias │   │  0–7 dias  │   │  < 0 dias  │
  └─────┬──────┘   └─────┬──────┘   └─────┬──────┘
        │                │                │
        └────────────────┴────────────────┴──▶ ┌──────────────┐    ┌────────────┐
                                               │ Em andamento │──▶ │ Concluído  │
                                               └──────────────┘    └────────────┘
                 (de qualquer estágio aberto) ─────────────────▶   ┌────────────┐
                                                                   │ Cancelado  │
                                                                   └────────────┘
```

As mesmas regras e cores valem para o **Calendário** (`calendario/utils.py`), o **Gantt**, os **Mapas** e os **relatórios em PDF**. Assim a situação de um serviço é igual em qualquer tela.

---

## Ciclo de vida de um serviço

1. **Configuração.** O gestor cria um *Serviço Configurado* (`ServicoJardinagemConfigurado`): a área, os serviços do catálogo, os dias da semana, até 7 horários por dia e o tempo médio planejado.
2. **Agendamento automático.** Todo dia às **00:15** o agendador (`schedules/`) lê as configurações *mobilizadas* e cria os serviços do dia. Ele só considera serviços cuja área, localidade, unidade e item de catálogo estejam todos com status `Mobilizado`.
3. **Agendamentos manuais.** Também dá para criar serviços do tipo **Regular**, **Extra** ou **Automático**, e marcar serviços como compulsórios.
4. **Escala.** Colaboradores são escalados e podem **confirmar** ou **negar** a participação.
5. **Execução.** O colaborador registra chegada e saída da área (`FatoServicoJardinagem`), preenche **checklists** e anexa **fotos** de solicitação e de entrega. As imagens são redimensionadas sozinhas para 500 px.
6. **Conclusão.** O serviço vai para *Concluído* e entra no histórico, nos dashboards e nos relatórios.

---

## Módulos

| Módulo | Função |
|---|---|
| `kanban` | Quadro de 6 estágios, com filtros por área, tipo, serviço, colaborador e datas |
| `calendario` | Visão mensal/semanal dos serviços, com as cores do Kanban |
| `gantt` | Linha do tempo de execução dos serviços |
| `mapas` / `unidade` | Visualização geográfica de unidades e áreas (GeoPandas, Plotly) |
| `servicos` | Serviços configurados, agendados e fatos de execução |
| `catalogo_de_servicos` | Catálogo de serviços de cada vertical |
| `schedules` | Agendador diário que gera serviços a partir das configurações |
| `checklists` | Listas de verificação ligadas aos serviços |
| `solicitacoes` | Pedidos de serviço por **QR Code** fixado em cada área, com exportação dos códigos |
| `retornos` | Retornos e reaberturas de serviços |
| `areas` / `localidade` / `terrenos` / `vegetacao` | Cadastro do espaço físico e das características da área |
| `empresaprimaria` / `empresasecundario` | Estrutura multiempresa: contratante e prestadoras |
| `gerente` | Colaboradores e gestores, com backend de autenticação próprio |
| `permissionscontrol` | Permissões por vertical, com códigos numerados |
| `authenticate` | Login, recuperação de senha por token e controle de sessão |
| `notifications` | Avisos de novos serviços, inclusão de gestores e reset de senha |
| `dashboards` | Dashboard administrativo e de produtividade |
| `relatorios` | Relatórios em **PDF** (com ou sem checklist) e **XLSX** |
| `history` | Histórico e auditoria das operações |
| `medidor` / `processos` | Medições e documentos de processo |
| `settings` / `semana` / `utils` | Configurações gerais, dias da semana e utilitários comuns |

---

## Hierarquia de dados

```text
Empresa primária (contratante)
 └── Empresa secundária (prestadora / contrato)
      └── Unidade
           └── Localidade
                └── Área (jardim / ambiente predial)
                     ├── Serviço configurado  ──(agendador 00:15)──▶ Serviço agendado
                     │                                                 ├── Colaboradores escalados / confirmados / negados
                     │                                                 ├── Checklists
                     │                                                 ├── Fotos de solicitação e entrega
                     │                                                 └── Fatos de execução (chegada / retorno)
                     └── QR Code de solicitação
```

Cada nível tem um status **Mobilizado / Desmobilizado**. Quando um nível é desmobilizado, nenhum serviço é gerado abaixo dele. Todas as consultas são filtradas pelas empresas do usuário logado (`define_empresas`), o que isola os dados de cada cliente.

---

## Permissões

O acesso é controlado por permissões numeradas e separadas por vertical. Alguns exemplos no Kanban:

| Código | Permissão |
|---|---|
| 320 | Pode agendar novos serviços |
| 321 | Pode editar serviços agendados |
| 322 | Pode visualizar serviços agendados |
| 324 | Pode acompanhar serviços agendados |
| 326 | Pode concluir serviços em andamento |
| 328 | Pode cancelar serviços agendados |
| 361 | Pode acompanhar serviços agendados para si próprio (vê só os próprios serviços) |

---

## Stack técnica

- **Backend:** Python 3.11, Django 5.1, Django REST Framework (com token), Django Channels
- **Banco de dados:** PostgreSQL (`psycopg2`, `dj-database-url`)
- **Arquivos:** Google Cloud Storage via `django-storages`
- **Tarefas:** `schedule` (thread diária), `django-background-tasks`
- **Dados e gráficos:** Pandas, NumPy, Plotly, Matplotlib, Kaleido, GeoPandas, PyProj
- **Relatórios:** ReportLab (PDF), OpenPyXL (XLSX)
- **Imagens / QR:** Pillow, `qrcode`
- **Front-end:** templates Django com AdminLTE / Bootstrap
- **Servidor:** Gunicorn (Heroku `Procfile`)

---

## Instalação local

```bash
git clone https://github.com/Markosalves12/zeladorxV2.git
cd zeladorxV2

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt

# configure o .env (veja abaixo)
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
python manage.py runserver
```

Acesse `http://localhost:8000`.

> O agendador diário sobe por `schedules.views.force_updates`. Ele cria uma thread que roda às 00:15 e gera os serviços do dia para as duas verticais.

---

## Variáveis de ambiente

Crie um arquivo `.env` na raiz (**nunca faça commit dele**):

```env
SECRET_KEY=troque-por-uma-chave-segura
DEBUG=False
DATABASE_URL=postgres://usuario:senha@host:5432/zeladorx
GS_BUCKET_NAME=seu-bucket
GOOGLE_APPLICATION_CREDENTIALS=/caminho/seguro/credenciais.json
```

---

## Deploy

O projeto está pronto para Heroku (ou qualquer PaaS compatível):

```text
web: gunicorn setup.wsgi
```

1. Crie o app e adicione um PostgreSQL.
2. Configure as variáveis de ambiente.
3. Faça o deploy e rode `python manage.py migrate`.

---

## Estrutura do projeto

```text
zeladorxV2/
├── setup/              # settings, urls, wsgi/asgi
├── kanban/             # framework Kanban de 6 estágios
├── schedules/          # agendador automático diário
├── servicos/           # configurados, agendados e fatos
├── calendario/ gantt/ mapas/
├── areas/ localidade/ unidade/ terrenos/ vegetacao/
├── empresaprimaria/ empresasecundario/ gerente/
├── permissionscontrol/ authenticate/ notifications/
├── checklists/ solicitacoes/ retornos/ history/
├── dashboards/ relatorios/ medidor/ processos/
├── settings/ semana/ utils/ zeladorx/
├── templates/          # telas (Kanban, calendário, Gantt, mapas, dashboards...)
├── static/             # AdminLTE, plugins e assets
├── manage.py
├── requirements.txt
└── Procfile
```

---

## Segurança

- Não versione `.env` nem arquivos de chave de conta de serviço (`*.json`). Coloque-os no `.gitignore`.
- Se alguma credencial já foi publicada, **troque-a** no provedor (Google Cloud, banco de dados, `SECRET_KEY`).
- Em produção, use `DEBUG=False` e defina `ALLOWED_HOSTS`.

---

## Autor

Desenvolvido por **Markos Alves Pereira**.
