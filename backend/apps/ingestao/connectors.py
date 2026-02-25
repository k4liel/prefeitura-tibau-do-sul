import gzip
import html
import json
import re
import urllib.parse
import urllib.request
from decimal import Decimal
from urllib.error import HTTPError


class ConnectorError(Exception):
    pass


def _fetch_json(url: str, timeout: int = 30):
    try:
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json,text/plain,*/*",
                "Accept-Encoding": "gzip, deflate",
                "User-Agent": "Mozilla/5.0",
            },
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
            if response.headers.get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            return json.loads(raw.decode("utf-8", errors="ignore"))
    except Exception as exc:  # noqa: BLE001
        raise ConnectorError(f"Falha ao consultar {url}: {exc}") from exc


def _fetch_json_status(url: str, timeout: int = 30):
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json,text/plain,*/*",
            "Accept-Encoding": "gzip, deflate",
            "User-Agent": "Mozilla/5.0",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
            if response.headers.get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            payload = json.loads(raw.decode("utf-8", errors="ignore"))
            return {
                "ok": True,
                "status_code": response.status,
                "payload": payload,
                "error_code": "",
            }
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        error_code = ""
        try:
            parsed = json.loads(body)
            error_code = (
                parsed.get("metadata", {}).get("message")
                if isinstance(parsed, dict)
                else ""
            ) or ""
        except Exception:  # noqa: BLE001
            pass
        return {
            "ok": False,
            "status_code": exc.code,
            "payload": {},
            "error_code": error_code,
            "error_text": body,
            "raw_body": body,
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "status_code": 0,
            "payload": {},
            "error_code": "NETWORK",
            "error_text": str(exc),
            "raw_body": str(exc),
        }


def _build_url_with_params(base_url: str, params: dict):
    if not params:
        return base_url
    query = urllib.parse.urlencode(params, doseq=True)
    return f"{base_url}?{query}"


def _probe_topsolutions_endpoint(endpoint: str, candidate_params: list[dict]):
    attempts = []
    for params in candidate_params:
        target_url = _build_url_with_params(endpoint, params)
        response = _fetch_json_status(target_url, timeout=90)
        payload = response.get("payload", {})
        rows = payload.get("data", []) if isinstance(payload, dict) else payload
        rows_count = len(rows) if isinstance(rows, list) else 0

        attempt = {
            "url": target_url,
            "ok": bool(response.get("ok")),
            "status_code": int(response.get("status_code") or 0),
            "error_code": response.get("error_code") or "",
            "count": rows_count,
            "params": params,
        }
        attempts.append(attempt)

        if attempt["ok"]:
            return {
                "ok": True,
                "status_code": attempt["status_code"],
                "error_code": "",
                "count": rows_count,
                "url": target_url,
                "resolved_params": params,
                "attempts": attempts,
            }

    last = attempts[-1] if attempts else {}
    return {
        "ok": False,
        "status_code": last.get("status_code", 0),
        "error_code": last.get("error_code", ""),
        "count": 0,
        "url": last.get("url", endpoint),
        "resolved_params": {},
        "attempts": attempts,
    }


def fetch_prefeitura_2025(base_url: str):
    return {
        "receitas": _fetch_json(
            f"{base_url}/receitaprevistaarrecadada/receitaprevistaarrecadadaasync?classificacaoPor=receita&numExercicio=2025&mesIni=1&mesFim=12"
        ),
        "despesas": _fetch_json(
            f"{base_url}/despesa/despesaporclassificacaoasync?strClassificarPor=orgao&dtIni=01/01/2025&dtFim=31/12/2025"
        ),
        "licitacoes": _fetch_json(
            f"{base_url}/licitacao/licitacaopordataasync?dtInicio=2025-01-01&dtFim=2025-12-31"
        ),
        "contratos": _fetch_json(
            f"{base_url}/contrato/contratopordataasync?dtInicio=2025-01-01&dtFim=2025-12-31"
        ),
    }


