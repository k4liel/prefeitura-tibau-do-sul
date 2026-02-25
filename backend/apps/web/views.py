import csv
import json
import re
import unicodedata
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q, Sum
from django.views.generic import TemplateView

from apps.contratacoes.models import Contrato, Licitacao
from apps.financas.models import DespesaSecretaria, Emenda, OrcamentoItem, ReceitaResumo
from apps.fornecedores.models import Fornecedor
from apps.governanca.models import Secretaria
from apps.governanca.services import resumo_governanca
from apps.legislativo.models import Vereador
from apps.monitoramento.models import Alerta
from apps.monitoramento.services import metricas_jobs
from apps.pessoal.models import Servidor


_BACKEND_DIR = Path(__file__).resolve().parents[2]


def _find_data_file(filename):
    """Look in backend/seed_data/ first (production), then project-root data/exports/ (local)."""
    candidates = [
        _BACKEND_DIR / "seed_data" / filename,
        _BACKEND_DIR.parent / "data" / "exports" / filename,
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def load_municipio_contexto():
    file_path = _find_data_file("municipio-contexto.json")
    if file_path is None:
        return {}
    try:
        return json.loads(file_path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}


def load_export_data(filename):
    file_path = _find_data_file(filename)
    if file_path is None:
        return []
    try:
        payload = json.loads(file_path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, list) else []
    except Exception:  # noqa: BLE001
        return []


def load_export_csv(filename):
    file_path = _find_data_file(filename)
    if file_path is None:
        return []
    try:
        with file_path.open("r", encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle, delimiter=";"))
    except Exception:  # noqa: BLE001
        return []


def _extract_number(value):
    if value is None:
        return None
    text = str(value)
    match = re.search(r"[0-9][0-9\.,]*", text)
    if not match:
        return None
    token = match.group(0)
    if "," in token and "." in token:
        token = token.replace(".", "").replace(",", ".")
    elif "," in token:
        token = token.replace(",", ".")
    try:
        return float(token)
    except ValueError:
        return None


def _decimal_or_zero(value):
    if value in (None, ""):
        return Decimal("0")
    try:
        return Decimal(str(value))
    except Exception:  # noqa: BLE001
        cleaned = str(value).replace(".", "").replace(",", ".")
        try:
            return Decimal(cleaned)
        except Exception:  # noqa: BLE001
            return Decimal("0")


def _normalize_text(value):
    text = str(value or "").strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _match_secretaria(orgao, secretarias_norm):
    orgao_norm = _normalize_text(orgao)
    if not orgao_norm:
        return None

    for sec in secretarias_norm:
        if orgao_norm == sec["norm"]:
            return sec

    candidates = [
        sec
        for sec in secretarias_norm
        if sec["norm"] and (sec["norm"] in orgao_norm or orgao_norm in sec["norm"])
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda item: len(item["norm"]))


def _pick_servidor_por_nome(nome, servidores_por_nome):
    key = _normalize_text(nome)
    candidatos = servidores_por_nome.get(key, [])
    if not candidatos:
        return None
    return max(candidatos, key=lambda row: row.get("valor_bruto") or Decimal("0"))


