from .models import Servidor


def resumo_pessoal() -> dict:
    return {
        "total_servidores": Servidor.objects.count(),
    }
