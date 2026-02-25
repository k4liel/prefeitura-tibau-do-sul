from django.urls import path
from django_filters import rest_framework as filters
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.csv import CSVListExportMixin

from .models import DespesaSecretaria
from .serializers import DespesaSecretariaSerializer
from .services import resumo_financeiro


class ResumoFinanceiroAPIView(APIView):
    def get(self, request):
        ano = int(request.query_params.get("ano", 2025))
        return Response(resumo_financeiro(ano=ano))


class DespesaSecretariaFilter(filters.FilterSet):
    ano = filters.NumberFilter(field_name="ano")
    secretaria = filters.CharFilter(field_name="secretaria", lookup_expr="icontains")

    class Meta:
        model = DespesaSecretaria
        fields = ("ano", "secretaria")


class DespesaSecretariaListAPIView(CSVListExportMixin, ListAPIView):
    queryset = DespesaSecretaria.objects.all()
    serializer_class = DespesaSecretariaSerializer
    filterset_class = DespesaSecretariaFilter
    search_fields = ("secretaria",)
    ordering_fields = ("orcamento", "empenhado", "liquidado", "pago")
    csv_filename = "despesas-por-secretaria.csv"

    def get_queryset(self):
        request = getattr(self, "request", None)
        ano_param = request.query_params.get("ano", 2025) if request else 2025
        ano = int(ano_param)
        return DespesaSecretaria.objects.filter(ano=ano).order_by("-orcamento")


urlpatterns = [
    path("resumo/", ResumoFinanceiroAPIView.as_view(), name="financas-resumo"),
    path(
        "por-secretaria/",
        DespesaSecretariaListAPIView.as_view(),
        name="financas-por-secretaria",
    ),
]
