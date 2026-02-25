import json
from pathlib import Path

from django.core.management.base import BaseCommand

from apps.ingestao.connectors import (
    fetch_topsolutions_detalhes,
    fetch_ibge_municipio_contexto,
    fetch_topsolutions_operacionais,
    fetch_tce_municipio_contexto,
    fetch_topsolutions_municipio_contexto,
)


class Command(BaseCommand):
    help = "Sincroniza panorama geral do municipio (IBGE + TCE-RN)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output-dir",
            type=str,
            default=str(Path(__file__).resolve().parents[6] / "data" / "exports"),
        )

        parser.add_argument(
            "--output-file",
            type=str,
            default=str(
                Path(__file__).resolve().parents[6]
                / "data"
                / "exports"
                / "municipio-contexto.json"
            ),
        )

    def handle(self, *args, **options):
        output_file = Path(options["output_file"])
        output_dir = Path(options["output_dir"])
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)

        detalhes = fetch_topsolutions_detalhes()
        operacionais = fetch_topsolutions_operacionais()

        payload = {
            "ibge": fetch_ibge_municipio_contexto(),
            "tce_rn": fetch_tce_municipio_contexto(),
            "topsolutions": fetch_topsolutions_municipio_contexto(),
            "topsolutions_operacionais": operacionais,
        }

        output_file.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        (output_dir / "topsolutions-orcamento-2025.json").write_text(
            json.dumps(detalhes.get("orcamento", []), ensure_ascii=False),
            encoding="utf-8",
        )
        (output_dir / "topsolutions-emendas-2025.json").write_text(
            json.dumps(detalhes.get("emendas", []), ensure_ascii=False),
            encoding="utf-8",
        )
        (output_dir / "topsolutions-operacionais-2025.json").write_text(
            json.dumps(operacionais, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        self.stdout.write(
            self.style.SUCCESS(f"Contexto municipal salvo em {output_file}")
        )
