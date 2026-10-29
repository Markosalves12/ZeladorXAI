"""Local stdio only: no unauthenticated HTTP endpoint is opened."""
import asyncio
from typing import Literal
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from ai_chat.tools import run_tool, require_user

class Command(BaseCommand):
    help = 'MCP local somente leitura via stdio, vinculado a um gerente existente.'

    def handle(self, *args, **options):
        identity = settings.MCP_USER_ID_RANDOM
        if not identity:
            raise CommandError('Configure MCP_USER_ID_RANDOM com um gerente autorizado. Não há usuário padrão.')
        def user():
            try:
                manager = get_user_model().objects.get(id_random=identity)
                require_user(manager)
                return manager
            except (get_user_model().DoesNotExist, PermissionDenied):
                raise CommandError('Gerente MCP inexistente ou sem acesso ativo.')
        user()
        server = FastMCP('ZeladorX AI')
        annotations = ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=False)
        @server.tool(annotations=annotations)
        async def listar_empresas() -> dict:
            """Lista empresas acessíveis ao gerente configurado no processo local."""
            return await asyncio.to_thread(lambda: run_tool(user(), 'listar_empresas', {}))
        @server.tool(annotations=annotations)
        async def listar_servicos(vertical: Literal['jardinagem', 'limpeza_predial'] = 'jardinagem',
            empresa: str = '', status: str = '', inicio: str = '', fim: str = '', busca: str = '',
            limite: int = 50, offset: int = 0) -> dict:
            """Lista serviços por empresa, período e status, sem duplicação e sem escrita."""
            return await asyncio.to_thread(lambda: run_tool(user(), 'listar_servicos', {'vertical': vertical, 'empresa': empresa, 'status': status, 'inicio': inicio, 'fim': fim, 'busca': busca, 'limite': limite, 'offset': offset}))
        @server.tool(annotations=annotations)
        async def resumir_servicos(vertical: Literal['jardinagem', 'limpeza_predial'] = 'jardinagem',
            empresa: str = '', status: str = '', inicio: str = '', fim: str = '', busca: str = '') -> dict:
            """Conta serviços autorizados; inclui atrasados, sem truncamento de página."""
            return await asyncio.to_thread(lambda: run_tool(user(), 'resumir_servicos', {'vertical': vertical, 'empresa': empresa, 'status': status, 'inicio': inicio, 'fim': fim, 'busca': busca}))
        server.run(transport='stdio')
