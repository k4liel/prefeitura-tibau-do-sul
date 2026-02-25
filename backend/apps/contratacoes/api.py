from django.urls import path
from rest_framework.generics import ListAPIView

from apps.common.csv import CSVListExportMixin

from .models import Contrato, Licitacao
from .serializers import ContratoSerializer, LicitacaoSerializer


class LicitacaoListAPIView(CSVListExportMixin, ListAPIView):
    queryset = Licitacao.objects.all().order_by("-valor")
    serializer_class = LicitacaoSerializer
    filterset_fields = ("modalidade",)
    search_fields = ("certame", "objeto")
    ordering_fields = ("valor", "certame")
    csv_filename = "licitacoes.csv"


class ContratoListAPIView(CSVListExportMixin, ListAPIView):
    queryset = Contrato.objects.all().order_by("-valor")
    serializer_class = ContratoSerializer
    filterset_fields = ("modalidade", "empresa")
    search_fields = ("numero", "empresa", "objeto")
    ordering_fields = ("valor", "numero", "empresa")
    csv_filename = "contratos.csv"


urlpatterns = [
    path("licitacoes/", LicitacaoListAPIView.as_view(), name="contratacoes-licitacoes"),
    path("contratos/", ContratoListAPIView.as_view(), name="contratacoes-contratos"),
]
