from django.contrib.admin.models import LogEntry
from django.urls import path
from rest_framework.generics import ListAPIView

from apps.common.csv import CSVListExportMixin
from apps.common.permissions import IsAnalistaOrAdmin

from .models import DataProvenance, SyncRun
from .serializers import (
    DataProvenanceSerializer,
    ManualAuditLogSerializer,
    SyncRunSerializer,
)


class SyncRunListAPIView(CSVListExportMixin, ListAPIView):
    queryset = SyncRun.objects.all()
    serializer_class = SyncRunSerializer
    filterset_fields = ("fonte", "status")
    search_fields = ("fonte", "mensagem")
    ordering_fields = ("iniciado_em", "finalizado_em")
    permission_classes = (IsAnalistaOrAdmin,)
    csv_filename = "sync-runs.csv"


class DataProvenanceListAPIView(CSVListExportMixin, ListAPIView):
    queryset = DataProvenance.objects.all()
    serializer_class = DataProvenanceSerializer
    filterset_fields = ("fonte", "recurso", "versao")
    search_fields = ("endpoint", "external_id", "payload_hash")
    ordering_fields = ("coletado_em",)
    permission_classes = (IsAnalistaOrAdmin,)
    csv_filename = "fontes-auditoria.csv"


class ManualAuditLogListAPIView(CSVListExportMixin, ListAPIView):
    queryset = LogEntry.objects.select_related("user", "content_type").all()
    serializer_class = ManualAuditLogSerializer
    filterset_fields = ("user", "content_type", "action_flag")
    search_fields = ("object_repr", "change_message")
    ordering_fields = ("action_time",)
    permission_classes = (IsAnalistaOrAdmin,)
    csv_filename = "auditoria-manual.csv"


urlpatterns = [
    path("status/", SyncRunListAPIView.as_view(), name="ingestao-status"),
    path("fontes/", DataProvenanceListAPIView.as_view(), name="ingestao-fontes"),
    path(
        "auditoria-manual/",
        ManualAuditLogListAPIView.as_view(),
        name="ingestao-auditoria-manual",
    ),
]
