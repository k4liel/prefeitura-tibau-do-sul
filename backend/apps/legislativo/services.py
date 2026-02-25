from .models import Vereador


def listar_vereadores() -> list[dict]:
    return list(Vereador.objects.values("nome", "partido", "mandato"))
