from .models import Contrato, Licitacao


def listar_licitacoes():
    return Licitacao.objects.order_by("-valor")


def listar_contratos():
    return Contrato.objects.order_by("-valor")
