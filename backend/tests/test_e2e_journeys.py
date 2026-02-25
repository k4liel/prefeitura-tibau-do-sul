import json
from pathlib import Path

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import Client

pytestmark = pytest.mark.django_db


def _write_json(path: Path, payload: dict | list):
    path.write_text(json.dumps(payload), encoding="utf-8")


def _create_snapshot(tmp_path: Path):
    _write_json(
        tmp_path / "receitas2025.json",
        {
            "data": [
                {
                    "txtClassificacao": "A",
                    "vlrPrevisaoAtualizado": 100,
                    "vlrArrecadacao": 90,
                }
            ]
        },
    )
    _write_json(
        tmp_path / "despesasOrgao2025.json",
        {
            "data": [
                {
                    "exercicio": 2025,
                    "txtDescricaoUnidade": "SEC. TESTE",
                    "vlrOrcadoAtualizado": 80,
                    "vlrEmpenhado": 70,
                    "vlrLiquidado": 60,
                    "vlrPago": 50,
                }
            ]
        },
    )
    _write_json(
        tmp_path / "licitacoes2025.json",
        {
            "data": [
                {
                    "numCertame": "1/2025",
                    "txtModalidadeLicit": "Pregao",
                    "txtObjeto": "Internet",
                    "vlrTotal": 123,
                }
            ]
        },
    )
    _write_json(
        tmp_path / "contratos2025.json",
        {
            "data": [
                {
                    "numContrato": "10/2025",
                    "txtNomeRazaoContratada": "Empresa Teste",
                    "txtCpfCnpjContratada": "00",
                    "txtModalidade": "Dispensa",
                    "txtObjeto": "Software",
                    "vlrContrato": 456,
                }
            ]
        },
    )
    _write_json(
        tmp_path / "servidores2025.json",
        [
            {
                "mes": 12,
                "payload": {
                    "data": [
                        {
                            "nome": "Servidor Teste",
                            "orgao": "SEC. TESTE",
                            "vinculo": "Efetivo",
                            "vlrRemuneracaoBruta": 1000,
                            "vlrRemuAposDescObrig": 900,
                        }
                    ]
                },
            }
        ],
    )


def test_e2e_jornada_publica_da_carga_ao_dashboard(tmp_path):
    _create_snapshot(tmp_path)
    call_command("load_legacy_snapshot", data_dir=str(tmp_path))

    client = Client()
    assert client.get("/").status_code == 200
    assert client.get("/financas/").status_code == 200
    assert client.get("/licitacoes/?search=Internet").status_code == 200
    assert client.get("/contratos/?search=Software").status_code == 200

    api_overview = client.get("/api/dashboard/overview/?ano=2025")
    assert api_overview.status_code == 200
    assert api_overview.json().get("ano") == 2025

    api_csv = client.get("/api/contratacoes/contratos/?export=csv")
    assert api_csv.status_code == 200
    assert api_csv["Content-Type"].startswith("text/csv")


def test_e2e_jornada_analista_com_auditoria(tmp_path):
    _create_snapshot(tmp_path)
    call_command("load_legacy_snapshot", data_dir=str(tmp_path))
    call_command("create_access_profiles")

    User = get_user_model()
    analista = User.objects.create_user("analista-e2e", password="123")
    analista.groups.add(Group.objects.get(name="analista"))

    client = Client()
    client.force_login(analista)

    assert client.get("/api/ingestao/status/").status_code == 200
    assert client.get("/api/ingestao/fontes/").status_code == 200
    assert client.get("/api/ingestao/auditoria-manual/").status_code == 200
    assert client.get("/fontes/").status_code == 200
