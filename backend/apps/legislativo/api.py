from django.urls import path
from rest_framework.generics import ListAPIView

from apps.common.csv import CSVListExportMixin

from .models import Vereador
from .serializers import VereadorSerializer


class VereadorListAPIView(CSVListExportMixin, ListAPIView):
    queryset = Vereador.objects.all()
    serializer_class = VereadorSerializer
    filterset_fields = ("partido", "mandato")
    search_fields = ("nome", "partido")
    ordering_fields = ("nome",)
    csv_filename = "vereadores.csv"


urlpatterns = [
    path("vereadores/", VereadorListAPIView.as_view(), name="legislativo-vereadores"),
]