class DashboardView(TemplateView):
    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        receitas = ReceitaResumo.objects.filter(ano=2025).aggregate(
            previsao=Sum("previsao"), arrecadacao=Sum("arrecadacao")
        )
        despesas = DespesaSecretaria.objects.filter(ano=2025).aggregate(
            orcamento=Sum("orcamento"), pago=Sum("pago")
        )
        context.update(
            {
                "kpis": {
                    "secretarias": Secretaria.objects.count(),
                    "vereadores": Vereador.objects.count(),
                    "servidores": Servidor.objects.count(),
                    "licitacoes": Licitacao.objects.count(),
                    "contratos": Contrato.objects.count(),
                    "emendas": Emenda.objects.count(),
                    "orcamento_itens": OrcamentoItem.objects.count(),
                    "receita_arrecadada": receitas.get("arrecadacao") or 0,
                    "despesa_paga": despesas.get("pago") or 0,
                }
            }
        )
        contexto = load_municipio_contexto()
        context["contexto_municipio"] = contexto

        receita_realizada = context["kpis"]["receita_arrecadada"] or 0
        despesa_paga = context["kpis"]["despesa_paga"] or 0
        saldo = receita_realizada - despesa_paga

        fornecedores_total = (
            Fornecedor.objects.aggregate(total=Sum("valor_total")).get("total") or 0
        )
        top5_total = sum(
            item.valor_total
            for item in Fornecedor.objects.order_by("-valor_total")[:5]
            if item.valor_total
        )
        concentracao_top5 = (
            (top5_total / fornecedores_total) * 100 if fornecedores_total else 0
        )

        ticket_medio_contratos = (
            Contrato.objects.aggregate(media=Avg("valor")).get("media") or 0
        )
        contratos_acima_media = Contrato.objects.filter(
            valor__gt=ticket_medio_contratos
        ).count()
        alertas_altos = Alerta.objects.filter(severidade__iexact="alta").count()

        ibge = contexto.get("ibge", {})
        tce = contexto.get("tce_rn", {})
        topsolutions = contexto.get("topsolutions", {})
        operacionais = contexto.get("topsolutions_operacionais", {})
        operacionais_rows = []
        for key, label in [
            ("diarias", "Diarias"),
            ("obras", "Obras"),
            ("pca", "Plano de Contratacao Anual"),
        ]:
            item = operacionais.get(key, {})
            operacionais_rows.append(
                {
                    "chave": key,
                    "titulo": label,
                    "ok": bool(item.get("ok")),
                    "status_code": item.get("status_code"),
                    "count": item.get("count", 0),
                    "error_code": item.get("error_code", ""),
                    "url": item.get("url", ""),
                }
            )

        context["diagnostico"] = {
            "demografia": {
                "habitantes": ibge.get("populacao_estimada_2025"),
                "censo": ibge.get("populacao_censo_2022"),
                "densidade": ibge.get("densidade_demografica"),
                "area": ibge.get("area_territorial"),
            },
            "educacao": {
                "escolarizacao": ibge.get("escolarizacao_6_14"),
                "idhm": ibge.get("idhm"),
            },
            "saude": {
                "mortalidade_infantil": ibge.get("mortalidade_infantil"),
            },
            "fiscal": {
                "receita_realizada": tce.get("receita_realizada"),
                "despesa_paga": tce.get("despesa_paga"),
                "receita_prevista": tce.get("receita_prevista"),
            },
            "contratacoes": {
                "processos_unicos": tce.get("licitacoes_processos_unicos"),
                "lotes_unicos": tce.get("licitacoes_lotes_unicos"),
                "homologadas": tce.get("licitacoes_homologadas"),
                "em_andamento": tce.get("licitacoes_em_andamento"),
                "contratos": tce.get("contratos_qtd"),
            },
            "emendas": {
                "quantidade": topsolutions.get("emendas_qtd"),
                "previsto_total": topsolutions.get("emendas_previsto_total"),
                "realizado_total": topsolutions.get("emendas_realizado_total"),
            },
            "operacionais": {
                "fontes_ok": sum(1 for row in operacionais_rows if row["ok"]),
                "fontes_total": len(operacionais_rows),
            },
        }
        context["operacionais_topsolutions"] = operacionais_rows
        context["one_minute"] = {
            "saldo": saldo,
            "receita_realizada": receita_realizada,
            "despesa_paga": despesa_paga,
            "concentracao_top5": concentracao_top5,
            "alertas_altos": alertas_altos,
            "contratos_acima_media": contratos_acima_media,
        }
        context["riscos"] = [
            (
                "Concentracao de fornecedores: "
                f"top 5 representam {concentracao_top5:.1f}% do valor contratado."
            ),
            (
                "Contratos acima do ticket medio: "
                f"{contratos_acima_media} registros para avaliacao prioritaria."
            ),
            (f"Alertas de alta severidade ativos: {alertas_altos}."),
        ]
        return context


class GovernancaView(TemplateView):
    template_name = "dashboard/governanca.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["secretarias"] = Secretaria.objects.exclude(gestor__isnull=True).exclude(gestor="").order_by("nome")
        return context


class LegislativoView(TemplateView):
    template_name = "dashboard/legislativo.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["vereadores"] = Vereador.objects.order_by("nome")
        return context


class FinancasView(TemplateView):
    template_name = "dashboard/financas.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        despesas_qs = DespesaSecretaria.objects.filter(ano=2025).order_by("-orcamento")
        receitas_qs = ReceitaResumo.objects.filter(ano=2025)

        receitas_totais = receitas_qs.aggregate(
            previsao=Sum("previsao"), arrecadacao=Sum("arrecadacao")
        )
        despesas_totais = despesas_qs.aggregate(
            orcamento=Sum("orcamento"),
            empenhado=Sum("empenhado"),
            liquidado=Sum("liquidado"),
            pago=Sum("pago"),
        )

        arrecadacao = receitas_totais.get("arrecadacao") or 0
        pago = despesas_totais.get("pago") or 0
        saldo = arrecadacao - pago
        previsao = receitas_totais.get("previsao") or 0
        execucao_pct = (arrecadacao / previsao * 100) if previsao else 0

        context.update(
            {
                "despesas": despesas_qs[:20],
                "receitas": receitas_qs,
                "financeiro": {
                    "previsao": previsao,
                    "arrecadacao": arrecadacao,
                    "orcamento": despesas_totais.get("orcamento") or 0,
                    "empenhado": despesas_totais.get("empenhado") or 0,
                    "liquidado": despesas_totais.get("liquidado") or 0,
                    "pago": pago,
                    "saldo": saldo,
                    "execucao_pct": execucao_pct,
                    "top_secretaria": despesas_qs.first(),
                    "receita_pct": 100,
                    "despesa_pct": (pago / arrecadacao * 100) if arrecadacao else 0,
                },
            }
        )
        top_secretarias_chart = list(despesas_qs[:8])
        max_pago = max((item.pago for item in top_secretarias_chart), default=0)
        context["secretarias_chart"] = [
            {
                "secretaria": item.secretaria,
                "valor": item.pago,
                "pct": (item.pago / max_pago * 100) if max_pago else 0,
            }
            for item in top_secretarias_chart
        ]
        context["insights"] = [
            (
                "A receita realizada corresponde a "
                f"{execucao_pct:.1f}% da previsao anual."
            ),
            (
                f"O saldo fiscal atual e de R$ {saldo:,.2f}.".replace(",", "_")
                .replace(".", ",")
                .replace("_", ".")
            ),
            (
                "A maior alocacao orcamentaria esta em "
                f"{(despesas_qs.first().secretaria if despesas_qs.first() else 'N/A')}"
            ),
        ]
        return context


