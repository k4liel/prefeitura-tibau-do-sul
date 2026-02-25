from rest_framework import serializers

from .models import DespesaSecretaria, ReceitaResumo


class ReceitaResumoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReceitaResumo
        fields = ("id", "ano", "previsao", "arrecadacao")


class DespesaSecretariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DespesaSecretaria
        fields = (
            "id",
            "ano",
            "secretaria",
            "orcamento",
            "empenhado",
            "liquidado",
            "pago",
        )
