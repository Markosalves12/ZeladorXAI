import json
from unittest.mock import patch
from django.test import TestCase, Client, override_settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.utils import timezone
from gerente.models import Gerente
from empresaprimaria.models import EmpresaPrimaria
from empresasecundario.models import EmpresaSecundaria
from zeladorx.models import TypeZeladoria
from unidade.models import Unidade
from localidade.models_Jardinagem import LocalidadeJardiangem
from localidade.models_limpeza_predial import LocalidadeLimpezaPredial
from areas.models_jardinagem import AreasJardins
from areas.models_limpeza_predial import AreaLimpezaPredial
from catalogo_de_servicos.models_jardinagem import CatalogodeServicoJardinagem
from catalogo_de_servicos.models_limpeza_predial import CatalogodeServicoLimpezaPredial
from terrenos.models import Terreno
from vegetacao.models import CatalogoVegetacao
from permissionscontrol.models import (PermissionsJardinagem, PermissionsLimpezaPredial,
    PermissionsAccessJardinagem, PermissionsAccessLimpezaPredial)
from servicos.models_jardinagem import ServicoJardinagemAgendado
from servicos.models_limpeza_predial import ServicoLimpezaPredialAgendado
from .tools import run_tool
from .lmstudio import answer, ModelError, embeddings

