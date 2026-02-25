import json

import pytest
from django.core.management import call_command

pytestmark = pytest.mark.django_db


def test_sync_prefeitura_topsolutions_command_writes_files(tmp_path, monkeypatch):
    from apps.ingestao.management.commands import sync_prefeitura_topsolutions as cmd

    monkeypatch.setattr(
        cmd,
        "fetch_prefeitura_2025",
        lambda _base_url: {
            "receitas": {"data": []},
            "despesas": {"data": []},
            "licitacoes": {"data": []},
            "contratos": {"data": []},
        },
    )

    call_command("sync_prefeitura_topsolutions", output_dir=str(tmp_path))

    expected_files = [
        "receitas2025.json",
        "despesasOrgao2025.json",
        "licitacoes2025.json",
        "contratos2025.json",
    ]
    for filename in expected_files:
        assert (tmp_path / filename).exists()


def test_sync_camara_topsolutions_command_writes_files(tmp_path, monkeypatch):
    from apps.ingestao.management.commands import sync_camara_topsolutions as cmd

    monkeypatch.setattr(
        cmd,
        "fetch_camara_topsolutions",
        lambda _base_url: {
            "vereadores": {"data": []},
            "mesa_diretora": {"data": []},
            "comissoes": {"data": []},
        },
    )

    call_command("sync_camara_topsolutions", output_dir=str(tmp_path))

    expected_files = [
        "camara-vereadores-2025.json",
        "camara-mesa-diretora-2025.json",
        "camara-comissoes-2025.json",
    ]
    for filename in expected_files:
        assert (tmp_path / filename).exists()


def test_sync_camara_portal_command_writes_file(tmp_path, monkeypatch):
    from apps.ingestao.management.commands import sync_camara_portal as cmd

    monkeypatch.setattr(cmd, "fetch_camara_portal", lambda _url: {"ok": True})
    output_file = tmp_path / "camara-init-data.json"

    call_command("sync_camara_portal", output_file=str(output_file))

    assert output_file.exists()
    assert json.loads(output_file.read_text(encoding="utf-8"))["ok"] is True
