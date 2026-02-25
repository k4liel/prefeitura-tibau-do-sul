from rest_framework import serializers

from .models import Vereador


class VereadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vereador
        fields = ("id", "nome", "partido", "mandato")
