from django.urls import path
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.csv import CSVListExportMixin

from .models import Secretaria
from .serializers import SecretariaSerializer
from .services import resumo_governanca


class ResumoGovernancaAPIView(APIView):
    def get(self, request):
        return Response(resumo_governanca())


class SecretariaListAPIView(CSVListExportMixin, ListAPIView):
    queryset = Secretaria.objects.all()
    serializer_class = SecretariaSerializer
    filterset_fields = ("nome", "gestor")
    search_fields = ("nome", "gestor")
    ordering_fields = ("nome",)
    csv_filename = "secretarias.csv"


urlpatterns = [
    path("resumo/", ResumoGovernancaAPIView.as_view(), name="governanca-resumo"),
    path(
        "secretarias/", SecretariaListAPIView.as_view(), name="governanca-secretarias"
    ),
]
