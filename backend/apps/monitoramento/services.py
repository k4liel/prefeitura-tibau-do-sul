from collections import defaultdict

from apps.ingestao.models import SyncRun

from .models import Alerta


def listar_alertas(limite: int = 50):
    return list(
        Alerta.objects.values(
            "codigo", "titulo", "severidade", "detalhes", "criado_em"
        )[:limite]
    )


def metricas_jobs(limite_por_fonte: int = 30):
    by_fonte = defaultdict(list)
    runs = SyncRun.objects.order_by("-iniciado_em")
    for run in runs:
        if len(by_fonte[run.fonte]) >= limite_por_fonte:
            continue
        by_fonte[run.fonte].append(run)

    metricas = []
    for fonte, fonte_runs in by_fonte.items():
        falhas = [r for r in fonte_runs if r.status == "erro"]
        latencias = []
        for run in fonte_runs:
            if run.finalizado_em and run.iniciado_em:
                latencias.append(
                    int((run.finalizado_em - run.iniciado_em).total_seconds() * 1000)
                )
        total = len(fonte_runs)
        metricas.append(
            {
                "fonte": fonte,
                "total_execucoes": total,
                "falhas": len(falhas),
                "taxa_falha": round((len(falhas) / total) * 100, 2) if total else 0,
                "retry_estimado": len(falhas),
                "latencia_media_ms": (
                    int(sum(latencias) / len(latencias)) if latencias else 0
                ),
                "ultima_execucao": fonte_runs[0].iniciado_em,
            }
        )

    return sorted(metricas, key=lambda item: item["taxa_falha"], reverse=True)
