from django.urls import path
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.csv import CSVListExportMixin

from .models import Servidor
from .serializers import ServidorSerializer
from .services import resumo_pessoal


class ResumoPessoalAPIView(APIView):
    def get(self, request):
        return Response(resumo_pessoal())


class ServidorListAPIView(CSVListExportMixin, ListAPIView):
    queryset = Servidor.objects.all()
    serializer_class = ServidorSerializer
    filterset_fields = ("orgao", "vinculo")
    search_fields = ("nome", "orgao", "vinculo")
    ordering_fields = ("nome", "valor_bruto", "valor_liquido")
    csv_filename = "funcionarios.csv"


urlpatterns = [
    path("resumo/", ResumoPessoalAPIView.as_view(), name="pessoal-resumo"),
    path("funcionarios/", ServidorListAPIView.as_view(), name="pessoal-funcionarios"),
]
