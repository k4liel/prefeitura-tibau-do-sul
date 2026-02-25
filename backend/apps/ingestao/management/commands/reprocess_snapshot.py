from django.core.management import call_command
from django.core.management.base import BaseCommand

from apps.contratacoes.models import Contrato, Licitacao
from apps.financas.models import DespesaSecretaria, ReceitaResumo
from apps.fornecedores.models import Fornecedor
from apps.governanca.models import Secretaria
from apps.ingestao.models import DataProvenance
from apps.legislativo.models import Vereador
from apps.pessoal.models import Servidor


class Command(BaseCommand):
    help = "Reprocessa snapshot legado com opcao de limpeza previa."

    def add_arguments(self, parser):
        parser.add_argument("--data-dir", type=str, default="")
        parser.add_argument("--truncate", action="store_true")

    def handle(self, *args, **options):
        if options["truncate"]:
            self.stdout.write("Limpando tabelas antes do reprocessamento...")
            DataProvenance.objects.all().delete()
            Servidor.objects.all().delete()
            Fornecedor.objects.all().delete()
            Contrato.objects.all().delete()
            Licitacao.objects.all().delete()
            DespesaSecretaria.objects.all().delete()
            ReceitaResumo.objects.all().delete()
            Secretaria.objects.all().delete()
            Vereador.objects.all().delete()

        kwargs = {}
        if options["data_dir"]:
            kwargs["data_dir"] = options["data_dir"]
        call_command("load_legacy_snapshot", **kwargs)
        self.stdout.write(self.style.SUCCESS("Reprocessamento concluido."))
