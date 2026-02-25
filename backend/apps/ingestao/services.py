from django.utils import timezone

from .models import SyncRun


def iniciar_execucao(fonte: str) -> SyncRun:
    return SyncRun.objects.create(fonte=fonte, status="executando")


def finalizar_execucao(
    run: SyncRun,
    status: str,
    mensagem: str = "",
    registro_count: int = 0,
    erro_count: int = 0,
) -> SyncRun:
    run.status = status
    run.mensagem = mensagem
    run.registro_count = registro_count
    run.erro_count = erro_count
    run.finalizado_em = timezone.now()
    run.save(
        update_fields=[
            "status",
            "mensagem",
            "finalizado_em",
            "registro_count",
            "erro_count",
        ]
    )
    return run
