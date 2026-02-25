from .models import Fornecedor


def ranking_fornecedores(limite: int = 20):
    return list(Fornecedor.objects.all().values("nome", "cnpj", "valor_total")[:limite])
