import json
from pathlib import Path

from django.core.management.base import BaseCommand

from apps.ingestao.connectors import fetch_prefeitura_2025


class Command(BaseCommand):
    help = (
        "Sincroniza dados 2025 da prefeitura via API TopSolutions "
        "e salva snapshot JSON."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--base-url",
            type=str,
            default="https://pmtibausulrn.apitransparencia.topsolutionsrn.com.br",
        )
        parser.add_argument(
            "--output-dir",
            type=str,
            default=str(
                Path(__file__).resolve().parents[6]
                / "legacy"
                / "painel-estatico"
                / "site"
                / "data"
            ),
        )

    def handle(self, *args, **options):
        payload = fetch_prefeitura_2025(options["base_url"])
        output_dir = Path(options["output_dir"])
        output_dir.mkdir(parents=True, exist_ok=True)
        mapping = {
            "receitas": "receitas2025.json",
            "despesas": "despesasOrgao2025.json",
            "licitacoes": "licitacoes2025.json",
            "contratos": "contratos2025.json",
        }
        for key, filename in mapping.items():
            (output_dir / filename).write_text(
                json.dumps(payload.get(key, {}), ensure_ascii=False), encoding="utf-8"
            )
        self.stdout.write(self.style.SUCCESS("Sync prefeitura concluida."))
