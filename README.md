# ZeladorX AI

Plataforma Django da família ZeladorX para conversar com os dados de Jardinagem e Limpeza Predial usando **LM Studio local** e ferramentas **MCP somente leitura**.

## Primeira versão

- Interface de conversa azul/verde, Sora/Manrope, lista lateral e consultas com fontes.
- Login compartilhado com ZeladorX, ChatChannels e Automações. Usuário já autenticado vai para `/`.
- Ferramentas `listar_empresas`, `listar_servicos` e `resumir_servicos`; filtros por vertical, empresa, período, status e descrição.
- Consultas únicas pelo ID com `.distinct()`; resumos calculados sobre todos os IDs filtrados, não sobre uma página.
- Permissão **322** separada por vertical; ausência de permissão bloqueia. Superusuário mantém escopo das empresas primárias às quais já está vinculado; não recebe acesso global.
- Usuários inativos/desmobilizados e empresas desmobilizadas não são consultáveis.
- Nenhuma ferramenta executa SQL recebido, cria, altera, cancela, agenda ou exclui serviços.
- PostgreSQL abre transações de ferramenta em modo somente leitura, com limite de duração.
- MCP inicial **stdio local**, autorizado pelo gerente configurado no processo. Não abre endpoint público nem OAuth remoto.
- Conversas ficam apenas na memória da página nesta etapa; recarregar encerra o histórico. Dados atuais são consultados novamente a cada pergunta.

## Instalar e configurar

```powershell
git clone https://github.com/Markosalves12/ZeladorXAI.git
cd ZeladorXAI
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-ai.txt
Copy-Item .env.example .env
```

Preencha `.env` **localmente**:

1. Copie `SECRET_KEY` e os parâmetros do mesmo PostgreSQL usado pelo ZeladorX. Não invente outro banco nem outra chave.
2. Use o mesmo host nos navegadores: `127.0.0.1` em todos os apps, com portas diferentes.
3. Preserve `SESSION_ENGINE`, `SESSION_COOKIE_NAME`, domínio e caminho da família. O padrão é sessão Django no banco e cookie `sessionid`.
4. Abra o LM Studio, carregue um modelo que suporte **tool calling**, inicie o servidor local e copie seu ID exato para `LMSTUDIO_CHAT_MODEL`.
5. Confirme `LMSTUDIO_URL=http://127.0.0.1:1234/v1`. Autenticação do LM Studio, se habilitada, usa `LMSTUDIO_API_KEY`.

```powershell
python manage.py check
python manage.py check_ai
python manage.py runserver 127.0.0.1:8003
```

Acesse `http://127.0.0.1:8003/`. Não execute migrações compartilhadas por esta plataforma: elas pertencem ao app principal. A primeira versão AI não cria tabelas nem migrações próprias. O banco existente precisa ter as migrações do ZeladorX aplicadas.

**Sair encerra a sessão compartilhada de toda a família**. Tentativa de login inválida não efetua logout da sessão existente. A aplicação preserva os dois caminhos de backend para reconhecer cookies antigos, mas bloqueia explicitamente usuários inativos na interface e nas ferramentas.

## MCP no LM Studio

O MCP local é um processo filho que recebe mensagens via stdio. Quem pode executar o processo ou editar seu `.env` pode usar a identidade nele configurada: use somente em sua máquina confiável. Não o exponha como serviço remoto.

Configure `MCP_USER_ID_RANDOM` com o `id_random` de um gerente existente e autorizado (não e-mail, senha ou usuário escolhido pela IA). Cada ferramenta recarrega esse usuário e revalida o acesso.

No `mcp.json` do LM Studio, ajuste caminhos absolutos:

```json
{
  "mcpServers": {
    "zeladorx-ai": {
      "command": "C:/projetos/ZeladorXAI/.venv/Scripts/python.exe",
      "args": ["C:/projetos/ZeladorXAI/manage.py", "run_mcp"]
    }
  }
}
```

O `.env` é resolvido pela raiz do projeto, independentemente do diretório do processo. Também pode executar `python manage.py run_mcp` para diagnóstico, mas ele espera um cliente MCP; não imprime um menu. Avisos Django são enviados a stderr, não ao protocolo stdio.

## Vetorização

O oraculo fornece o padrão de `/embeddings`; ChatcomLLm fornece o padrão de chat com LM Studio. Nesta etapa as consultas operacionais usam **dados vivos e contagens determinísticas**, não uma cópia vetorizada desatualizada. `ai_chat.lmstudio.embeddings()` fornece o adaptador local e valida lotes/dimensões, mas **não há índice vetorial, ingestão automática nem busca semântica operacional**. Esses recursos precisam de projeto separado por empresa e regras de atualização/exclusão antes de ativação.

## Testes

```powershell
python manage.py test ai_chat --settings=ai_chat.test_settings
```

Os testes usam SQLite temporário e dados sintéticos, sem tocar no PostgreSQL da família nem chamar o seu LM Studio. Execute `check_ai` e uma pergunta real em sua máquina para confirmar o modelo e o banco reais.

## Deploy

Deploy da família continua pela CLI do Heroku. Instale dependências AI e execute `collectstatic --noinput`. Em produção configure `DEBUG=False`, hosts restritos, HTTPS e cookies seguros. Um servidor Heroku **não acessa o LM Studio do seu computador em 127.0.0.1**: para uso inicial, rode ambos localmente. Não publicar o MCP local em HTTP; autenticação remota será uma etapa futura.

## Estrutura

- `setup/`: configuração própria da plataforma AI.
- `ai_chat/`: UI, LM Studio e fronteira única de consultas; MCP usa exatamente as mesmas ferramentas.
- Apps de negócio e migrações: cópias compartilhadas, preservadas sem alteração.
- `requirements-ai.txt`: instalação leve, separada da pilha de relatórios/gráficos copiada do app principal.
