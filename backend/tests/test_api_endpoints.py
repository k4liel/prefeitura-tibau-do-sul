import pytest
from django.contrib.admin.models import LogEntry
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.test import Client

from apps.contratacoes.models import Contrato, Licitacao
from apps.financas.models import DespesaSecretaria, ReceitaResumo
from apps.fornecedores.models import Fornecedor
from apps.governanca.models import Secretaria
from apps.ingestao.models import DataProvenance, SyncRun
from apps.legislativo.models import Vereador
from apps.pessoal.models import Servidor

pytestmark = pytest.mark.django_db


def test_api_governanca_resumo():
    client = Client()
    response = client.get("/api/governanca/resumo/")
    assert response.status_code == 200
    assert "prefeito" in response.json()


def test_api_dashboard_overview():
    client = Client()
    response = client.get("/api/dashboard/overview/?ano=2025")
    assert response.status_code == 200
    assert "ano" in response.json()


def test_api_legislativo_vereadores_list():
    Vereador.objects.create(nome="Teste", partido="ABC", mandato="2025-2028")
    client = Client()
    response = client.get("/api/legislativo/vereadores/")
    assert response.status_code == 200
    assert response.json().get("count", 0) >= 1


def test_api_pessoal_funcionarios_list():
    Servidor.objects.create(
        nome="Servidor Teste",
        orgao="SEC. TESTE",
        vinculo="Efetivo",
        valor_bruto=1000,
        valor_liquido=900,
    )
    client = Client()
    response = client.get("/api/pessoal/funcionarios/")
    assert response.status_code == 200
    assert response.json().get("count", 0) >= 1


def test_api_financas_endpoints():
    ReceitaResumo.objects.create(ano=2025, previsao=10, arrecadacao=9)
    DespesaSecretaria.objects.create(
        ano=2025,
        secretaria="SEC. TESTE",
        orcamento=8,
        empenhado=7,
        liquidado=6,
        pago=5,
    )
    client = Client()
    resumo = client.get("/api/financas/resumo/?ano=2025")
    por_secretaria = client.get("/api/financas/por-secretaria/?ano=2025")
    assert resumo.status_code == 200
    assert por_secretaria.status_code == 200


def test_api_monitoramento_jobs_metrics():
    SyncRun.objects.create(fonte="legacy_snapshot", status="sucesso")
    SyncRun.objects.create(fonte="legacy_snapshot", status="erro")
    client = Client()
    response = client.get("/api/monitoramento/jobs/")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert payload
    assert payload[0]["fonte"] == "legacy_snapshot"


def test_api_contratacoes_endpoints():
    Licitacao.objects.create(
        certame="1/2025", modalidade="Pregao", objeto="Teste", valor=100
    )
    Contrato.objects.create(
        numero="10/2025",
        empresa="Empresa X",
        modalidade="Dispensa",
        objeto="Obj",
        valor=200,
    )
    client = Client()
    lic = client.get("/api/contratacoes/licitacoes/")
    ctr = client.get("/api/contratacoes/contratos/")
    assert lic.status_code == 200
    assert ctr.status_code == 200


def test_api_fornecedores_ranking():
    Fornecedor.objects.create(nome="Fornecedor Y", cnpj="00", valor_total=500)
    client = Client()
    response = client.get("/api/fornecedores/ranking/")
    assert response.status_code == 200
    assert response.json().get("count", 0) >= 1


def test_api_ingestao_status():
    SyncRun.objects.create(fonte="teste", status="sucesso")
    User = get_user_model()
    admin = User.objects.create_user("admin", password="admin123")
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()
    client = Client()
    client.force_login(admin)
    response = client.get("/api/ingestao/status/")
    assert response.status_code == 200
    assert response.json().get("count", 0) >= 1


def test_api_ingestao_fontes_requires_admin_and_csv_export():
    DataProvenance.objects.create(
        fonte="legacy_snapshot",
        endpoint="receitas2025.json",
        recurso="receita",
        external_id="x",
        payload_hash="abc",
        versao="v1",
    )
    client = Client()
    unauthorized = client.get("/api/ingestao/fontes/")
    assert unauthorized.status_code in (302, 401, 403)

    User = get_user_model()
    analista = User.objects.create_user("analista", password="analista123")
    client.force_login(analista)
    forbidden = client.get("/api/ingestao/fontes/")
    assert forbidden.status_code == 403

    client.logout()
    admin = User.objects.create_user("admin2", password="admin123")
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()
    client.force_login(admin)
    authorized = client.get("/api/ingestao/fontes/")
    assert authorized.status_code == 200

    csv_response = client.get("/api/ingestao/fontes/?export=csv")
    assert csv_response.status_code == 200
    assert csv_response["Content-Type"].startswith("text/csv")


