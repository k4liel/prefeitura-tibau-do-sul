from rest_framework import serializers

from .models import Alerta


class AlertaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alerta
        fields = ("id", "codigo", "titulo", "severidade", "detalhes", "criado_em")


class JobMetricSerializer(serializers.Serializer):
    fonte = serializers.CharField()
    total_execucoes = serializers.IntegerField()
    falhas = serializers.IntegerField()
    taxa_falha = serializers.FloatField()
    retry_estimado = serializers.IntegerField()
    latencia_media_ms = serializers.IntegerField()
    ultima_execucao = serializers.DateTimeField(allow_null=True)