def fetch_camara_topsolutions(base_url: str):
    return {
        "vereadores": _fetch_json(f"{base_url}/vereador/vereadorasync?exercicio=2025"),
        "mesa_diretora": _fetch_json(
            f"{base_url}/mesa/mesadiretoraasync?exercicio=2025"
        ),
        "comissoes": _fetch_json(f"{base_url}/comissao/comissaoasync?exercicio=2025"),
    }


def fetch_camara_portal(legislativo_url: str):
    encoded = urllib.parse.quote(legislativo_url, safe="")
    endpoint = f"https://www.portalcr2.com.br/api/1.1/init/data?location={encoded}"
    return _fetch_json(endpoint)


def _fetch_text(url: str, timeout: int = 30):
    try:
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "text/html,application/json,*/*",
                "Accept-Encoding": "gzip, deflate",
                "User-Agent": "Mozilla/5.0",
            },
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
            if response.headers.get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            return raw.decode("utf-8", errors="ignore")
    except Exception as exc:  # noqa: BLE001
        raise ConnectorError(f"Falha ao consultar {url}: {exc}") from exc


def _to_decimal(value):
    try:
        text = str(value).strip()
        if "," in text and "." in text:
            text = text.replace(".", "").replace(",", ".")
        elif "," in text:
            text = text.replace(",", ".")
        return Decimal(text)
    except Exception:  # noqa: BLE001
        return Decimal("0")


def fetch_ibge_municipio_contexto():
    cidade_api = _fetch_json(
        "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/2414209"
    )
    pop_est = _fetch_json(
        "https://apisidra.ibge.gov.br/values/t/6579/n6/2414209/v/9324/p/2025"
    )
    pop_2025 = int(pop_est[1]["V"]) if len(pop_est) > 1 else 0

    cidade_page = _fetch_text(
        "https://www.ibge.gov.br/cidades-e-estados/rn/tibau-do-sul.html"
    )

    indicadores = {}
    pattern = re.compile(
        r"<img alt='([^']+)'[^>]*><p>(.*?)</p></div><p class='ind-value'>(.*?)</p>",
        re.S,
    )
    for _alt, label, value in pattern.findall(cidade_page):
        label_clean = html.unescape(re.sub("<[^>]+>", "", label)).strip()
        value_clean = html.unescape(re.sub("<[^>]+>", " ", value)).replace("\xa0", " ")
        value_clean = re.sub(r"\s+", " ", value_clean).strip()
        indicadores[label_clean] = value_clean

    return {
        "municipio": cidade_api.get("nome"),
        "codigo_ibge": str(cidade_api.get("id")),
        "uf": cidade_api.get("microrregiao", {})
        .get("mesorregiao", {})
        .get("UF", {})
        .get("sigla"),
        "regiao_imediata": cidade_api.get("regiao-imediata", {}).get("nome"),
        "regiao_intermediaria": cidade_api.get("regiao-imediata", {})
        .get("regiao-intermediaria", {})
        .get("nome"),
        "populacao_estimada_2025": pop_2025,
        "area_territorial": indicadores.get("Área Territorial", ""),
        "populacao_censo_2022": indicadores.get("População no último censo", ""),
        "densidade_demografica": indicadores.get("Densidade demográfica", ""),
        "escolarizacao_6_14": indicadores.get("Escolarização 6 a 14 anos", ""),
        "idhm": indicadores.get("IDHM Índice de desenvolvimento humano municipal", ""),
        "mortalidade_infantil": indicadores.get("Mortalidade infantil", ""),
        "receita_bruta_2024": indicadores.get(
            "Total de receitas brutas realizadas", ""
        ),
        "despesa_bruta_2024": indicadores.get(
            "Total de despesas brutas empenhadas", ""
        ),
        "pib_per_capita": indicadores.get("PIB per capita", ""),
        "fonte": "IBGE Cidades e Estados / SIDRA",
    }