def test_api_ingestao_auditoria_manual_requires_privileged_user():
    User = get_user_model()
    model_type = ContentType.objects.get_for_model(Fornecedor)
    admin_user = User.objects.create_user("admin-audit", password="admin123")
    admin_user.is_staff = True
    admin_user.save()
    LogEntry.objects.create(
        user_id=admin_user.pk,
        content_type_id=model_type.pk,
        object_id="1",
        object_repr="Fornecedor Teste",
        action_flag=2,
        change_message="Atualizacao manual",
    )

    client = Client()
    unauthorized = client.get("/api/ingestao/auditoria-manual/")
    assert unauthorized.status_code in (302, 401, 403)

    admin = User.objects.create_user("admin-audit2", password="admin123")
    admin.is_staff = True
    admin.save()
    client.force_login(admin)
    response = client.get("/api/ingestao/auditoria-manual/")
    assert response.status_code == 200
    assert response.json().get("count", 0) >= 1


def test_api_ingestao_fontes_allows_analista_group():
    DataProvenance.objects.create(
        fonte="legacy_snapshot",
        endpoint="contratos2025.json",
        recurso="contrato",
        external_id="x-2",
        payload_hash="hash-2",
        versao="v1",
    )
    analista_group = Group.objects.create(name="analista")
    User = get_user_model()
    analista = User.objects.create_user("analista-grupo", password="123")
    analista.groups.add(analista_group)

    client = Client()
    client.force_login(analista)
    response = client.get("/api/ingestao/fontes/")
    assert response.status_code == 200


def test_web_pages_load():
    Secretaria.objects.create(nome="SEC. A")
    Vereador.objects.create(nome="Vereador A", partido="PL", mandato="2025-2028")
    client = Client()
    assert client.get("/").status_code == 200
    assert client.get("/hierarquia/").status_code == 200
    assert client.get("/remuneracoes/").status_code == 200
    assert client.get("/governanca/").status_code == 200
    assert client.get("/legislativo/").status_code == 200
    assert client.get("/financas/").status_code == 200
    assert client.get("/licitacoes/").status_code == 200
    assert client.get("/contratos/").status_code == 200
    assert client.get("/fornecedores/").status_code == 200
    assert client.get("/emendas/").status_code == 200
    assert client.get("/orcamento-detalhado/").status_code == 200
    assert client.get("/secretarias/").status_code == 200
    assert client.get("/funcionarios/").status_code == 200
    assert client.get("/tecnologia/").status_code == 200
    assert client.get("/alertas/").status_code == 200
    assert client.get("/fontes/").status_code in (302, 403)

    User = get_user_model()
    admin = User.objects.create_user("admin-web", password="admin123")
    admin.is_staff = True
    admin.save()
    client.force_login(admin)
    assert client.get("/fontes/").status_code == 200


def test_web_filter_pages_with_query_params():
    Licitacao.objects.create(
        certame="2/2025", modalidade="Pregao", objeto="internet", valor=100
    )
    Contrato.objects.create(
        numero="11/2025",
        empresa="Tech Co",
        modalidade="Dispensa",
        objeto="software",
        valor=200,
    )
    Fornecedor.objects.create(nome="Tech Co", cnpj="123", valor_total=200)
    client = Client()
    assert (
        client.get("/licitacoes/?search=internet&modalidade=Pregao").status_code == 200
    )
    assert client.get("/contratos/?search=software&empresa=Tech").status_code == 200
    assert client.get("/fornecedores/?search=Tech&cnpj=123").status_code == 200
    assert client.get("/alertas/?severidade=alta").status_code == 200
    assert (
        client.get(
            "/funcionarios/?search=Servidor&orgao=SEC&vinculo=Efetivo"
        ).status_code
        == 200
    )


def test_csv_exports_for_core_list_endpoints():
    client = Client()
    urls = [
        "/api/governanca/secretarias/?export=csv",
        "/api/legislativo/vereadores/?export=csv",
        "/api/pessoal/funcionarios/?export=csv",
        "/api/financas/por-secretaria/?export=csv&ano=2025",
        "/api/contratacoes/licitacoes/?export=csv",
        "/api/contratacoes/contratos/?export=csv",
        "/api/fornecedores/ranking/?export=csv",
        "/api/monitoramento/alertas/?export=csv",
    ]
    for url in urls:
        response = client.get(url)
        assert response.status_code == 200
        assert response["Content-Type"].startswith("text/csv")