class LicitacoesView(TemplateView):
    template_name = "dashboard/licitacoes.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search = self.request.GET.get("search", "").strip()
        modalidade = self.request.GET.get("modalidade", "").strip()
        status = self.request.GET.get("status", "").strip()
        valor_min = self.request.GET.get("valor_min", "").strip()
        valor_max = self.request.GET.get("valor_max", "").strip()
        ordering = self.request.GET.get("ordering", "-valor")
        allowed_order = {"valor", "-valor", "certame", "-certame", "modalidade"}
        if ordering not in allowed_order:
            ordering = "-valor"

        queryset = Licitacao.objects.all()
        if search:
            queryset = queryset.filter(
                Q(certame__icontains=search)
                | Q(modalidade__icontains=search)
                | Q(objeto__icontains=search)
            )
        if modalidade:
            queryset = queryset.filter(modalidade__iexact=modalidade)
        if status:
            queryset = queryset.filter(status__iexact=status)
        if valor_min:
            queryset = queryset.filter(valor__gte=valor_min)
        if valor_max:
            queryset = queryset.filter(valor__lte=valor_max)

        queryset = queryset.order_by(ordering)
        totais = queryset.aggregate(total=Sum("valor"))
        certames_unicos = set(
            (item or "").strip().upper()
            for item in queryset.values_list("certame", flat=True)
            if (item or "").strip()
        )
        contexto = load_municipio_contexto().get("tce_rn", {})
        status_counts = {
            row["status"]: row["total"]
            for row in Licitacao.objects.values("status")
            .annotate(total=Count("id"))
            .order_by()
            if row["status"]
        }
        paginator = Paginator(queryset, 25)
        page_number = self.request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)

        statuses = list(
            Licitacao.objects.values_list("status", flat=True)
            .distinct()
            .order_by("status")
        )
        context.update(
            {
                "page_obj": page_obj,
                "search": search,
                "modalidade": modalidade,
                "status": status,
                "statuses": [s for s in statuses if s],
                "valor_min": valor_min,
                "valor_max": valor_max,
                "ordering": ordering,
                "resumo": {
                    "total_filtrado": totais.get("total") or 0,
                    "quantidade": queryset.count(),
                    "certames_unicos": len(certames_unicos),
                    "lotes_estimados": max(queryset.count() - len(certames_unicos), 0),
                    "homologadas": contexto.get("licitacoes_homologadas"),
                    "em_andamento": contexto.get("licitacoes_em_andamento"),
                    "valor_unico_tce": contexto.get(
                        "licitacoes_valor_total_orcado_unico"
                    ),
                    "ticket_medio": (
                        (totais.get("total") or 0) / queryset.count()
                        if queryset.count()
                        else 0
                    ),
                    "status_counts": status_counts,
                },
                "insights": [
                    (
                        "A base filtrada possui "
                        f"{len(certames_unicos)} certames unicos "
                        f"em {queryset.count()} registros."
                    ),
                    (
                        "No recorte oficial do TCE-RN, ha "
                        f"{contexto.get('licitacoes_homologadas', 0)} homologadas e "
                        f"{contexto.get('licitacoes_em_andamento', 0)} em andamento."
                    ),
                    (
                        "Use modalidade + faixa de valor para "
                        "reduzir ruido de lotes duplicados."
                    ),
                ],
            }
        )
        return context


