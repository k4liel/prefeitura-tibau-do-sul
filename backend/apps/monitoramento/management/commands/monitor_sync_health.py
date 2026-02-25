from django.core.management.base import BaseCommand

from apps.monitoramento.models import Alerta
from apps.monitoramento.services import metricas_jobs


class Command(BaseCommand):
    help = "Avalia saude dos jobs e registra alertas por falha/latencia."

    def add_arguments(self, parser):
        parser.add_argument("--max-failure-rate", type=float, default=30.0)
        parser.add_argument("--max-latency-ms", type=int, default=120000)

    def handle(self, *args, **options):
        max_failure_rate = options["max_failure_rate"]
        max_latency_ms = options["max_latency_ms"]

        created = 0
        for item in metricas_jobs():
            if item["taxa_falha"] > max_failure_rate:
                Alerta.objects.create(
                    codigo=f"job-failure-{item['fonte']}",
                    titulo=f"Taxa de falha alta em {item['fonte']}",
                    severidade="alta",
                    detalhes=(
                        "Taxa de falha "
                        f"{item['taxa_falha']}% acima de {max_failure_rate}%"
                    ),
                )
                created += 1
            if item["latencia_media_ms"] > max_latency_ms:
                Alerta.objects.create(
                    codigo=f"job-latency-{item['fonte']}",
                    titulo=f"Latencia alta em {item['fonte']}",
                    severidade="media",
                    detalhes=(
                        "Latencia media "
                        f"{item['latencia_media_ms']}ms acima de {max_latency_ms}ms"
                    ),
                )
                created += 1

        self.stdout.write(
            self.style.SUCCESS(f"Monitoramento executado. Alertas: {created}")
        )
