from django.db.models import Sum
from django.urls import path
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.contratacoes.models import Contrato, Licitacao
from apps.financas.models import DespesaSecretaria, ReceitaResumo
from apps.fornecedores.models import Fornecedor
from apps.governanca.models import Secretaria
from apps.legislativo.models import Vereador
from apps.pessoal.models import Servidor


class DashboardOverviewAPIView(APIView):
    def get(self, request):
        ano = int(request.query_params.get("ano", 2025))
        receitas = ReceitaResumo.objects.filter(ano=ano).aggregate(
            arrecadacao=Sum("arrecadacao")
        )
        despesas = DespesaSecretaria.objects.filter(ano=ano).aggregate(pago=Sum("pago"))
        data = {
            "ano": ano,
            "secretarias": Secretaria.objects.count(),
            "vereadores": Vereador.objects.count(),
            "servidores": Servidor.objects.count(),
            "licitacoes": Licitacao.objects.count(),
            "contratos": Contrato.objects.count(),
            "fornecedores": Fornecedor.objects.count(),
            "receita_arrecadada": receitas.get("arrecadacao") or 0,
            "despesa_paga": despesas.get("pago") or 0,
        }
        return Response(data)


urlpatterns = [
    path("overview/", DashboardOverviewAPIView.as_view(), name="dashboard-overview"),
]
