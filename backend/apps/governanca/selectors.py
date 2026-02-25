from .models import Secretaria


def listar_secretarias():
    return Secretaria.objects.all()
