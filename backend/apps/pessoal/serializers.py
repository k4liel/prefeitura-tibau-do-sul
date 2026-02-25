from rest_framework import serializers

from .models import Servidor


class ServidorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servidor
        fields = (
            "id",
            "matricula",
            "nome",
            "orgao",
            "vinculo",
            "valor_bruto",
            "valor_liquido",
        )