class AiAccessTests(TestCase):
    def setUp(self):
        self.user = Gerente.objects.create_user(email='synthetic@test.invalid', username='Sintético', password='test-password')
        self.j = TypeZeladoria.objects.create(setor='Jardinagem')
        self.l = TypeZeladoria.objects.create(setor='Limpeza predial')
        self.primary = EmpresaPrimaria.objects.create(nome='Cliente teste', N_unidades=1)
        self.primary.setor.add(self.j,self.l)
        self.company = EmpresaSecundaria.objects.create(nome='Time teste',empresaprimaria=self.primary)
        self.company.setor.add(self.j,self.l)
        self.user.empresasecundaria.add(self.company)
        self.grant('jardinagem'); self.grant('limpeza_predial')
        self.service = self.make_service(self.company)
        self.clean = self.make_service(self.company, 'limpeza_predial')
        self.client.force_login(self.user, backend='gerente.backends.CaseInsensitiveModelBackend')

    def grant(self, vertical):
        access, permission = (PermissionsAccessJardinagem,PermissionsJardinagem) if vertical == 'jardinagem' else (PermissionsAccessLimpezaPredial,PermissionsLimpezaPredial)
        row, _ = access.objects.get_or_create(Gerente=self.user)
        p, _ = permission.objects.get_or_create(Permissions='322: Pode visualizar serviços agendados')
        row.Permissions.add(p)

    def make_service(self, company, vertical='jardinagem'):
        unit = Unidade.objects.create(nome='Unidade teste'); unit.empresasecundaria.add(company)
        if vertical == 'jardinagem':
            catalog = CatalogodeServicoJardinagem.objects.get_or_create(nome='Poda',EmpresaSecundaria=company)[0]
            locality = LocalidadeJardiangem.objects.create(nome='Bairro',lat_med=0,long_med=0,unidade=unit)
            terrain = Terreno.objects.get_or_create(nome='Terreno', EmpresaSecundaria=company)[0]
            vegetation = CatalogoVegetacao.objects.get_or_create(nome='Vegetação', EmpresaSecundaria=company)[0]
            area = AreasJardins.objects.create(nome='Praça',Terreno=terrain,vegetacao=vegetation,servico=catalog,localidade=locality)
            model = ServicoJardinagemAgendado
        else:
            catalog = CatalogodeServicoLimpezaPredial.objects.get_or_create(nome='Limpeza',EmpresaSecundaria=company)[0]
            locality = LocalidadeLimpezaPredial.objects.create(nome='Bairro',lat_med=0,long_med=0,unidade=unit)
            area = AreaLimpezaPredial.objects.create(nome='Prédio',servico=catalog,localidade=locality)
            model = ServicoLimpezaPredialAgendado
        return model.objects.create(Areas=area,DescricaoDoServico='Serviço teste',DataDeInicio=timezone.now())

    def test_jardinagem_permission_322_required(self):
        PermissionsAccessJardinagem.objects.filter(Gerente=self.user).delete()
        with self.assertRaises(PermissionDenied): run_tool(self.user,'listar_servicos',{'vertical':'jardinagem'})

    def test_limpeza_permission_322_required(self):
        PermissionsAccessLimpezaPredial.objects.filter(Gerente=self.user).delete()
        with self.assertRaises(PermissionDenied): run_tool(self.user,'listar_servicos',{'vertical':'limpeza_predial'})

    def test_cross_company_data_excluded(self):
        other = EmpresaPrimaria.objects.create(nome='Outro cliente',N_unidades=1); other.setor.add(self.j,self.l)
        team = EmpresaSecundaria.objects.create(nome='Outro time',empresaprimaria=other); team.setor.add(self.j,self.l)
        self.make_service(team); self.make_service(team,'limpeza_predial')
        for vertical in ['jardinagem','limpeza_predial']:
            self.assertEqual(run_tool(self.user,'listar_servicos',{'vertical':vertical})['total'],1)
            with self.assertRaises(PermissionDenied): run_tool(self.user,'listar_servicos',{'vertical':vertical,'empresa':team.id_random})

    def test_unique_id_for_many_to_many_unit_and_summary(self):
        team = EmpresaSecundaria.objects.create(nome='Segundo time',empresaprimaria=self.primary); team.setor.add(self.j,self.l)
        self.user.empresasecundaria.add(team)
        self.service.Areas.localidade.unidade.empresasecundaria.add(team)
        listed = run_tool(self.user,'listar_servicos',{})
        self.assertEqual([r['id'] for r in listed['servicos']],[self.service.id_random])
        self.assertEqual(listed['total'],1)
        self.assertEqual(run_tool(self.user,'resumir_servicos',{})['por_status'],[{'status':'Agendado','total':1}])

    def test_disabled_vertical_excluded(self):
        self.company.setor.remove(self.l)
        self.assertEqual(run_tool(self.user,'listar_servicos',{'vertical':'limpeza_predial'})['total'],0)

    def test_inactive_user_blocked(self):
        self.user.is_active=False
        with self.assertRaises(PermissionDenied): run_tool(self.user,'listar_empresas',{})

    def test_demobilized_user_blocked(self):
        self.user.status='Desmobilizado'
        with self.assertRaises(PermissionDenied): run_tool(self.user,'listar_empresas',{})

    def test_superuser_not_global(self):
        self.user.is_superuser=True
        self.user.empresasecundaria.clear()
        self.assertEqual(run_tool(self.user,'listar_servicos',{})['total'],0)

    def test_no_write_or_arbitrary_sql(self):
        with self.assertRaises(ValidationError): run_tool(self.user,'execute_sql',{'sql':'DELETE FROM servicos'})
        with self.assertRaises(ValidationError): run_tool(self.user,'listar_servicos',{'model':'gerente'})
        self.assertEqual(ServicoJardinagemAgendado.objects.count(),1)

    def test_response_field_allowlist_and_nullable_dates(self):
        self.clean.DataDeInicio=None; self.clean.save()
        row = run_tool(self.user,'listar_servicos',{'vertical':'limpeza_predial'})['servicos'][0]
        self.assertEqual(set(row),{'id','descricao','status','inicio','conclusao','area','localidade','unidade'})
        self.assertIsNone(row['inicio']); self.assertIsNone(row['conclusao'])

    def test_full_summary_not_page(self):
        self.make_service(self.company)
        self.assertEqual(len(run_tool(self.user,'listar_servicos',{'limite':1})['servicos']),1)
        self.assertEqual(run_tool(self.user,'resumir_servicos',{})['total'],2)

    def test_logged_in_login_redirects_without_logout(self):
        self.assertRedirects(self.client.get('/login/'), '/', fetch_redirect_response=False)
        self.assertEqual(self.client.session['_auth_user_id'],str(self.user.pk))

    def test_invalid_login_does_not_flush_existing_family_session(self):
        self.client.post('/login/',{'username':'bad','password':'bad'})
        self.assertEqual(self.client.session['_auth_user_id'],str(self.user.pk))

    def test_anonymous_api_no_access(self):
        self.assertEqual(Client().post('/ai/perguntar/',json.dumps({'pergunta':'Liste empresas'}),content_type='application/json').status_code,403)

    def test_csrf_required(self):
        client=Client(enforce_csrf_checks=True); client.force_login(self.user)
        self.assertEqual(client.post('/ai/perguntar/',json.dumps({'pergunta':'teste'}),content_type='application/json').status_code,403)

    @patch('ai_chat.lmstudio.request_json')
    def test_model_calls_tool_and_returns_sources(self, call):
        call.side_effect=[{'choices':[{'message':{'role':'assistant','content':None,'tool_calls':[
            {'id':'test-call','type':'function','function':{'name':'resumir_servicos','arguments':'{"vertical":"jardinagem"}'}}]}}]},
            {'choices':[{'message':{'role':'assistant','content':'Há 1 serviço.'}}]}]
        result=answer(self.user,'Quantos serviços?',[])
        self.assertEqual(result['fontes'][0]['resultado']['total'],1)
        self.assertEqual(call.call_args[0][1]['messages'][-1]['role'],'tool')

    @patch('ai_chat.lmstudio.request_json')
    def test_no_unverified_model_answer(self, call):
        call.return_value={'choices':[{'message':{'content':'Existem 1000 serviços.'}}]}
        with self.assertRaises(ModelError): answer(self.user,'Quantos?',[])

    @override_settings(LMSTUDIO_EMBED_MODEL='embedding-test')
    @patch('ai_chat.lmstudio.request_json')
    def test_embeddings_order_and_count(self, call):
        call.return_value={'data':[{'index':1,'embedding':[3,4]},{'index':0,'embedding':[1,2]}]}
        self.assertEqual(embeddings(['a','b']),[[1,2],[3,4]])
