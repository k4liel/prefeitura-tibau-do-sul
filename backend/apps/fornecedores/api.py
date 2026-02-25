from django.urls import path
from rest_framework.generics import ListAPIView

from apps.common.csv import CSVListExportMixin

from .models import Fornecedor
from .serializers import FornecedorSerializer


class FornecedorListAPIView(CSVListExportMixin, ListAPIView):
    queryset = Fornecedor.objects.all().order_by("-valor_total")
    serializer_class = FornecedorSerializer
    filterset_fields = ("cnpj",)
    search_fields = ("nome", "cnpj")
    ordering_fields = ("valor_total", "nome")
    csv_filename = "fornecedores.csv"


urlpatterns = [
    path("ranking/", FornecedorListAPIView.as_view(), name="fornecedores-ranking"),
]
