"""
Carrega dados da investigação Playwright para o banco Django.

Processa dados de:
- TopSolutions: servidores, receitas, orçamento, emendas
- TCE-RN: licitações, contratos, despesa, receita
- CSV: gestores de secretaria
- Gera alertas analíticos
"""

import csv
import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.contratacoes.models import Contrato, Licitacao
from apps.financas.models import (
    DespesaSecretaria,
    Emenda,
    OrcamentoItem,
    ReceitaResumo,
)
from apps.fornecedores.models import Fornecedor
from apps.governanca.models import Secretaria
from apps.ingestao.models import SyncRun
from apps.ingestao.normalization import normalize_cnpj, normalize_text
from apps.ingestao.services import finalizar_execucao, iniciar_execucao
from apps.monitoramento.models import Alerta
from apps.pessoal.models import Servidor


def _dec(value):
    if value is None:
        return Decimal("0")
    s = str(value).strip()
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return Decimal(s)
    except Exception:
        return Decimal("0")


def _parse_date_br(s):
    """Parse DD/MM/YYYY HH:MM:SS or DD/MM/YYYY."""
    if not s:
        return None
    try:
        return datetime.strptime(s.strip().split(" ")[0], "%d/%m/%Y").date()
    except Exception:
        return None


def _parse_date_iso(s):
    """Parse YYYY-MM-DDTHH:MM:SS or YYYY-MM-DD."""
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "")).date()
    except Exception:
        return None


