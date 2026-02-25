from django.urls import path
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.csv import CSVListExportMixin

from .models import Alerta
from .serializers import AlertaSerializer, JobMetricSerializer
from .services import metricas_jobs


class AlertaListAPIView(CSVListExportMixin, ListAPIView):
    queryset = Alerta.objects.all()
    serializer_class = AlertaSerializer
    filterset_fields = ("severidade",)
    search_fields = ("codigo", "titulo", "detalhes")
    ordering_fields = ("criado_em",)
    csv_filename = "alertas.csv"


class JobMetricListAPIView(APIView):
    def get(self, request):
        payload = metricas_jobs()
        serializer = JobMetricSerializer(payload, many=True)
        return Response(serializer.data)


urlpatterns = [
    path("alertas/", AlertaListAPIView.as_view(), name="monitoramento-alertas"),
    path("jobs/", JobMetricListAPIView.as_view(), name="monitoramento-jobs"),
]
