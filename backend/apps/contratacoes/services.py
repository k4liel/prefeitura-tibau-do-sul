from .models import Contrato, Licitacao


def totais_contratacoes() -> dict:
    return {
        "licitacoes": Licitacao.objects.count(),
        "contratos": Contrato.objects.count(),
    }
