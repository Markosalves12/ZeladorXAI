# ZeladorX engineering rules

- Keep the shared corporate data model and shared-app migrations compatible with ChatChannels and the API repository, because all three products use the same database.
- Extend AdminLTE through `setup/static/dist/css/zeladorx-modern.css` and `setup/static/dist/js/zeladorx-modern.js`, because replacing vendor files makes upgrades and troubleshooting unsafe.
- Keep sidebar expansion state in browser UI state only, because navigation preferences must not require database changes.
- Keep the ZeladorX UI aligned with ChatChannels using the shared blue/green palette, Sora/Manrope typography, light navigation, and modular dashboards, because the products belong to one corporate family.

## Criação rápida em dropdowns (ZeladorX)
- Dropdowns obrigatórios ganham botão "Novo" via `{% zx_quick_create forms %}` (utils/templatetags/zx_quick_create.py) + `dist/js/zeladorx-quick-create.js`; novos cadastros entram em `QUICK_CREATE_ROUTES`. Motivo: um único ponto genérico, sem alterar cada form.
- "Salvar e voltar" é tratado em `generic_view` por `quick_create_redirect`, aceitando só caminhos internos. Motivo: evitar redirecionamento aberto.
- Recolhimento da sidebar respeita `sidebar-collapse`/`sidebar-open` do AdminLTE e é persistido em localStorage (`zeladorx.sidebar.collapsed`).

- Style the four management/admin dashboards through the `zx-dashboard-page` scope and render Plotly figures in the browser, because dashboard presentation must remain isolated from shared business logic and server-side chart rendering.

## ZeladorX AI
- Keep AI routes and integrations in ai_chat, with shared model files and migrations unchanged, because the family shares its business database.
- Register split service model modules from AiChatConfig.ready, because shared apps do not define models.py and must not be modified here.
- Use a single read-only, field-allowlisted tool boundary for both chat and stdio MCP, because model instructions are not authorization.
- Expose tables only through the declarative allowlist in `ai_chat/catalog.py` (company scope lookups + fields), because new tables must stay company-scoped by construction.
- When the model returns no tool calls, ground the answer with keyword-selected tool results instead of failing, because small local models often skip tool calling.
- Bind MCP stdio to an operator-configured existing user and reload its access per call; never expose it as unauthenticated HTTP, because local process trust is not remote authentication.
- Use LM Studio directly from Django and configure exact model IDs through the environment, because this platform targets local inference rather than a hosted provider.
- Own AI styling in ai_chat/static/ai_chat with semantic CSS tokens, because AI presentation must not change shared templates.