def fetch_tce_municipio_contexto(identificador_unidade: int = 494, ano: int = 2025):
    base = "https://apidadosabertos.tce.rn.gov.br"
    licitacoes = _fetch_json(
        f"{base}/api/ProcedimentosLicitatoriosApi/LicitacaoPublica/Json/{identificador_unidade}/{ano}-01-01/{ano}-12-31",
        timeout=120,
    )
    contratos = _fetch_json(
        f"{base}/api/ContratosApi/Contratos/Json/{identificador_unidade}/true",
        timeout=120,
    )
    receita = _fetch_json(
        f"{base}/api/BalancoOrcamentarioApi/Receita/Json/{ano}/6/{identificador_unidade}",
        timeout=120,
    )
    despesa = _fetch_json(
        f"{base}/api/BalancoOrcamentarioApi/Despesa/Json/{ano}/6/{identificador_unidade}",
        timeout=120,
    )

    processos = {}
    lotes = set()
    status_por_processo = {}
    for item in licitacoes:
        numero = str(item.get("numeroLicitacao") or "").strip()
        ano_licit = str(item.get("anoLicitacao") or ano).strip()
        if not numero:
            continue
        processo = f"{ano_licit}/{numero}"
        valor = _to_decimal(item.get("valorTotalOrcado"))
        processos[processo] = max(processos.get(processo, Decimal("0")), valor)

        lote = str(item.get("numeroLote") or "").strip()
        if lote:
            lotes.add(f"{processo}-{lote}")

        status = str(item.get("situacaoProcedimentoLicitacao") or "").upper().strip()
        status_por_processo.setdefault(processo, set()).add(status)

    homologadas = 0
    em_andamento = 0
    for statuses in status_por_processo.values():
        joined = " ".join(statuses)
        if "HOMOLOG" in joined or "CONCLU" in joined or "FINALIZ" in joined:
            homologadas += 1
        else:
            em_andamento += 1

    return {
        "fonte": "API Dados Abertos TCE-RN",
        "identificador_unidade": identificador_unidade,
        "ano": ano,
        "licitacoes_qtd": len(licitacoes),
        "licitacoes_processos_unicos": len(processos),
        "licitacoes_lotes_unicos": len(lotes),
        "licitacoes_homologadas": homologadas,
        "licitacoes_em_andamento": em_andamento,
        "licitacoes_valor_total_orcado_unico": float(sum(processos.values())),
        "licitacoes_valor_total_orcado": float(
            sum(_to_decimal(item.get("valorTotalOrcado")) for item in licitacoes)
        ),
        "contratos_qtd": len(contratos),
        "contratos_valor_total": float(
            sum(_to_decimal(item.get("valorContrato")) for item in contratos)
        ),
        "receita_prevista": float(
            sum(_to_decimal(item.get("valorPrevistoAtualizado")) for item in receita)
        ),
        "receita_realizada": float(
            sum(_to_decimal(item.get("valorRealizadoNoExecicio")) for item in receita)
        ),
        "despesa_dotacao_atualizada": float(
            sum(_to_decimal(item.get("valorDotacaoAtualizada")) for item in despesa)
        ),
        "despesa_empenhada": float(
            sum(_to_decimal(item.get("valorEmpenhoAtePeriodo")) for item in despesa)
        ),
        "despesa_liquidada": float(
            sum(_to_decimal(item.get("valorLiquidacaoAtePeriodo")) for item in despesa)
        ),
        "despesa_paga": float(
            sum(_to_decimal(item.get("valorPagoAtePeriodo")) for item in despesa)
        ),
    }


