import json
from collections import defaultdict
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum

from apps.contratacoes.models import Contrato, Licitacao
from apps.financas.models import DespesaSecretaria, ReceitaResumo
from apps.fornecedores.models import Fornecedor
from apps.ingestao.normalization import (
    fornecedor_dedupe_key,
    normalize_cnpj,
    normalize_text,
    servidor_dedupe_key,
)
from apps.pessoal.models import Servidor


def as_decimal(value):
    if value is None:
        return Decimal("0")
    return Decimal(str(value))


def as_money(value):
    return as_decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class Command(BaseCommand):
    help = (
        "Valida consistencia numerica entre JSON legado e dados persistidos no banco."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--data-dir",
            type=str,
            default=str(
                Path(__file__).resolve().parents[5]
                / "legacy"
                / "painel-estatico"
                / "site"
                / "data"
            ),
            help="Diretorio contendo os arquivos JSON legados.",
        )

    def handle(self, *args, **options):
        data_dir = Path(options["data_dir"])
        if not data_dir.exists():
            raise CommandError(f"Diretorio nao encontrado: {data_dir}")

        errors = []

        receitas = json.loads(
            (data_dir / "receitas2025.json").read_text(encoding="utf-8")
        )
        despesas = json.loads(
            (data_dir / "despesasOrgao2025.json").read_text(encoding="utf-8")
        )
        licitacoes = json.loads(
            (data_dir / "licitacoes2025.json").read_text(encoding="utf-8")
        )
        contratos = json.loads(
            (data_dir / "contratos2025.json").read_text(encoding="utf-8")
        )
        servidores = json.loads(
            (data_dir / "servidores2025.json").read_text(encoding="utf-8")
        )

        exp_previsao = sum(
            as_money(row.get("vlrPrevisaoAtualizado"))
            for row in receitas.get("data", [])
        )
        exp_arrecadacao = sum(
            as_money(row.get("vlrArrecadacao")) for row in receitas.get("data", [])
        )
        resumo = ReceitaResumo.objects.filter(ano=2025).first()
        db_previsao = as_money(resumo.previsao if resumo else 0)
        db_arrecadacao = as_money(resumo.arrecadacao if resumo else 0)
        if db_previsao != exp_previsao:
            errors.append(
                f"Previsao divergente: db={db_previsao} esperado={exp_previsao}"
            )
        if db_arrecadacao != exp_arrecadacao:
            errors.append(
                "Arrecadacao divergente: "
                f"db={db_arrecadacao} esperado={exp_arrecadacao}"
            )

        despesas_por_secretaria = {}
        for row in despesas.get("data", []):
            if int(row.get("exercicio", 0)) != 2025:
                continue
            key = normalize_text(row.get("txtDescricaoUnidade") or "SEM SECRETARIA")
            despesas_por_secretaria[key] = {
                "orcamento": as_money(row.get("vlrOrcadoAtualizado")),
                "empenhado": as_money(row.get("vlrEmpenhado")),
                "liquidado": as_money(row.get("vlrLiquidado")),
                "pago": as_money(row.get("vlrPago")),
            }
        exp_despesas = defaultdict(lambda: Decimal("0"))
        for row in despesas_por_secretaria.values():
            exp_despesas["orcamento"] += row["orcamento"]
            exp_despesas["empenhado"] += row["empenhado"]
            exp_despesas["liquidado"] += row["liquidado"]
            exp_despesas["pago"] += row["pago"]
        db_despesas = DespesaSecretaria.objects.filter(ano=2025).aggregate(
            orcamento=Sum("orcamento"),
            empenhado=Sum("empenhado"),
            liquidado=Sum("liquidado"),
            pago=Sum("pago"),
        )
        for field in ("orcamento", "empenhado", "liquidado", "pago"):
            db_value = as_money(db_despesas.get(field) or 0)
            if db_value != exp_despesas[field]:
                errors.append(
                    f"Despesa {field} divergente: "
                    f"db={db_value} esperado={exp_despesas[field]}"
                )

        licit_map = {}
        for row in licitacoes.get("data", []):
            key = normalize_text(str(row.get("numCertame") or ""))
            licit_map[key] = as_money(row.get("vlrTotal"))
        exp_licit_total = sum(licit_map.values())
        db_licit_total = as_money(
            Licitacao.objects.aggregate(total=Sum("valor")).get("total") or 0
        )
        if db_licit_total != exp_licit_total:
            errors.append(
                "Total licitacoes divergente: "
                f"db={db_licit_total} esperado={exp_licit_total}"
            )

        contrato_map = {}
        fornecedor_map = defaultdict(lambda: Decimal("0"))
        for row in contratos.get("data", []):
            numero = normalize_text(str(row.get("numContrato") or ""))
            empresa = normalize_text(
                row.get("txtNomeRazaoContratada") or "Nao informado"
            )
            contrato_map[(numero, empresa)] = as_money(row.get("vlrContrato"))

            cnpj = normalize_cnpj(row.get("txtCpfCnpjContratada") or "")
            f_key = fornecedor_dedupe_key(empresa, cnpj)
            fornecedor_map[f_key] += as_money(row.get("vlrContrato"))

        exp_contratos_total = sum(contrato_map.values())
        db_contratos_total = as_money(
            Contrato.objects.aggregate(total=Sum("valor")).get("total") or 0
        )
        if db_contratos_total != exp_contratos_total:
            errors.append(
                "Total contratos divergente: "
                f"db={db_contratos_total} esperado={exp_contratos_total}"
            )

        db_fornecedores_total = as_money(
            Fornecedor.objects.aggregate(total=Sum("valor_total")).get("total") or 0
        )
        exp_fornecedores_total = sum(fornecedor_map.values())
        if db_fornecedores_total != exp_fornecedores_total:
            errors.append(
                "Total fornecedores divergente: "
                f"db={db_fornecedores_total} esperado={exp_fornecedores_total}"
            )

        dezembro = next(
            (item for item in servidores if int(item.get("mes", 0)) == 12),
            {},
        )
        dedupe = {}
        for row in dezembro.get("payload", {}).get("data", []):
            orgao = normalize_text(row.get("orgao") or "SEM ORGAO")
            key = servidor_dedupe_key(
                row.get("nome"), orgao, row.get("vinculo"), row.get("numMatricula")
            )
            dedupe[key] = row
        exp_servidores = len(dedupe)
        db_servidores = Servidor.objects.count()
        if db_servidores != exp_servidores:
            errors.append(
                "Quantidade servidores divergente: "
                f"db={db_servidores} esperado={exp_servidores}"
            )

        if errors:
            raise CommandError("; ".join(errors))

        self.stdout.write(
            self.style.SUCCESS("Consistencia numerica validada com sucesso.")
        )
