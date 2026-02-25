from django.core.management.base import BaseCommand

from apps.legislativo.models import Vereador

VEREADORES = [
    ("Antonio Henrique", "MDB"),
    ("Chiquinho do Munim", "PL"),
    ("Eronaldo Bezerra", "UNIAO"),
    ("Geraldo", "UNIAO"),
    ("Ilana Inacio", "PL"),
    ("Italo Caetano", "REPUBLICANOS"),
    ("Lalinha Galvao", "REPUBLICANOS"),
    ("Leandro Barros", "PL"),
    ("Mano do Camarao", "PL"),
    ("Manoel Padi", "UNIAO"),
    ("Mourinha", "UNIAO"),
]


class Command(BaseCommand):
    help = "Carrega vereadores eleitos de Tibau do Sul (mandato 2025-2028)."

    def handle(self, *args, **options):
        created = 0
        for nome, partido in VEREADORES:
            _, was_created = Vereador.objects.get_or_create(
                nome=nome, mandato="2025-2028", defaults={"partido": partido}
            )
            if was_created:
                created += 1
        self.stdout.write(
            self.style.SUCCESS(f"Vereadores processados. Novos registros: {created}")
        )
