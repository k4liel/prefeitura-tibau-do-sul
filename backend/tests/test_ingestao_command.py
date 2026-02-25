import json
from pathlib import Path

import pytest
from django.contrib.auth.models import Group
from django.core.management import call_command

from apps.contratacoes.models import Contrato, Licitacao
from apps.financas.models import DespesaSecretaria, ReceitaResumo
from apps.fornecedores.models import Fornecedor
from apps.ingestao.models import SyncRun
from apps.legislativo.models import Vereador
from apps.pessoal.models import Servidor

pytestmark = pytest.mark.django_db


def _write_json(path: Path, payload: dict | list):
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_load_legacy_snapshot(tmp_path):
    _write_json(
        tmp_path / "receitas2025.json",
        {"data": [{"vlrPrevisaoAtualizado": 100, "vlrArrecadacao": 90}]},
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
                    "txtObjeto": "Objeto",
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
                    "txtObjeto": "Servico",
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

    call_command("load_legacy_snapshot", data_dir=str(tmp_path))

    assert ReceitaResumo.objects.filter(ano=2025).exists()
    assert DespesaSecretaria.objects.filter(ano=2025, secretaria="SEC. TESTE").exists()
    assert Licitacao.objects.filter(certame="1/2025").exists()
    assert Contrato.objects.filter(numero="10/2025").exists()
    assert Fornecedor.objects.filter(nome="EMPRESA TESTE").exists()
    assert Servidor.objects.filter(nome="SERVIDOR TESTE").exists()
    assert Vereador.objects.count() >= 11
    assert SyncRun.objects.filter(fonte="legacy_snapshot", status="sucesso").exists()


def test_create_access_profiles_command():
    call_command("create_access_profiles")

    assert Group.objects.filter(name="publico").exists()
    assert Group.objects.filter(name="analista").exists()
    assert Group.objects.filter(name="admin").exists()

    analista = Group.objects.get(name="analista")
    assert analista.permissions.filter(codename="view_logentry").exists()


def test_validate_legacy_consistency_command(tmp_path):
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
                    "txtObjeto": "Objeto",
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
                    "txtObjeto": "Servico",
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

    call_command("load_legacy_snapshot", data_dir=str(tmp_path))
    call_command("validate_legacy_consistency", data_dir=str(tmp_path))


def test_load_legacy_snapshot_is_idempotent(tmp_path):
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
                    "txtObjeto": "Objeto",
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
                    "txtObjeto": "Servico",
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

    call_command("load_legacy_snapshot", data_dir=str(tmp_path))
    first_counts = {
        "receita": ReceitaResumo.objects.count(),
        "despesa": DespesaSecretaria.objects.count(),
        "licitacao": Licitacao.objects.count(),
        "contrato": Contrato.objects.count(),
        "fornecedor": Fornecedor.objects.count(),
        "servidor": Servidor.objects.count(),
    }

    call_command("load_legacy_snapshot", data_dir=str(tmp_path))
    second_counts = {
        "receita": ReceitaResumo.objects.count(),
        "despesa": DespesaSecretaria.objects.count(),
        "licitacao": Licitacao.objects.count(),
        "contrato": Contrato.objects.count(),
        "fornecedor": Fornecedor.objects.count(),
        "servidor": Servidor.objects.count(),
    }

    assert second_counts == first_counts
