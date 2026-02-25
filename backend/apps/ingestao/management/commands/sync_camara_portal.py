import json
from pathlib import Path

from django.core.management.base import BaseCommand

from apps.ingestao.connectors import fetch_camara_portal


class Command(BaseCommand):
    help = "Consulta snapshot da camara via endpoint init/data do Portal CR2."

    def add_arguments(self, parser):
        parser.add_argument(
            "--url",
            type=str,
            default="https://www.portalcr2.com.br/detalhes-parlamentar/tibau-do-sul",
        )
        parser.add_argument(
            "--output-file",
            type=str,
            default=str(
                Path(__file__).resolve().parents[6]
                / "data"
                / "exports"
                / "camara-init-data.json"
            ),
        )

    def handle(self, *args, **options):
        payload = fetch_camara_portal(options["url"])
        output_file = Path(options["output_file"])
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(
            json.dumps(payload, ensure_ascii=False), encoding="utf-8"
        )
        self.stdout.write(self.style.SUCCESS(f"Snapshot camara salva em {output_file}"))
