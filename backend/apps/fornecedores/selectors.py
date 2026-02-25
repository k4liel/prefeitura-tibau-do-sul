from .models import Fornecedor


def buscar_por_nome(termo: str):
    return Fornecedor.objects.filter(nome__icontains=termo)
