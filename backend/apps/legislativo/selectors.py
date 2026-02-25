from .models import Vereador


def vereadores_ativos():
    return Vereador.objects.all()
