from .models import Alerta


def alertas_criticos():
    return Alerta.objects.filter(severidade="alta")
