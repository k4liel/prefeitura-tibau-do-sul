import pytest
from django.test import Client

pytestmark = pytest.mark.django_db


def test_base_template_has_skip_link_and_focus_styles():
    client = Client()
    response = client.get("/")
    content = response.content.decode("utf-8")
    assert "Pular para conteudo principal" in content
    assert "focus-visible" in content


def test_filter_pages_have_explicit_labels_and_table_wrap():
    client = Client()
    urls = ["/licitacoes/", "/contratos/", "/fornecedores/", "/alertas/"]
    for url in urls:
        response = client.get(url)
        content = response.content.decode("utf-8")
        assert response.status_code == 200
        assert 'class="sr-only"' in content
        assert 'class="table-wrap"' in content