class ContratosView(TemplateView):
    template_name = "dashboard/contratos.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search = self.request.GET.get("search", "").strip()
        modalidade = self.request.GET.get("modalidade", "").strip()
        empresa = self.request.GET.get("empresa", "").strip()
        ativo = self.request.GET.get("ativo", "").strip()
        valor_min = self.request.GET.get("valor_min", "").strip()
        valor_max = self.request.GET.get("valor_max", "").strip()
        ordering = self.request.GET.get("ordering", "-valor")
        allowed_order = {"valor", "-valor", "numero", "-numero", "empresa", "-empresa"}
        if ordering not in allowed_order:
            ordering = "-valor"

        queryset = Contrato.objects.all()
        if search:
            queryset = queryset.filter(
                Q(numero__icontains=search)
                | Q(empresa__icontains=search)
                | Q(modalidade__icontains=search)
                | Q(objeto__icontains=search)
            )
        if modalidade:
            queryset = queryset.filter(modalidade__iexact=modalidade)
        if empresa:
            queryset = queryset.filter(empresa__icontains=empresa)
        if ativo in ("1", "true"):
            queryset = queryset.filter(ativo=True)
        elif ativo in ("0", "false"):
            queryset = queryset.filter(ativo=False)
        if valor_min:
            queryset = queryset.filter(valor__gte=valor_min)
        if valor_max:
            queryset = queryset.filter(valor__lte=valor_max)

        queryset = queryset.order_by(ordering)
        totais = queryset.aggregate(total=Sum("valor"))
        media = (totais.get("total") or 0) / queryset.count() if queryset.count() else 0
        paginator = Paginator(queryset, 25)
        page_number = self.request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)

        context.update(
            {
                "page_obj": page_obj,
                "search": search,
                "modalidade": modalidade,
                "empresa": empresa,
                "ativo": ativo,
                "valor_min": valor_min,
                "valor_max": valor_max,
                "ordering": ordering,
                "resumo": {
                    "total_filtrado": totais.get("total") or 0,
                    "quantidade": queryset.count(),
                    "ticket_medio": (media if queryset.count() else 0),
                },
                "insights": [
                    (f"O valor medio por contrato no recorte atual e R$ {media:,.2f}.")
                    .replace(",", "_")
                    .replace(".", ",")
                    .replace("_", "."),
                    (
                        "Priorize analise dos contratos acima do ticket medio "
                        "para identificar maior impacto fiscal."
                    ),
                    (
                        "Combine filtros por empresa e modalidade para auditoria "
                        "de concentracao contratual."
                    ),
                ],
            }
        )
        return context


class FornecedoresView(TemplateView):
    template_name = "dashboard/fornecedores.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        search = self.request.GET.get("search", "").strip()
        cnpj = self.request.GET.get("cnpj", "").strip()
        valor_min = self.request.GET.get("valor_min", "").strip()
        ordering = self.request.GET.get("ordering", "-valor_total")
        allowed_order = {"valor_total", "-valor_total", "nome", "-nome"}
        if ordering not in allowed_order:
            ordering = "-valor_total"

        queryset = Fornecedor.objects.all()
        if search:
            queryset = queryset.filter(
                Q(nome__icontains=search) | Q(cnpj__icontains=search)
            )
        if cnpj:
            queryset = queryset.filter(cnpj__icontains=cnpj)
        if valor_min:
            queryset = queryset.filter(valor_total__gte=valor_min)

        queryset = queryset.order_by(ordering)
        totais = queryset.aggregate(total=Sum("valor_total"))
        top5 = list(queryset[:5])
        top5_total = sum(item.valor_total for item in top5)
        total_geral = totais.get("total") or 0
        concentracao_top5 = (top5_total / total_geral) * 100 if total_geral else 0
        paginator = Paginator(queryset, 25)
        page_number = self.request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)

        context.update(
            {
                "page_obj": page_obj,
                "search": search,
                "cnpj": cnpj,
                "valor_min": valor_min,
                "ordering": ordering,
                "resumo": {
                    "total_filtrado": total_geral,
                    "quantidade": queryset.count(),
                    "concentracao_top5": (concentracao_top5),
                },
                "insights": [
                    (
                        "Os 5 maiores fornecedores concentram "
                        f"{concentracao_top5:.1f}% "
                        "do valor filtrado."
                    ),
                    "CNPJ preenchido melhora rastreabilidade e cruzamento externo.",
                    "Use ordenacao por valor para identificar riscos de concentracao.",
                ],
            }
        )
        return context


class AlertasView(TemplateView):
    template_name = "dashboard/alertas.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search = self.request.GET.get("search", "").strip()
        severidade = self.request.GET.get("severidade", "").strip()
        ordering = self.request.GET.get("ordering", "-criado_em")
        allowed_order = {"criado_em", "-criado_em", "severidade", "-severidade"}
        if ordering not in allowed_order:
            ordering = "-criado_em"

        queryset = Alerta.objects.all()
        if search:
            queryset = queryset.filter(
                Q(codigo__icontains=search)
                | Q(titulo__icontains=search)
                | Q(detalhes__icontains=search)
            )
        if severidade:
            queryset = queryset.filter(severidade__iexact=severidade)

        queryset = queryset.order_by(ordering)
        paginator = Paginator(queryset, 25)
        page_number = self.request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)

        context.update(
            {
                "page_obj": page_obj,
                "search": search,
                "severidade": severidade,
                "ordering": ordering,
            }
        )
        return context