def fetch_topsolutions_municipio_contexto(ano: int = 2025):
    base = "https://dadosabertos.topsolutionsrn.com.br/pmtibausulrn"
    orcamento = _fetch_json(
        f"{base}/orcamento/orcamentoasync?dataInicio=01/01/{ano}&dataFim=31/12/{ano}"
    )
    emendas = _fetch_json(f"{base}/emendaparlamentar/emendaparlamentarasync")

    orc_rows = orcamento.get("data", []) if isinstance(orcamento, dict) else orcamento
    emenda_rows = emendas.get("data", []) if isinstance(emendas, dict) else emendas

    autoria_count = {}
    for item in emenda_rows:
        autoria = str(item.get("autoria") or "N/A").strip()
        autoria_count[autoria] = autoria_count.get(autoria, 0) + 1

    top_autorias = sorted(autoria_count.items(), key=lambda row: row[1], reverse=True)[
        :5
    ]

    return {
        "fonte": "TopSolutions Dados Abertos Prefeitura",
        "ano": ano,
        "orcamento_registros": len(orc_rows),
        "orcamento_inicial_total": float(
            sum(_to_decimal(item.get("vlrOrcamentoInicial")) for item in orc_rows)
        ),
        "orcamento_atualizado_total": float(
            sum(_to_decimal(item.get("vlrOrcamentoAtualizado")) for item in orc_rows)
        ),
        "orcamento_disponivel_total": float(
            sum(_to_decimal(item.get("vlrDisponivel")) for item in orc_rows)
        ),
        "emendas_qtd": len(emenda_rows),
        "emendas_previsto_total": float(
            sum(_to_decimal(item.get("vlrPrevisto")) for item in emenda_rows)
        ),
        "emendas_realizado_total": float(
            sum(_to_decimal(item.get("vlrRealizado")) for item in emenda_rows)
        ),
        "emendas_pago_total": float(
            sum(_to_decimal(item.get("vlrPago")) for item in emenda_rows)
        ),
        "emendas_top_autorias": [
            {"autoria": autoria, "quantidade": qtd} for autoria, qtd in top_autorias
        ],
    }


def fetch_topsolutions_operacionais(ano: int = 2025):
    base = "https://dadosabertos.topsolutionsrn.com.br/pmtibausulrn"
    endpoints = {
        "diarias": {
            "url": f"{base}/diaria/diariaasync",
            "candidates": [
                {},
                {"ano": ano},
                {"exercicio": ano},
                {"numExercicio": ano},
                {"mesIni": 1, "mesFim": 12, "numExercicio": ano},
                {"dataInicio": f"01/01/{ano}", "dataFim": f"31/12/{ano}"},
                {"dtInicio": f"01/01/{ano}", "dtFim": f"31/12/{ano}"},
            ],
        },
        "obras": {
            "url": f"{base}/obra/ObraAsync",
            "candidates": [
                {},
                {"ano": ano},
                {"exercicio": ano},
                {"numExercicio": ano},
                {"dataInicio": f"01/01/{ano}", "dataFim": f"31/12/{ano}"},
                {"dtInicio": f"01/01/{ano}", "dtFim": f"31/12/{ano}"},
                {"strExercicio": ano},
            ],
        },
        "pca": {
            "url": f"{base}/planocontratacaoanual/planocontratacaoanualasync",
            "candidates": [
                {},
                {"ano": ano},
                {"exercicio": ano},
                {"numExercicio": ano},
                {"strExercicio": ano},
                {"dataInicio": f"01/01/{ano}", "dataFim": f"31/12/{ano}"},
                {"dtInicio": f"01/01/{ano}", "dtFim": f"31/12/{ano}"},
            ],
        },
    }

    result = {}
    for key, config in endpoints.items():
        result[key] = _probe_topsolutions_endpoint(
            endpoint=config["url"],
            candidate_params=config["candidates"],
        )
    result["ano"] = ano
    result["fonte"] = "TopSolutions Dados Abertos Prefeitura"
    return result


def fetch_topsolutions_detalhes(ano: int = 2025):
    base = "https://dadosabertos.topsolutionsrn.com.br/pmtibausulrn"
    orcamento = _fetch_json(
        f"{base}/orcamento/orcamentoasync?dataInicio=01/01/{ano}&dataFim=31/12/{ano}",
        timeout=120,
    )
    emendas = _fetch_json(
        f"{base}/emendaparlamentar/emendaparlamentarasync",
        timeout=120,
    )
    return {
        "orcamento": orcamento.get("data", [])
        if isinstance(orcamento, dict)
        else orcamento,
        "emendas": emendas.get("data", []) if isinstance(emendas, dict) else emendas,
    }
