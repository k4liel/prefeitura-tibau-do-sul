from .models import Servidor


def servidores_por_orgao(orgao: str):
    return Servidor.objects.filter(orgao=orgao)