class SecretariasOrcamentoView(TemplateView):
    template_name = "dashboard/secretarias.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search = self.request.GET.get("search", "").strip()
        queryset = DespesaSecretaria.objects.filter(ano=2025)
        if search:
            queryset = queryset.filter(secretaria__icontains=search)
        queryset = queryset.order_by("-orcamento")
        totais = queryset.aggregate(
            orcamento=Sum("orcamento"),
            empenhado=Sum("empenhado"),
            liquidado=Sum("liquidado"),
            pago=Sum("pago"),
        )
        context["despesas"] = queryset
        context["search"] = search
        context["resumo"] = {
            "orcamento": totais.get("orcamento") or 0,
            "empenhado": totais.get("empenhado") or 0,
            "liquidado": totais.get("liquidado") or 0,
            "pago": totais.get("pago") or 0,
            "quantidade": queryset.count(),
        }
        top = queryset.first()
        execucao = (
            ((totais.get("pago") or 0) / (totais.get("orcamento") or 1) * 100)
            if totais.get("orcamento")
            else 0
        )
        context["insights"] = [
            f"A execucao financeira acumulada esta em {execucao:.1f}% do orcamento.",
            (
                "A secretaria com maior orcamento atual e "
                f"{top.secretaria if top else 'N/A'}."
            ),
            "Secretarias com baixa execucao podem demandar revisao de planejamento.",
        ]
        return context


class FuncionariosView(TemplateView):
    template_name = "dashboard/funcionarios.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search = self.request.GET.get("search", "").strip()
        orgao = self.request.GET.get("orgao", "").strip()
        vinculo = self.request.GET.get("vinculo", "").strip()
        cargo = self.request.GET.get("cargo", "").strip()
        queryset = Servidor.objects.all()
        if search:
            queryset = queryset.filter(nome__icontains=search)
        if orgao:
            queryset = queryset.filter(orgao__icontains=orgao)
        if vinculo:
            queryset = queryset.filter(vinculo__icontains=vinculo)
        if cargo:
            queryset = queryset.filter(cargo__icontains=cargo)

        totais = queryset.aggregate(
            total_bruto=Sum("valor_bruto"),
            total_liquido=Sum("valor_liquido"),
            media_bruto=Avg("valor_bruto"),
        )

        paginator = Paginator(queryset.order_by("nome"), 25)
        context["page_obj"] = paginator.get_page(self.request.GET.get("page", 1))
        context.update(
            {
                "search": search,
                "orgao": orgao,
                "vinculo": vinculo,
                "cargo": cargo,
                "resumo": {
                    "total_servidores": queryset.count(),
                    "total_bruto": totais.get("total_bruto") or 0,
                    "total_liquido": totais.get("total_liquido") or 0,
                    "media_bruto": totais.get("media_bruto") or 0,
                },
            }
        )
        return context


class TecnologiaView(TemplateView):
    template_name = "dashboard/tecnologia.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        terms = [
            "tecnolog",
            "software",
            "sistema",
            "internet",
            "telecom",
            "dados",
            "informat",
        ]
        q = Q()
        for term in terms:
            q |= Q(objeto__icontains=term) | Q(empresa__icontains=term)
        context["contratos_tech"] = Contrato.objects.filter(q).order_by("-valor")[:200]
        context["total_tech"] = (
            Contrato.objects.filter(q).aggregate(total=Sum("valor")).get("total") or 0
        )
        context["total_geral"] = (
            Contrato.objects.aggregate(total=Sum("valor")).get("total") or 0
        )
        return context


class HierarquiaOrganizacionalView(TemplateView):
    template_name = "dashboard/hierarquia.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        governanca = resumo_governanca()

        secretarias = list(Secretaria.objects.order_by("nome"))
        secretarias_norm = [
            {
                "id": sec.id,
                "nome": sec.nome,
                "norm": _normalize_text(sec.nome),
                "obj": sec,
            }
            for sec in secretarias
        ]

        grupos = {sec.id: {"secretaria": sec, "servidores": []} for sec in secretarias}
        servidores_sem_vinculo = []
        servidores = list(Servidor.objects.order_by("nome"))

        for servidor in servidores:
            matched = _match_secretaria(servidor.orgao, secretarias_norm)
            if matched:
                grupos[matched["id"]]["servidores"].append(servidor)
            else:
                servidores_sem_vinculo.append(servidor)

        vinculos_counter = defaultdict(int)
        for servidor in servidores:
            vinculos_counter[str(servidor.vinculo or "Nao informado").strip()] += 1

        hierarchy_rows = sorted(
            [item for item in grupos.values() if item["servidores"]],
            key=lambda row: len(row["servidores"]),
            reverse=True,
        )
        secretarias_sem_servidor = [
            item["secretaria"] for item in grupos.values() if not item["servidores"]
        ]

        context.update(
            {
                "prefeito": governanca.get("prefeito", "-"),
                "vice_prefeito": governanca.get("vice_prefeito", "-"),
                "hierarquia_rows": hierarchy_rows,
                "secretarias_sem_servidor": secretarias_sem_servidor,
                "servidores_sem_vinculo": servidores_sem_vinculo,
                "resumo": {
                    "total_secretarias": len(secretarias),
                    "total_com_gestor": sum(1 for s in secretarias if s.gestor),
                    "secretarias_com_servidor": len(hierarchy_rows),
                    "total_servidores": len(servidores),
                    "servidores_sem_vinculo": len(servidores_sem_vinculo),
                },
                "resumo_vinculos": sorted(
                    vinculos_counter.items(), key=lambda item: item[1], reverse=True
                )[:10],
            }
        )
        return context


