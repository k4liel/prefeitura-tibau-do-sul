from celery import shared_task

from .services import finalizar_execucao, iniciar_execucao


@shared_task
def sync_placeholder(fonte: str = "prefeitura"):
    run = iniciar_execucao(fonte)
    finalizar_execucao(run, status="sucesso", mensagem="Job placeholder executado")
    return {"run_id": run.id, "status": "sucesso"}
