from rest_framework import serializers

from .models import Fornecedor


class FornecedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fornecedor
        fields = ("id", "nome", "cnpj", "valor_total")