class RemuneracoesView(TemplateView):
    template_name = "dashboard/remuneracoes.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        governanca = resumo_governanca()
        secretarias = list(Secretaria.objects.order_by("nome"))
        vereadores = list(Vereador.objects.order_by("nome"))

        folha_export = load_export_csv("funcionarios-folha-2026-01.csv")
        servidores = []
        for row in folha_export:
            servidores.append(
                {
                    "nome": (row.get("nome") or "").strip(),
                    "orgao": (row.get("orgao") or "").strip(),
                    "vinculo": (row.get("vinculo") or "").strip() or "-",
                    "funcao": (
                        row.get("funcao") or row.get("cargoFuncao") or ""
                    ).strip(),
                    "matricula": (row.get("numMatricula") or "").strip(),
                    "valor_bruto": _decimal_or_zero(row.get("vlrRemuneracaoBruta")),
                    "valor_liquido": _decimal_or_zero(row.get("vlrRemuAposDescObrig")),
                    "fonte": "export-folha-2026-01",
                }
            )

        if not servidores:
            for servidor in Servidor.objects.order_by("nome"):
                servidores.append(
                    {
                        "nome": servidor.nome,
                        "orgao": servidor.orgao,
                        "vinculo": servidor.vinculo or "-",
                        "funcao": "",
                        "matricula": servidor.matricula,
                        "valor_bruto": servidor.valor_bruto or Decimal("0"),
                        "valor_liquido": servidor.valor_liquido or Decimal("0"),
                        "fonte": "banco-local",
                    }
                )

        servidores_por_nome = defaultdict(list)
        for servidor in servidores:
            servidores_por_nome[_normalize_text(servidor.get("nome"))].append(servidor)

        cargos_estrategicos = [
            (
                "Executivo",
                "Prefeito",
                governanca.get("prefeito", ""),
                "Gabinete do Prefeito",
            ),
            (
                "Executivo",
                "Vice-prefeito",
                governanca.get("vice_prefeito", ""),
                "Gabinete do Vice-prefeito",
            ),
        ]
        for sec in secretarias:
            cargos_estrategicos.append(
                ("Executivo", "Secretario", sec.gestor, sec.nome)
            )

        subsidios_legais = {
            "Prefeito": Decimal("25000.00"),
            "Vice-prefeito": Decimal("12500.00"),
            "Secretario": Decimal("8300.00"),
            "Vereador": Decimal("9400.00"),
            "Vereador Presidente": Decimal("10400.00"),
        }

        rows_estrategicos = []
        for esfera, cargo, nome, orgao in cargos_estrategicos:
            if not nome:
                continue
            servidor = _pick_servidor_por_nome(nome, servidores_por_nome)
            valor_bruto = servidor.get("valor_bruto") if servidor else None
            valor_liquido = servidor.get("valor_liquido") if servidor else None
            fonte_salario = (
                servidor.get("fonte") if servidor else "nao localizado na folha"
            )
            if valor_bruto is None and cargo in subsidios_legais:
                valor_bruto = subsidios_legais[cargo]
                valor_liquido = None
                fonte_salario = "lei-805-2023"

            rows_estrategicos.append(
                {
                    "esfera": esfera,
                    "cargo": cargo,
                    "nome": nome,
                    "orgao": orgao,
                    "vinculo": servidor.get("vinculo") if servidor else "-",
                    "valor_bruto": valor_bruto,
                    "valor_liquido": valor_liquido,
                    "fonte_salario": fonte_salario,
                    "funcao": servidor.get("funcao") if servidor else "",
                }
            )

        rows_vereadores = []
        for vereador in vereadores:
            servidor = _pick_servidor_por_nome(vereador.nome, servidores_por_nome)
            valor_bruto = servidor.get("valor_bruto") if servidor else None
            valor_liquido = servidor.get("valor_liquido") if servidor else None
            fonte_salario = (
                servidor.get("fonte") if servidor else "pendente base da Camara"
            )
            if valor_bruto is None:
                valor_bruto = subsidios_legais["Vereador"]
                valor_liquido = None
                fonte_salario = "lei-804-2023"

            rows_vereadores.append(
                {
                    "esfera": "Legislativo",
                    "cargo": "Vereador",
                    "nome": vereador.nome,
                    "orgao": "Camara Municipal",
                    "vinculo": servidor.get("vinculo") if servidor else "-",
                    "valor_bruto": valor_bruto,
                    "valor_liquido": valor_liquido,
                    "fonte_salario": fonte_salario,
                    "funcao": servidor.get("funcao") if servidor else "",
                }
            )

        rows_servidores = [
            {
                "esfera": "Executivo",
                "cargo": "Servidor",
                "nome": servidor.get("nome"),
                "orgao": servidor.get("orgao"),
                "vinculo": servidor.get("vinculo") or "-",
                "funcao": servidor.get("funcao") or "-",
                "valor_bruto": servidor.get("valor_bruto") or Decimal("0"),
                "valor_liquido": servidor.get("valor_liquido") or Decimal("0"),
                "fonte_salario": servidor.get("fonte"),
                "matricula": servidor.get("matricula") or "-",
            }
            for servidor in servidores
        ]

        total_bruto = sum(
            (item.get("valor_bruto") or Decimal("0")) for item in servidores
        )
        total_liquido = sum(
            (item.get("valor_liquido") or Decimal("0")) for item in servidores
        )
        estrategicos_sem_salario = sum(
            1 for item in rows_estrategicos if item.get("valor_bruto") is None
        )
        vereadores_sem_salario = sum(
            1 for item in rows_vereadores if item.get("valor_bruto") is None
        )

        # Search and paginate servidores
        search = self.request.GET.get("search", "").strip()
        filtered_servidores = rows_servidores
        if search:
            search_lower = search.lower()
            filtered_servidores = [
                r for r in rows_servidores
                if search_lower in (r["nome"] or "").lower()
                or search_lower in (r["orgao"] or "").lower()
            ]

        paginator = Paginator(filtered_servidores, 25)
        page_number = self.request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)

        context.update(
            {
                "resumo": {
                    "estrategicos": len(rows_estrategicos),
                    "vereadores": len(rows_vereadores),
                    "servidores": len(rows_servidores),
                    "total_bruto": total_bruto,
                    "total_liquido": total_liquido,
                    "estrategicos_sem_salario": estrategicos_sem_salario,
                    "vereadores_sem_salario": vereadores_sem_salario,
                    "fonte_principal": "export-folha-2026-01"
                    if folha_export
                    else "banco-local",
                },
                "rows_estrategicos": rows_estrategicos,
                "rows_vereadores": rows_vereadores,
                "page_obj": page_obj,
                "search": search,
                "referencias_legais": {
                    "lei_804": {
                        "url": "https://www.tibaudosul.rn.leg.br/processo-legislativo-1/leis-municipais/lei-ordinaria-municipal/2023/lei-ordinaria-municipal-no-804-de-18-de-maio-de-2023/at_download/file",
                        "vereador": subsidios_legais["Vereador"],
                        "vereador_presidente": subsidios_legais["Vereador Presidente"],
                    },
                    "lei_805": {
                        "url": "https://www.tibaudosul.rn.leg.br/processo-legislativo-1/leis-municipais/lei-ordinaria-municipal/2023/lei-ordinaria-municipal-no-805-de-18-de-maio-de-2023/at_download/file",
                        "prefeito": subsidios_legais["Prefeito"],
                        "vice_prefeito": subsidios_legais["Vice-prefeito"],
                        "secretario": subsidios_legais["Secretario"],
                    },
                },
            }
        )
        return context


