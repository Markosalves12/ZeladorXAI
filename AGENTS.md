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
