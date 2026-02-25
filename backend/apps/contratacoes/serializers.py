from rest_framework import serializers

from .models import Contrato, Licitacao


class LicitacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Licitacao
        fields = ("id", "certame", "modalidade", "objeto", "valor")


class ContratoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contrato
        fields = ("id", "numero", "empresa", "modalidade", "objeto", "valor")
