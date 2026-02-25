from django.db.models import Sum

from .models import DespesaSecretaria, ReceitaResumo


def resumo_financeiro(ano: int = 2025) -> dict:
    receitas = ReceitaResumo.objects.filter(ano=ano).aggregate(
        previsao=Sum("previsao"), arrecadacao=Sum("arrecadacao")
    )
    despesas = DespesaSecretaria.objects.filter(ano=ano).aggregate(
        orcamento=Sum("orcamento"),
        empenhado=Sum("empenhado"),
        liquidado=Sum("liquidado"),
        pago=Sum("pago"),
    )
    return {"ano": ano, "receitas": receitas, "despesas": despesas}
