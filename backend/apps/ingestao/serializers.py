from django.contrib.admin.models import LogEntry
from rest_framework import serializers

from .models import DataProvenance, SyncRun


class SyncRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = SyncRun
        fields = (
            "id",
            "fonte",
            "status",
            "iniciado_em",
            "finalizado_em",
            "mensagem",
            "registro_count",
            "erro_count",
        )


class DataProvenanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataProvenance
        fields = (
            "id",
            "fonte",
            "endpoint",
            "recurso",
            "external_id",
            "payload_hash",
            "versao",
            "coletado_em",
        )


class ManualAuditLogSerializer(serializers.ModelSerializer):
    usuario = serializers.SerializerMethodField()
    acao = serializers.SerializerMethodField()

    class Meta:
        model = LogEntry
        fields = (
            "id",
            "action_time",
            "usuario",
            "content_type",
            "object_repr",
            "object_id",
            "acao",
            "change_message",
        )

    def get_usuario(self, obj):
        return obj.user.get_username() if obj.user_id else ""

    def get_acao(self, obj):
        if obj.is_addition():
            return "adicao"
        if obj.is_change():
            return "alteracao"
        if obj.is_deletion():
            return "exclusao"
        return "desconhecida"
