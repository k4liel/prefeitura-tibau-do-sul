import json
from pathlib import Path

from django.core.management.base import BaseCommand

from apps.ingestao.connectors import fetch_camara_topsolutions


class Command(BaseCommand):
    help = "Sincroniza dados legislativos 2025 via TopSolutions e salva snapshot JSON."

    def add_arguments(self, parser):
        parser.add_argument(
            "--base-url",
            type=str,
            default="https://camaratibaudosul.apitransparencia.topsolutionsrn.com.br",
        )
        parser.add_argument(
            "--output-dir",
            type=str,
            default=str(Path(__file__).resolve().parents[6] / "data" / "exports"),
        )

    def handle(self, *args, **options):
        payload = fetch_camara_topsolutions(options["base_url"])
        output_dir = Path(options["output_dir"])
        output_dir.mkdir(parents=True, exist_ok=True)

        mapping = {
            "vereadores": "camara-vereadores-2025.json",
            "mesa_diretora": "camara-mesa-diretora-2025.json",
            "comissoes": "camara-comissoes-2025.json",
        }
        for key, filename in mapping.items():
            (output_dir / filename).write_text(
                json.dumps(payload.get(key, {}), ensure_ascii=False), encoding="utf-8"
            )

        self.stdout.write(self.style.SUCCESS("Sync camara TopSolutions concluida."))
