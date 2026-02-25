import pytest

from apps.ingestao.normalization import (
    fornecedor_dedupe_key,
    normalize_cnpj,
    normalize_text,
    servidor_dedupe_key,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (" secretaria  de saude ", "SECRETARIA DE SAUDE"),
        ("", ""),
        (None, ""),
    ],
)
def test_normalize_text(value, expected):
    assert normalize_text(value) == expected


def test_normalize_cnpj_removes_non_digits():
    assert normalize_cnpj("12.345.678/0001-90") == "12345678000190"


def test_fornecedor_dedupe_key_prefers_cnpj():
    assert (
        fornecedor_dedupe_key("Empresa X", "12.345.678/0001-90")
        == "cnpj:12345678000190"
    )


def test_servidor_dedupe_key_prefers_matricula():
    assert servidor_dedupe_key("Maria", "Saude", "Efetivo", "123") == "mat:123"


def test_servidor_dedupe_key_fallback_composite():
    assert servidor_dedupe_key("Maria", "Saude", "Efetivo", "") == "MARIA|SAUDE|EFETIVO"
