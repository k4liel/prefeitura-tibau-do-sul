from .models import DespesaSecretaria


def despesas_por_secretaria(ano: int = 2025):
    return DespesaSecretaria.objects.filter(ano=ano).order_by("-orcamento")