class FontesAuditoriaView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "dashboard/fontes.html"
    login_url = "/admin/login/"

    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        if user.is_staff or user.is_superuser:
            return True
        return user.groups.filter(name__in=["analista", "admin"]).exists()

    def get_context_data(self, **kwargs):
        from django.contrib.admin.models import LogEntry

        from apps.ingestao.models import DataProvenance, SyncRun

        context = super().get_context_data(**kwargs)
        context["sync_runs"] = SyncRun.objects.order_by("-iniciado_em")[:30]
        context["fontes"] = DataProvenance.objects.order_by("-coletado_em")[:100]
        context["auditoria_manual"] = LogEntry.objects.select_related(
            "user", "content_type"
        ).order_by("-action_time")[:30]

        provenance_counts = {
            row["fonte"]: row["total"]
            for row in DataProvenance.objects.values("fonte")
            .annotate(total=Count("id"))
            .order_by()
        }
        score_rows = []
        for item in metricas_jobs():
            lat = item.get("latencia_media_ms") or 0
            taxa = item.get("taxa_falha") or 0
            prov = provenance_counts.get(item["fonte"], 0)

            confiabilidade = max(0, 100 - taxa)
            completude = min(100, 40 + (prov // 10) * 5)
            if lat <= 2000:
                desempenho = 100
            elif lat <= 10000:
                desempenho = 75
            elif lat <= 30000:
                desempenho = 55
            else:
                desempenho = 35

            score = round(
                (confiabilidade * 0.5) + (completude * 0.3) + (desempenho * 0.2), 1
            )
            if score >= 80:
                nivel = "alto"
            elif score >= 60:
                nivel = "medio"
            else:
                nivel = "baixo"

            score_rows.append(
                {
                    "fonte": item["fonte"],
                    "score": score,
                    "nivel": nivel,
                    "confiabilidade": confiabilidade,
                    "completude": completude,
                    "desempenho": desempenho,
                    "taxa_falha": taxa,
                    "latencia_media_ms": lat,
                    "provenance_total": prov,
                }
            )

        context["source_scores"] = sorted(
            score_rows, key=lambda row: row["score"], reverse=True
        )
        return context


class EmendasView(TemplateView):
    template_name = "dashboard/emendas.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search = self.request.GET.get("search", "").strip()
        tipo = self.request.GET.get("tipo", "").strip()
        origem_recurso = self.request.GET.get("origem_recurso", "").strip()

        queryset = Emenda.objects.all()
        if search:
            queryset = queryset.filter(
                Q(autoria__icontains=search)
                | Q(objeto__icontains=search)
                | Q(beneficiario__icontains=search)
            )
        if tipo:
            queryset = queryset.filter(tipo__iexact=tipo)
        if origem_recurso:
            queryset = queryset.filter(origem_recurso__iexact=origem_recurso)

        totais = queryset.aggregate(
            previsto=Sum("valor_previsto"),
            empenhado=Sum("valor_empenhado"),
            liquidado=Sum("valor_liquidado"),
            pago=Sum("valor_pago"),
        )
        total_previsto = totais.get("previsto") or 0
        total_empenhado = totais.get("empenhado") or 0
        total_pago = totais.get("pago") or 0

        paginator = Paginator(queryset, 25)
        page_number = self.request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)

        tipos = list(
            Emenda.objects.values_list("tipo", flat=True)
            .distinct()
            .order_by("tipo")
        )
        origens = list(
            Emenda.objects.values_list("origem_recurso", flat=True)
            .distinct()
            .order_by("origem_recurso")
        )

        context.update(
            {
                "page_obj": page_obj,
                "search": search,
                "tipo": tipo,
                "origem_recurso": origem_recurso,
                "tipos": [t for t in tipos if t],
                "origens": [o for o in origens if o],
                "resumo": {
                    "quantidade": queryset.count(),
                    "previsto": total_previsto,
                    "empenhado": total_empenhado,
                    "pago": total_pago,
                },
                "insights": [
                    (
                        "A execucao financeira das emendas esta em "
                        f"{(total_empenhado / total_previsto * 100) if total_previsto else 0:.1f}% "
                        "do previsto."
                    ),
                    "Valores pagos tendem a ser inferiores ao realizado em estagios iniciais.",
                    "Priorize monitorar emendas com maior valor previsto e baixa execucao.",
                ],
            }
        )
        return context


class OrcamentoDetalhadoView(TemplateView):
    template_name = "dashboard/orcamento-detalhado.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search = self.request.GET.get("search", "").strip()
        funcao = self.request.GET.get("funcao", "").strip()

        queryset = OrcamentoItem.objects.all()
        if search:
            queryset = queryset.filter(
                Q(unidade__icontains=search) | Q(acao__icontains=search)
            )
        if funcao:
            queryset = queryset.filter(funcao__iexact=funcao)

        totais = queryset.aggregate(
            inicial=Sum("valor_inicial"),
            atualizado=Sum("valor_atualizado"),
            disponivel=Sum("valor_disponivel"),
        )
        total_inicial = totais.get("inicial") or 0
        total_atualizado = totais.get("atualizado") or 0
        total_disponivel = totais.get("disponivel") or 0

        paginator = Paginator(queryset, 25)
        page_number = self.request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)

        funcoes = list(
            OrcamentoItem.objects.values_list("funcao", flat=True)
            .distinct()
            .order_by("funcao")
        )
        context.update(
            {
                "page_obj": page_obj,
                "search": search,
                "funcao": funcao,
                "funcoes": [f for f in funcoes if f],
                "resumo": {
                    "quantidade": queryset.count(),
                    "inicial": total_inicial,
                    "atualizado": total_atualizado,
                    "disponivel": total_disponivel,
                },
                "insights": [
                    (
                        "A disponibilidade atual representa "
                        f"{(total_disponivel / total_inicial * 100) if total_inicial else 0:.1f}% "
                        "do orcamento inicial."
                    ),
                    "Registros com orcamento atualizado zerado exigem validacao da fonte.",
                    "Use o detalhamento por unidade e acao para auditoria setorial.",
                ],
            }
        )
        return context