class Command(BaseCommand):
    help = "Carrega dados da investigação Playwright para o banco Django."

    def add_arguments(self, parser):
        parser.add_argument(
            "--data-dir",
            type=str,
            default=str(
                Path(__file__).resolve().parents[5] / "data" / "investigation"
            ),
        )
        parser.add_argument(
            "--exports-dir",
            type=str,
            default=str(Path(__file__).resolve().parents[5] / "data" / "exports"),
        )

    def handle(self, *args, **options):
        data_dir = Path(options["data_dir"])
        exports_dir = Path(options["exports_dir"])
        if not data_dir.exists():
            self.stderr.write(self.style.ERROR(f"Nao encontrado: {data_dir}"))
            return

        run = iniciar_execucao("investigation_data")
        total = 0
        try:
            total += self._load_tce_licitacoes(data_dir)
            total += self._load_tce_contratos(data_dir)
            total += self._load_tce_despesa(data_dir)
            total += self._load_tce_receita(data_dir)
            total += self._load_ts_emendas(data_dir)
            total += self._load_ts_orcamento(data_dir)
            total += self._load_ts_receita(data_dir)
            total += self._load_ts_servidores(data_dir)
            total += self._load_gestores(exports_dir)
            total += self._fix_sync_runs()
            total += self._generate_alerts()

            finalizar_execucao(
                run, "sucesso", f"Investigation data loaded: {total} registros",
                registro_count=total,
            )
            self.stdout.write(self.style.SUCCESS(f"Carga finalizada: {total} registros"))
        except Exception as exc:
            finalizar_execucao(run, "erro", str(exc), registro_count=total, erro_count=1)
            raise

    def _load_json(self, data_dir, filename):
        fp = data_dir / filename
        if not fp.exists():
            self.stdout.write(f"  SKIP {filename} (nao encontrado)")
            return []
        data = json.loads(fp.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else data.get("data", [])

    # ── TCE-RN Licitações ──────────────────────────────────
    def _load_tce_licitacoes(self, data_dir):
        self.stdout.write("\n=== TCE-RN Licitacoes ===")
        rows = self._load_json(data_dir, "tce-licitacoes-2025-full.json")
        if not rows:
            return 0

        # Deduplicate by (numero, ano) - TCE has multiple lots per licitação
        dedup = {}
        for row in rows:
            num = str(row.get("numeroLicitacao") or "").strip()
            ano = str(row.get("anoLicitacao") or "").strip()
            key = f"{num}-{ano}"
            if key not in dedup:
                dedup[key] = {
                    "certame": num,
                    "ano": int(ano) if ano.isdigit() else None,
                    "modalidade": (row.get("modalidade") or "").strip(),
                    "objeto": (row.get("descricaoObjeto") or "").strip(),
                    "valor": _dec(row.get("valorTotalOrcado")),
                    "data_publicacao": _parse_date_br(
                        row.get("dataPublicacaoLicitacaoPublica")
                    ),
                    "status": (
                        row.get("situacaoProcedimentoLicitacao") or ""
                    ).strip(),
                    "tipo_objeto": (row.get("tipoObjeto") or "").strip(),
                    "link_edital": (row.get("linkEdital") or "").strip()[:500],
                }
            else:
                # Accumulate value from additional lots
                dedup[key]["valor"] += _dec(row.get("valorTotalOrcado"))

        count = 0
        with transaction.atomic():
            for item in dedup.values():
                Licitacao.objects.update_or_create(
                    certame=item["certame"],
                    fonte="tce_rn",
                    defaults={
                        "modalidade": item["modalidade"],
                        "objeto": item["objeto"][:2000],
                        "valor": item["valor"],
                        "ano": item["ano"],
                        "data_publicacao": item["data_publicacao"],
                        "status": item["status"],
                        "tipo_objeto": item["tipo_objeto"],
                        "link_edital": item["link_edital"],
                    },
                )
                count += 1

        self.stdout.write(f"  {count} licitacoes (de {len(rows)} registros TCE)")
        return count

    # ── TCE-RN Contratos ───────────────────────────────────
    def _load_tce_contratos(self, data_dir):
        self.stdout.write("\n=== TCE-RN Contratos ===")
        rows = self._load_json(data_dir, "tce-contratos-full.json")
        if not rows:
            return 0

        count = 0
        fornecedores_acum = {}
        with transaction.atomic():
            for row in rows:
                numero = str(row.get("numeroContrato") or "").strip()
                cnpj = normalize_cnpj(row.get("cpfcnpjContratado") or "")
                empresa = normalize_text(row.get("nomeContratado") or "Nao informado")
                valor = _dec(row.get("valorContrato"))

                Contrato.objects.update_or_create(
                    numero=numero,
                    empresa=empresa,
                    fonte="tce_rn",
                    defaults={
                        "objeto": (row.get("objetoContrato") or "").strip(),
                        "valor": valor,
                        "cnpj": cnpj,
                        "ano": row.get("anoContrato"),
                        "data_inicio": _parse_date_iso(
                            row.get("dataInicioVigencia")
                        ),
                        "data_fim": _parse_date_iso(
                            row.get("dataTerminoVigencia")
                        ),
                        "data_assinatura": _parse_date_iso(
                            row.get("dataDataAssinatura")
                        ),
                        "ativo": bool(row.get("ativo", True)),
                    },
                )
                count += 1

                # Accumulate for fornecedores
                key = cnpj if cnpj else empresa
                if key not in fornecedores_acum:
                    fornecedores_acum[key] = {
                        "nome": empresa,
                        "cnpj": cnpj,
                        "valor_total": Decimal("0"),
                    }
                fornecedores_acum[key]["valor_total"] += valor

            for payload in fornecedores_acum.values():
                Fornecedor.objects.update_or_create(
                    nome=payload["nome"],
                    defaults={
                        "cnpj": payload["cnpj"],
                        "valor_total": payload["valor_total"],
                    },
                )

        self.stdout.write(
            f"  {count} contratos, {len(fornecedores_acum)} fornecedores"
        )
        return count

    # ── TCE-RN Despesa ─────────────────────────────────────
    def _load_tce_despesa(self, data_dir):
        self.stdout.write("\n=== TCE-RN Despesa ===")
        rows = self._load_json(data_dir, "tce-despesa-2025-full.json")
        if not rows:
            return 0

        # Aggregate by category for DespesaSecretaria enrichment
        total_dotacao = sum(_dec(r.get("valorDotacaoInicial")) for r in rows)
        total_dotacao_atualizada = sum(
            _dec(r.get("valorDotacaoAtualizada")) for r in rows
        )
        total_empenhado = sum(_dec(r.get("valorEmpenhoAtePeriodo")) for r in rows)
        total_liquidado = sum(_dec(r.get("valorLiquidacaoAtePeriodo")) for r in rows)
        total_pago = sum(_dec(r.get("valorPagoAtePeriodo")) for r in rows)

        # Update ReceitaResumo with TCE data for comparison
        self.stdout.write(
            f"  TCE Despesa: dotacao={total_dotacao:,.0f} "
            f"empenhado={total_empenhado:,.0f} "
            f"liquidado={total_liquidado:,.0f} "
            f"pago={total_pago:,.0f}"
        )
        return len(rows)

    # ── TCE-RN Receita ─────────────────────────────────────
    def _load_tce_receita(self, data_dir):
        self.stdout.write("\n=== TCE-RN Receita ===")
        rows = self._load_json(data_dir, "tce-receita-2025-full.json")
        if not rows:
            return 0

        total_previsto = sum(_dec(r.get("valorPrevistoAtualizado")) for r in rows)
        total_realizado = sum(_dec(r.get("valorRealizadoNoExecicio")) for r in rows)

        ReceitaResumo.objects.update_or_create(
            ano=2025,
            defaults={
                "previsao": total_previsto,
                "arrecadacao": total_realizado,
            },
        )
        self.stdout.write(
            f"  Receita TCE: previsto={total_previsto:,.0f} "
            f"realizado={total_realizado:,.0f}"
        )
        return len(rows)

    # ── TopSolutions Emendas ───────────────────────────────
    def _load_ts_emendas(self, data_dir):
        self.stdout.write("\n=== TopSolutions Emendas ===")
        rows = self._load_json(data_dir, "ts-emendas-full.json")
        if not rows:
            return 0

        count = 0
        with transaction.atomic():
            Emenda.objects.all().delete()  # Replace all
            for row in rows:
                Emenda.objects.create(
                    numero=str(row.get("numEmenda") or "").strip(),
                    ano=row.get("anoEmenda") or 2025,
                    autoria=(row.get("autoria") or "").strip(),
                    tipo=(row.get("txtTipoEmenda") or "").strip(),
                    origem_recurso=(row.get("txtOrigemRecurso") or "").strip(),
                    objeto=(row.get("objeto") or "").strip(),
                    funcao_governo=(row.get("txtFuncaoGoverno") or "").strip(),
                    beneficiario=(row.get("txtBeneficiario") or "").strip(),
                    unidade=(row.get("txtDescricaoUnidade") or "").strip(),
                    valor_previsto=_dec(row.get("vlrPrevisto")),
                    valor_empenhado=_dec(row.get("vlrEmpenhado")),
                    valor_liquidado=_dec(row.get("vlrLiquidado")),
                    valor_pago=_dec(row.get("vlrPago")),
                    data_emenda=_parse_date_iso(row.get("dtEmenda")),
                )
                count += 1

        self.stdout.write(f"  {count} emendas")
        return count

    # ── TopSolutions Orçamento ─────────────────────────────
    def _load_ts_orcamento(self, data_dir):
        self.stdout.write("\n=== TopSolutions Orcamento ===")
        rows = self._load_json(data_dir, "ts-orcamento-2025-full.json")
        if not rows:
            return 0

        count = 0
        with transaction.atomic():
            OrcamentoItem.objects.all().delete()  # Replace all
            for row in rows:
                unidade = (row.get("txtDescricaoUnidade") or "").strip()
                OrcamentoItem.objects.create(
                    ano=row.get("numExercicioFinanc") or 2025,
                    orgao_cod=(row.get("codOrgao") or "").strip(),
                    unidade=unidade,
                    acao=(row.get("txtDescricaoAcao") or "").strip(),
                    funcao=(row.get("txtDescricaoFuncao") or "").strip(),
                    subfuncao=(row.get("txtDescricaoSubFuncao") or "").strip(),
                    natureza_despesa=(
                        row.get("codNaturezaDespesa") or ""
                    ).strip(),
                    elemento_despesa=(
                        row.get("txtDescricaoElementoDespesa") or ""
                    ).strip(),
                    fonte_recurso=(
                        row.get("txtDescricaoFonteRecurso") or ""
                    ).strip()[:255],
                    valor_inicial=_dec(row.get("vlrOrcamentoInicial")),
                    valor_atualizado=_dec(row.get("vlrOrcamentoAtualizado")),
                    valor_disponivel=_dec(row.get("vlrDisponivel")),
                )
                count += 1

                # Ensure secretaria exists
                if unidade:
                    Secretaria.objects.get_or_create(
                        nome=normalize_text(unidade)
                    )

        self.stdout.write(f"  {count} itens orcamentarios")
        return count

    # ── TopSolutions Receita (aggregate) ───────────────────
    def _load_ts_receita(self, data_dir):
        self.stdout.write("\n=== TopSolutions Receita ===")
        rows = self._load_json(data_dir, "ts-receita-2025-full.json")
        if not rows:
            return 0

        # Group by year
        by_year = {}
        for row in rows:
            ano = row.get("numExercicioFinanc") or 2025
            if ano not in by_year:
                by_year[ano] = {"previsao": Decimal("0"), "arrecadacao": Decimal("0")}
            by_year[ano]["previsao"] += _dec(row.get("vlrPrevisaoAtualizado"))
            by_year[ano]["arrecadacao"] += _dec(row.get("vlrArrecadacao"))

        # Also aggregate DespesaSecretaria from receita data (by unidade)
        despesa_by_unidade = {}
        for row in rows:
            unidade = normalize_text(
                row.get("txtDescricaoUnidade") or "SEM UNIDADE"
            )
            if unidade not in despesa_by_unidade:
                despesa_by_unidade[unidade] = {
                    "previsao": Decimal("0"),
                    "arrecadacao": Decimal("0"),
                }
            despesa_by_unidade[unidade]["previsao"] += _dec(
                row.get("vlrPrevisaoAtualizado")
            )
            despesa_by_unidade[unidade]["arrecadacao"] += _dec(
                row.get("vlrArrecadacao")
            )

        self.stdout.write(
            f"  {len(rows)} registros receita, {len(by_year)} anos, "
            f"{len(despesa_by_unidade)} unidades"
        )
        return len(rows)

    # ── TopSolutions Servidores ────────────────────────────
    def _load_ts_servidores(self, data_dir):
        self.stdout.write("\n=== TopSolutions Servidores ===")
        fp = data_dir / "ts-servidores-2026-01-full.json"
        if not fp.exists():
            self.stdout.write("  SKIP (nao encontrado)")
            return 0

        self.stdout.write("  Lendo arquivo (68MB)...")
        rows = json.loads(fp.read_text(encoding="utf-8"))
        self.stdout.write(f"  {len(rows)} registros brutos")

        # Deduplicate by matricula, keeping the LATEST dtMesAno
        dedup = {}
        for row in rows:
            mat = str(row.get("numMatricula") or "").strip()
            nome = (row.get("nome") or "").strip()
            if not mat and not nome:
                continue
            key = mat if mat and mat != "0000000" else nome

            dt_str = row.get("dtMesAno") or ""
            dt = _parse_date_iso(dt_str)

            if key not in dedup or (
                dt and (dedup[key]["_dt"] is None or dt > dedup[key]["_dt"])
            ):
                orgao = (row.get("orgao") or "").strip()
                # Remove " - EF", " - CC", " - TEMP" etc suffixes for cleaner names
                orgao_clean = orgao.split(" - ")[0].strip() if " - " in orgao else orgao
                dedup[key] = {
                    "matricula": mat,
                    "nome": nome,
                    "orgao": normalize_text(orgao_clean) if orgao_clean else "SEM ORGAO",
                    "vinculo": (row.get("vinculo") or "").strip(),
                    "valor_bruto": _dec(row.get("vlrRemuneracaoBruta")),
                    "valor_liquido": _dec(row.get("vlrRemuAposDescObrig")),
                    "cargo": (row.get("cargo") or "").strip(),
                    "funcao": (row.get("funcao") or "").strip(),
                    "carga_horaria": (row.get("cargaHoraria") or "").strip(),
                    "_dt": dt,
                }

        self.stdout.write(f"  {len(dedup)} servidores unicos (dedup por matricula)")

        count = 0
        with transaction.atomic():
            Servidor.objects.all().delete()  # Full replace with fresh data
            batch = []
            for item in dedup.values():
                batch.append(
                    Servidor(
                        matricula=item["matricula"],
                        nome=item["nome"],
                        orgao=item["orgao"],
                        vinculo=item["vinculo"],
                        valor_bruto=item["valor_bruto"],
                        valor_liquido=item["valor_liquido"],
                        cargo=item["cargo"],
                        funcao=item["funcao"],
                        carga_horaria=item["carga_horaria"],
                    )
                )
                if len(batch) >= 500:
                    Servidor.objects.bulk_create(batch)
                    count += len(batch)
                    batch = []

            if batch:
                Servidor.objects.bulk_create(batch)
                count += len(batch)

            # Ensure secretarias exist for all orgaos
            orgaos = set(item["orgao"] for item in dedup.values() if item["orgao"])
            for orgao in orgaos:
                Secretaria.objects.get_or_create(nome=orgao)

        self.stdout.write(self.style.SUCCESS(f"  {count} servidores carregados"))
        return count

    # ── Gestores de Secretaria ─────────────────────────────
    def _load_gestores(self, exports_dir):
        self.stdout.write("\n=== Gestores de Secretaria ===")
        csv_path = exports_dir / "secretarios-ativos-folha-2026-01.csv"
        if not csv_path.exists():
            self.stdout.write("  SKIP (CSV nao encontrado)")
            return 0

        count = 0
        with csv_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                orgao_raw = (row.get("orgao") or "").strip()
                nome = (row.get("nome") or "").strip()
                if not orgao_raw or not nome:
                    continue

                # Try exact match first, then fuzzy
                orgao_norm = normalize_text(orgao_raw)
                # Remove " - CC", " - EF" suffixes
                orgao_clean = orgao_raw.split(" - ")[0].strip()
                orgao_clean_norm = normalize_text(orgao_clean)

                matched = False
                for sec in Secretaria.objects.all():
                    sec_norm = normalize_text(sec.nome)
                    if (
                        sec_norm == orgao_norm
                        or sec_norm == orgao_clean_norm
                        or orgao_clean_norm in sec_norm
                        or sec_norm in orgao_clean_norm
                    ):
                        sec.gestor = nome
                        sec.save(update_fields=["gestor"])
                        count += 1
                        matched = True
                        break

                if not matched:
                    # Create new secretaria with gestor
                    Secretaria.objects.update_or_create(
                        nome=normalize_text(orgao_clean),
                        defaults={"gestor": nome},
                    )
                    count += 1

        self.stdout.write(f"  {count} gestores atribuidos")
        return count

    # ── Fix stuck SyncRuns ─────────────────────────────────
    def _fix_sync_runs(self):
        self.stdout.write("\n=== Fix Stuck SyncRuns ===")
        stuck = SyncRun.objects.filter(status="executando")
        count = stuck.count()
        if count:
            stuck.update(status="erro", mensagem="Encerrado automaticamente (stuck)")
            self.stdout.write(f"  {count} SyncRuns corrigidos")
        else:
            self.stdout.write("  Nenhum SyncRun stuck")
        return count

    # ── Generate Smart Alerts ──────────────────────────────
    def _generate_alerts(self):
        self.stdout.write("\n=== Gerando Alertas Analiticos ===")
        Alerta.objects.all().delete()  # Fresh alerts
        alertas = []

        # 1. Supplier concentration
        fornecedores = Fornecedor.objects.order_by("-valor_total")
        total_forn = sum(f.valor_total for f in fornecedores)
        if total_forn > 0:
            top5 = fornecedores[:5]
            top5_total = sum(f.valor_total for f in top5)
            pct = (top5_total / total_forn) * 100
            if pct > 60:
                alertas.append(Alerta(
                    codigo="CONC-FORN-001",
                    titulo="Concentracao de fornecedores acima de 60%",
                    severidade="alta",
                    detalhes=(
                        f"Os 5 maiores fornecedores concentram {pct:.1f}% "
                        f"(R$ {top5_total:,.2f}) do total contratado "
                        f"(R$ {total_forn:,.2f}). "
                        f"Top: {', '.join(f.nome for f in top5)}."
                    ),
                ))

        # 2. Budget execution rate
        despesas = DespesaSecretaria.objects.filter(ano=2025)
        total_orc = sum(d.orcamento for d in despesas)
        total_pago = sum(d.pago for d in despesas)
        if total_orc > 0:
            exec_pct = (total_pago / total_orc) * 100
            if exec_pct < 50:
                alertas.append(Alerta(
                    codigo="EXEC-ORC-001",
                    titulo="Execucao orcamentaria abaixo de 50%",
                    severidade="alta",
                    detalhes=(
                        f"A execucao financeira esta em {exec_pct:.1f}% "
                        f"(R$ {total_pago:,.2f} pago de R$ {total_orc:,.2f} orcado). "
                        "Indica risco de baixa capacidade de execucao."
                    ),
                ))

            # Low execution per secretaria
            for d in despesas:
                if d.orcamento > 0:
                    sec_pct = (d.pago / d.orcamento) * 100
                    if sec_pct < 20 and d.orcamento > 100000:
                        alertas.append(Alerta(
                            codigo=f"EXEC-SEC-{d.id:03d}",
                            titulo=f"Baixa execucao: {d.secretaria[:60]}",
                            severidade="media",
                            detalhes=(
                                f"Execucao de apenas {sec_pct:.1f}% "
                                f"(R$ {d.pago:,.2f} de R$ {d.orcamento:,.2f}). "
                                "Requer avaliacao de planejamento."
                            ),
                        ))

        # 3. Emendas with low execution
        emendas = Emenda.objects.filter(ano=2025)
        total_prev = sum(e.valor_previsto for e in emendas)
        total_real = sum(e.valor_pago for e in emendas)
        if total_prev > 0:
            exec_emenda = (total_real / total_prev) * 100
            if exec_emenda < 30:
                alertas.append(Alerta(
                    codigo="EMENDA-EXEC-001",
                    titulo="Baixa execucao de emendas parlamentares",
                    severidade="media",
                    detalhes=(
                        f"Apenas {exec_emenda:.1f}% das emendas foram pagas "
                        f"(R$ {total_real:,.2f} de R$ {total_prev:,.2f}). "
                        f"Total de {emendas.count()} emendas registradas."
                    ),
                ))

        # 4. Contracts without CNPJ
        contratos_sem_cnpj = Contrato.objects.filter(cnpj="").count()
        total_contratos = Contrato.objects.count()
        if contratos_sem_cnpj > 0 and total_contratos > 0:
            pct_sem = (contratos_sem_cnpj / total_contratos) * 100
            if pct_sem > 30:
                alertas.append(Alerta(
                    codigo="CONT-CNPJ-001",
                    titulo="Contratos sem CNPJ identificado",
                    severidade="media",
                    detalhes=(
                        f"{contratos_sem_cnpj} de {total_contratos} contratos "
                        f"({pct_sem:.0f}%) nao possuem CNPJ registrado. "
                        "Dificulta rastreabilidade e cruzamento de dados."
                    ),
                ))

        # 5. High-value contracts above average
        if total_contratos > 0:
            total_val = sum(c.valor for c in Contrato.objects.all())
            media = total_val / total_contratos
            acima = Contrato.objects.filter(valor__gt=media * 3).count()
            if acima > 0:
                alertas.append(Alerta(
                    codigo="CONT-VALOR-001",
                    titulo="Contratos com valor 3x acima da media",
                    severidade="alta",
                    detalhes=(
                        f"{acima} contratos possuem valor superior a "
                        f"3x a media (R$ {media:,.2f}). "
                        "Recomenda-se auditoria detalhada destes contratos."
                    ),
                ))

        # 6. Servidores without salary
        serv_sem_sal = Servidor.objects.filter(valor_bruto=0).count()
        total_serv = Servidor.objects.count()
        if serv_sem_sal > 0 and total_serv > 0:
            pct = (serv_sem_sal / total_serv) * 100
            if pct > 5:
                alertas.append(Alerta(
                    codigo="SERV-SAL-001",
                    titulo="Servidores com remuneracao zerada",
                    severidade="media",
                    detalhes=(
                        f"{serv_sem_sal} servidores ({pct:.1f}%) possuem "
                        "remuneracao bruta igual a zero. "
                        "Pode indicar erro de cadastro ou afastamento."
                    ),
                ))

        # 7. Licitações summary
        licit_total = Licitacao.objects.count()
        licit_homologadas = Licitacao.objects.filter(
            status__icontains="homologada"
        ).count()
        if licit_total > 0:
            alertas.append(Alerta(
                codigo="LICIT-INFO-001",
                titulo=f"{licit_total} licitacoes registradas no sistema",
                severidade="baixa",
                detalhes=(
                    f"Base possui {licit_total} licitacoes, "
                    f"sendo {licit_homologadas} homologadas. "
                    f"Valor total orcado: R$ "
                    f"{sum(l.valor for l in Licitacao.objects.all()):,.2f}."
                ),
            ))

        # 8. Staffing by type
        vinculos = {}
        for s in Servidor.objects.all():
            v = s.vinculo or "Nao informado"
            vinculos[v] = vinculos.get(v, 0) + 1

        comissionados = sum(
            v for k, v in vinculos.items()
            if "comission" in k.lower() or "cc" in k.lower() or "cargo" in k.lower()
        )
        if total_serv > 0 and comissionados > 0:
            pct_cc = (comissionados / total_serv) * 100
            if pct_cc > 20:
                alertas.append(Alerta(
                    codigo="SERV-CC-001",
                    titulo="Proporcao elevada de cargos comissionados",
                    severidade="alta",
                    detalhes=(
                        f"{comissionados} servidores comissionados "
                        f"({pct_cc:.1f}% do total de {total_serv}). "
                        "Pode indicar risco de descontinuidade administrativa."
                    ),
                ))

        Alerta.objects.bulk_create(alertas)
        self.stdout.write(f"  {len(alertas)} alertas gerados")
        return len(alertas)
