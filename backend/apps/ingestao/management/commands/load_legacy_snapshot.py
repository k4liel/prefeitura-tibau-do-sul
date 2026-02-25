import json
from decimal import Decimal
from hashlib import sha256
from pathlib import Path

from django.core.management.base import BaseCommand

from apps.contratacoes.models import Contrato, Licitacao
from apps.financas.models import DespesaSecretaria, ReceitaResumo
from apps.fornecedores.models import Fornecedor
from apps.governanca.models import Secretaria
from apps.ingestao.models import DataProvenance
from apps.ingestao.normalization import (
    fornecedor_dedupe_key,
    normalize_cnpj,
    normalize_text,
    servidor_dedupe_key,
)
from apps.ingestao.services import finalizar_execucao, iniciar_execucao
from apps.legislativo.models import Vereador
from apps.pessoal.models import Servidor


def as_decimal(value):
    if value is None:
        return Decimal("0")
    return Decimal(str(value))


class Command(BaseCommand):
    help = "Carrega dados da snapshot legada (JSON) para o banco Django."

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
            self.stderr.write(self.style.ERROR(f"Diretorio nao encontrado: {data_dir}"))
            return

        run = iniciar_execucao("legacy_snapshot")
        total_registros = 0
        try:
            total_registros += self._load_vereadores()
            total_registros += self._load_financas(data_dir)
            total_registros += self._load_contratacoes(data_dir)
            total_registros += self._load_fornecedores(data_dir)
            total_registros += self._load_servidores(data_dir)

            finalizar_execucao(
                run,
                "sucesso",
                "Snapshot legada carregada com sucesso",
                registro_count=total_registros,
            )
            self.stdout.write(self.style.SUCCESS("Carga finalizada com sucesso."))
        except Exception as exc:  # noqa: BLE001
            finalizar_execucao(
                run, "erro", str(exc), registro_count=total_registros, erro_count=1
            )
            raise

    def _load_vereadores(self):
        vereadores = [
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
        count = 0
        for nome, partido in vereadores:
            Vereador.objects.update_or_create(
                nome=nome,
                mandato="2025-2028",
                defaults={"partido": partido},
            )
            self._track(
                "manual", "seed_vereadores_2025", "vereador", nome, {"partido": partido}
            )
            count += 1
        return count

    def _load_financas(self, data_dir: Path):
        receitas_payload = json.loads(
            (data_dir / "receitas2025.json").read_text(encoding="utf-8")
        )
        despesas_payload = json.loads(
            (data_dir / "despesasOrgao2025.json").read_text(encoding="utf-8")
        )

        count = 0
        total_previsao = Decimal("0")
        total_arrecadacao = Decimal("0")
        for row in receitas_payload.get("data", []):
            total_previsao += as_decimal(row.get("vlrPrevisaoAtualizado"))
            total_arrecadacao += as_decimal(row.get("vlrArrecadacao"))
            self._track(
                "legacy_snapshot",
                "receitas2025.json",
                "receita",
                str(row.get("txtClassificacao") or "receita"),
                row,
            )
            count += 1

        ReceitaResumo.objects.update_or_create(
            ano=2025,
            defaults={
                "previsao": total_previsao,
                "arrecadacao": total_arrecadacao,
            },
        )

        for row in despesas_payload.get("data", []):
            if int(row.get("exercicio", 0)) != 2025:
                continue
            secretaria_nome = normalize_text(
                row.get("txtDescricaoUnidade") or "SEM SECRETARIA"
            )
            Secretaria.objects.get_or_create(nome=secretaria_nome)
            DespesaSecretaria.objects.update_or_create(
                ano=2025,
                secretaria=secretaria_nome,
                defaults={
                    "orcamento": as_decimal(row.get("vlrOrcadoAtualizado")),
                    "empenhado": as_decimal(row.get("vlrEmpenhado")),
                    "liquidado": as_decimal(row.get("vlrLiquidado")),
                    "pago": as_decimal(row.get("vlrPago")),
                },
            )
            self._track(
                "legacy_snapshot",
                "despesasOrgao2025.json",
                "despesa_secretaria",
                secretaria_nome,
                row,
            )
            count += 1
        return count

    def _load_contratacoes(self, data_dir: Path):
        licitacoes_payload = json.loads(
            (data_dir / "licitacoes2025.json").read_text(encoding="utf-8")
        )
        contratos_payload = json.loads(
            (data_dir / "contratos2025.json").read_text(encoding="utf-8")
        )

        count = 0
        for row in licitacoes_payload.get("data", []):
            Licitacao.objects.update_or_create(
                certame=normalize_text(str(row.get("numCertame") or "")),
                defaults={
                    "modalidade": normalize_text(row.get("txtModalidadeLicit") or ""),
                    "objeto": row.get("txtObjeto") or "",
                    "valor": as_decimal(row.get("vlrTotal")),
                },
            )
            self._track(
                "legacy_snapshot",
                "licitacoes2025.json",
                "licitacao",
                str(row.get("numCertame") or ""),
                row,
            )
            count += 1

        for row in contratos_payload.get("data", []):
            Contrato.objects.update_or_create(
                numero=normalize_text(str(row.get("numContrato") or "")),
                empresa=normalize_text(
                    row.get("txtNomeRazaoContratada") or "Nao informado"
                ),
                defaults={
                    "modalidade": normalize_text(row.get("txtModalidade") or ""),
                    "objeto": row.get("txtObjeto") or "",
                    "valor": as_decimal(row.get("vlrContrato")),
                },
            )
            self._track(
                "legacy_snapshot",
                "contratos2025.json",
                "contrato",
                str(row.get("numContrato") or ""),
                row,
            )
            count += 1
        return count

    def _load_fornecedores(self, data_dir: Path):
        contratos_payload = json.loads(
            (data_dir / "contratos2025.json").read_text(encoding="utf-8")
        )
        acumulado = {}
        count = 0
        for row in contratos_payload.get("data", []):
            nome = normalize_text(row.get("txtNomeRazaoContratada") or "Nao informado")
            cnpj = normalize_cnpj(row.get("txtCpfCnpjContratada") or "")
            key = fornecedor_dedupe_key(nome, cnpj)
            if key not in acumulado:
                acumulado[key] = {
                    "nome": nome,
                    "cnpj": cnpj,
                    "valor_total": Decimal("0"),
                }
            acumulado[key]["valor_total"] += as_decimal(row.get("vlrContrato"))

        for payload in acumulado.values():
            Fornecedor.objects.update_or_create(
                nome=payload["nome"],
                defaults={
                    "cnpj": payload["cnpj"],
                    "valor_total": payload["valor_total"],
                },
            )
            self._track(
                "legacy_snapshot",
                "contratos2025.json",
                "fornecedor",
                payload["cnpj"] or payload["nome"],
                payload,
            )
            count += 1
        return count

    def _load_servidores(self, data_dir: Path):
        servidores_payload = json.loads(
            (data_dir / "servidores2025.json").read_text(encoding="utf-8")
        )
        dezembro = next(
            (item for item in servidores_payload if int(item.get("mes", 0)) == 12), None
        )
        rows = (dezembro or {}).get("payload", {}).get("data", [])

        count = 0
        dedupe = {}
        for row in rows:
            orgao = normalize_text(row.get("orgao") or "SEM ORGAO")
            Secretaria.objects.get_or_create(nome=orgao)
            key = servidor_dedupe_key(
                row.get("nome"), orgao, row.get("vinculo"), row.get("numMatricula")
            )
            dedupe[key] = row

        for row in dedupe.values():
            orgao = normalize_text(row.get("orgao") or "SEM ORGAO")
            Servidor.objects.update_or_create(
                nome=normalize_text(row.get("nome") or ""),
                orgao=orgao,
                defaults={
                    "matricula": normalize_text(str(row.get("numMatricula") or "")),
                    "vinculo": normalize_text(row.get("vinculo") or ""),
                    "valor_bruto": as_decimal(row.get("vlrRemuneracaoBruta")),
                    "valor_liquido": as_decimal(row.get("vlrRemuAposDescObrig")),
                },
            )
            self._track(
                "legacy_snapshot",
                "servidores2025.json",
                "servidor",
                str(row.get("numMatricula") or row.get("nome") or ""),
                row,
            )
            count += 1
        return count

    def _track(
        self, fonte: str, endpoint: str, recurso: str, external_id: str, payload
    ):
        payload_hash = sha256(
            json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str).encode(
                "utf-8"
            )
        ).hexdigest()
        DataProvenance.objects.update_or_create(
            payload_hash=payload_hash,
            defaults={
                "fonte": fonte,
                "endpoint": endpoint,
                "recurso": recurso,
                "external_id": str(external_id)[:120],
                "versao": "v1",
            },
        )
