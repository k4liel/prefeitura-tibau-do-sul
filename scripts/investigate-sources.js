const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

const OUTPUT_DIR = path.join(__dirname, "..", "data", "investigation");
fs.mkdirSync(OUTPUT_DIR, { recursive: true });

function save(name, data) {
  const fp = path.join(OUTPUT_DIR, name);
  fs.writeFileSync(fp, typeof data === "string" ? data : JSON.stringify(data, null, 2));
  console.log(`  -> Saved: ${name} (${fs.statSync(fp).size} bytes)`);
}

async function fetchJson(page, url, label) {
  console.log(`\n[FETCH] ${label}: ${url}`);
  try {
    const resp = await page.request.get(url, { timeout: 15000 });
    const status = resp.status();
    console.log(`  Status: ${status}`);
    if (status === 200) {
      const text = await resp.text();
      try {
        const json = JSON.parse(text);
        const count = Array.isArray(json) ? json.length : (json.data ? (Array.isArray(json.data) ? json.data.length : 1) : 1);
        console.log(`  Records: ${count}`);
        return { ok: true, status, data: json, count };
      } catch {
        console.log(`  Not JSON, text length: ${text.length}`);
        return { ok: true, status, data: text, count: 0 };
      }
    }
    return { ok: false, status, data: null, count: 0 };
  } catch (err) {
    console.log(`  ERROR: ${err.message}`);
    return { ok: false, status: 0, data: null, count: 0, error: err.message };
  }
}

async function investigateTopSolutions(page) {
  console.log("\n========================================");
  console.log("INVESTIGATING: TopSolutions Portal");
  console.log("========================================");

  const BASE_PREF = "https://pmtibausulrn.apitransparencia.topsolutionsrn.com.br";
  const BASE_CAM = "https://camaratibaudosul.apitransparencia.topsolutionsrn.com.br";

  // Prefeitura endpoints to discover
  const prefEndpoints = [
    { path: "/api/Receita?numExercicio=2025", label: "Receita 2025" },
    { path: "/api/Despesa?numExercicio=2025", label: "Despesa 2025" },
    { path: "/api/Orcamento?numExercicio=2025", label: "Orcamento 2025" },
    { path: "/api/Licitacao?numExercicio=2025", label: "Licitacao 2025" },
    { path: "/api/Contrato?numExercicio=2025", label: "Contrato 2025" },
    { path: "/api/Emenda?numExercicio=2025", label: "Emenda 2025" },
    { path: "/api/Diaria?numExercicio=2025", label: "Diaria 2025" },
    { path: "/api/Obra?numExercicio=2025", label: "Obra 2025" },
    { path: "/api/PCA?numExercicio=2025", label: "PCA 2025" },
    { path: "/api/FolhaPagamento?numExercicio=2025", label: "Folha Pagamento 2025" },
    { path: "/api/FolhaPagamento?numExercicio=2026&numMes=1", label: "Folha Pagamento Jan 2026" },
    { path: "/api/Servidor?numExercicio=2025", label: "Servidor 2025" },
    { path: "/api/Servidor?numExercicio=2026", label: "Servidor 2026" },
    { path: "/api/UnidadeGestora", label: "Unidades Gestoras" },
    { path: "/api/OrgaoEntidade", label: "Orgaos e Entidades" },
    { path: "/api/VeiculoOficial?numExercicio=2025", label: "Veiculo Oficial 2025" },
    { path: "/api/Patrimonio?numExercicio=2025", label: "Patrimonio 2025" },
    { path: "/api/Convenio?numExercicio=2025", label: "Convenio 2025" },
    { path: "/api/Transferencia?numExercicio=2025", label: "Transferencia 2025" },
    { path: "/api/NotaFiscal?numExercicio=2025", label: "Nota Fiscal 2025" },
    { path: "/api/OrdemPagamento?numExercicio=2025", label: "Ordem Pagamento 2025" },
    { path: "/api/Empenho?numExercicio=2025", label: "Empenho 2025" },
    { path: "/api/Liquidacao?numExercicio=2025", label: "Liquidacao 2025" },
    { path: "/api/Pagamento?numExercicio=2025", label: "Pagamento 2025" },
    { path: "/api/Precatorio?numExercicio=2025", label: "Precatorio 2025" },
    { path: "/api/DividaAtiva?numExercicio=2025", label: "Divida Ativa 2025" },
    { path: "/api/Adiantamento?numExercicio=2025", label: "Adiantamento 2025" },
    { path: "/api/PassagemAerea?numExercicio=2025", label: "Passagem Aerea 2025" },
    { path: "/api/CartaoCredito?numExercicio=2025", label: "Cartao Credito 2025" },
    { path: "/api/ConcursoPublico", label: "Concurso Publico" },
    { path: "/api/ProcessoSeletivo", label: "Processo Seletivo" },
    { path: "/api/ComprasPublicas?numExercicio=2025", label: "Compras Publicas 2025" },
  ];

  // Câmara endpoints
  const camEndpoints = [
    { path: "/api/Vereador", label: "Vereadores (Cam)" },
    { path: "/api/MesaDiretora", label: "Mesa Diretora (Cam)" },
    { path: "/api/Comissao", label: "Comissoes (Cam)" },
    { path: "/api/Legislatura", label: "Legislatura (Cam)" },
    { path: "/api/ProjetoLei?numExercicio=2025", label: "Projeto de Lei 2025 (Cam)" },
    { path: "/api/Sessao?numExercicio=2025", label: "Sessao 2025 (Cam)" },
    { path: "/api/Indicacao?numExercicio=2025", label: "Indicacao 2025 (Cam)" },
    { path: "/api/Requerimento?numExercicio=2025", label: "Requerimento 2025 (Cam)" },
    { path: "/api/Mocao?numExercicio=2025", label: "Mocao 2025 (Cam)" },
    { path: "/api/FolhaPagamento?numExercicio=2025", label: "Folha Cam 2025" },
    { path: "/api/Receita?numExercicio=2025", label: "Receita Cam 2025" },
    { path: "/api/Despesa?numExercicio=2025", label: "Despesa Cam 2025" },
    { path: "/api/Contrato?numExercicio=2025", label: "Contrato Cam 2025" },
    { path: "/api/Licitacao?numExercicio=2025", label: "Licitacao Cam 2025" },
    { path: "/api/Diaria?numExercicio=2025", label: "Diaria Cam 2025" },
  ];

  const results = { prefeitura: {}, camara: {} };

  for (const ep of prefEndpoints) {
    const r = await fetchJson(page, BASE_PREF + ep.path, ep.label);
    results.prefeitura[ep.label] = { url: BASE_PREF + ep.path, ok: r.ok, status: r.status, count: r.count, error: r.error };
    if (r.ok && r.data && r.count > 0 && typeof r.data !== "string") {
      save(`topsolutions-pref-${ep.label.toLowerCase().replace(/\s+/g, "-")}.json`,
        Array.isArray(r.data) ? r.data.slice(0, 5) : r.data);
    }
  }

  for (const ep of camEndpoints) {
    const r = await fetchJson(page, BASE_CAM + ep.path, ep.label);
    results.camara[ep.label] = { url: BASE_CAM + ep.path, ok: r.ok, status: r.status, count: r.count, error: r.error };
    if (r.ok && r.data && r.count > 0 && typeof r.data !== "string") {
      save(`topsolutions-cam-${ep.label.toLowerCase().replace(/\s+/g, "-")}.json`,
        Array.isArray(r.data) ? r.data.slice(0, 5) : r.data);
    }
  }

  save("topsolutions-discovery.json", results);
  return results;
}

async function investigateTCERN(page) {
  console.log("\n========================================");
  console.log("INVESTIGATING: TCE-RN APIs");
  console.log("========================================");

  const BASE = "https://apidadosabertos.tce.rn.gov.br";
  const UNIT_ID = 494;

  const endpoints = [
    { path: `/api/ProcedimentosLicitatoriosApi/LicitacaoPublica/Json/${UNIT_ID}/01-01-2025_31-12-2025`, label: "Licitacoes 2025" },
    { path: `/api/ContratosApi/Contratos/Json/${UNIT_ID}/true`, label: "Contratos" },
    { path: `/api/BalancoOrcamentarioApi/Receita/Json/2025/6/${UNIT_ID}`, label: "Receita 2025" },
    { path: `/api/BalancoOrcamentarioApi/Despesa/Json/2025/6/${UNIT_ID}`, label: "Despesa 2025" },
    { path: `/api/FolhaDePagamentoApi/FolhaDePagamento/Json/${UNIT_ID}/2025/12`, label: "Folha Dez 2025" },
    { path: `/api/FolhaDePagamentoApi/FolhaDePagamento/Json/${UNIT_ID}/2026/1`, label: "Folha Jan 2026" },
    { path: `/api/DespesasApi/Empenhos/Json/${UNIT_ID}/2025`, label: "Empenhos 2025" },
    { path: `/api/DespesasApi/Liquidacoes/Json/${UNIT_ID}/2025`, label: "Liquidacoes 2025" },
    { path: `/api/DespesasApi/Pagamentos/Json/${UNIT_ID}/2025`, label: "Pagamentos 2025" },
    { path: `/api/ReceitaApi/Receitas/Json/${UNIT_ID}/2025`, label: "Receitas Detalhadas 2025" },
    { path: `/api/DiariasApi/Diarias/Json/${UNIT_ID}/01-01-2025_31-12-2025`, label: "Diarias TCE 2025" },
    { path: `/api/ObrasApi/Obras/Json/${UNIT_ID}`, label: "Obras TCE" },
    { path: `/api/PessoalApi/Pessoal/Json/${UNIT_ID}/2025/12`, label: "Pessoal TCE Dez 2025" },
    { path: `/api/TransparenciaApi/InfoMunicipais/Json/${UNIT_ID}`, label: "Info Municipais" },
    { path: `/api/TransparenciaApi/SiteTransparencia/Json/${UNIT_ID}`, label: "Site Transparencia" },
    { path: `/api/ConveniosApi/Convenios/Json/${UNIT_ID}`, label: "Convenios TCE" },
    { path: `/api/VeiculosApi/Veiculos/Json/${UNIT_ID}`, label: "Veiculos TCE" },
    { path: `/api/PatrimonioApi/Bens/Json/${UNIT_ID}`, label: "Patrimonio TCE" },
  ];

  const results = {};

  for (const ep of endpoints) {
    const r = await fetchJson(page, BASE + ep.path, ep.label);
    results[ep.label] = { url: BASE + ep.path, ok: r.ok, status: r.status, count: r.count, error: r.error };
    if (r.ok && r.data && r.count > 0 && typeof r.data !== "string") {
      save(`tcern-${ep.label.toLowerCase().replace(/\s+/g, "-")}.json`,
        Array.isArray(r.data) ? r.data.slice(0, 3) : r.data);
    }
  }

  save("tcern-discovery.json", results);
  return results;
}

async function investigateIBGE(page) {
  console.log("\n========================================");
  console.log("INVESTIGATING: IBGE APIs");
  console.log("========================================");

  const COD = "2414209";

  const endpoints = [
    { url: `https://servicodados.ibge.gov.br/api/v1/localidades/municipios/${COD}`, label: "Dados Basicos" },
    { url: `https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/2024/variaveis/9324?localidades=N6[${COD}]`, label: "Populacao Estimada" },
    { url: `https://servicodados.ibge.gov.br/api/v3/agregados/4714/periodos/2010/variaveis/93|60|5918?localidades=N6[${COD}]`, label: "IDHM 2010" },
    { url: `https://servicodados.ibge.gov.br/api/v3/agregados/5938/periodos/2021/variaveis/37?localidades=N6[${COD}]`, label: "PIB" },
    { url: `https://servicodados.ibge.gov.br/api/v3/agregados/1301/periodos/2022/variaveis/616?localidades=N6[${COD}]`, label: "PIB per capita" },
    { url: `https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/2022/variaveis/9324?localidades=N6[${COD}]`, label: "Censo 2022" },
    { url: `https://cidades.ibge.gov.br/brasil/rn/tibau-do-sul/panorama`, label: "Panorama IBGE (HTML)" },
  ];

  const results = {};

  for (const ep of endpoints) {
    const r = await fetchJson(page, ep.url, ep.label);
    results[ep.label] = { url: ep.url, ok: r.ok, status: r.status, count: r.count, error: r.error };
    if (r.ok && r.data && typeof r.data !== "string") {
      save(`ibge-${ep.label.toLowerCase().replace(/\s+/g, "-")}.json`, r.data);
    }
  }

  save("ibge-discovery.json", results);
  return results;
}

async function investigatePortalTransparencia(page) {
  console.log("\n========================================");
  console.log("INVESTIGATING: Portal Transparencia (dados abertos)");
  console.log("========================================");

  const portalUrl = "https://dadosabertos.topsolutionsrn.com.br/pmtibausulrn";
  console.log(`\n[BROWSE] ${portalUrl}`);

  try {
    await page.goto(portalUrl, { timeout: 20000, waitUntil: "domcontentloaded" });
    await page.waitForTimeout(3000);

    const title = await page.title();
    console.log(`  Title: ${title}`);

    const links = await page.evaluate(() => {
      const anchors = document.querySelectorAll("a[href]");
      return Array.from(anchors).map(a => ({
        text: a.textContent.trim().substring(0, 100),
        href: a.href,
      })).filter(l => l.href.includes("api") || l.href.includes("dados") || l.href.includes("download") || l.href.includes("csv") || l.href.includes("json"));
    });

    console.log(`  Found ${links.length} data-related links`);
    save("portal-transparencia-links.json", links);

    const pageContent = await page.evaluate(() => {
      const sections = document.querySelectorAll("h1, h2, h3, h4, [class*='card'], [class*='section']");
      return Array.from(sections).map(el => ({
        tag: el.tagName,
        text: el.textContent.trim().substring(0, 200),
        class: el.className,
      }));
    });
    save("portal-transparencia-structure.json", pageContent);
  } catch (err) {
    console.log(`  ERROR: ${err.message}`);
  }
}

async function investigatePrefeituraWebsite(page) {
  console.log("\n========================================");
  console.log("INVESTIGATING: Prefeitura Official Website");
  console.log("========================================");

  const urls = [
    "https://tibaudosul.rn.gov.br/",
    "https://tibaudosul.rn.gov.br/secretarias/",
    "https://tibaudosul.rn.gov.br/o-municipio/sobre-o-municipio/",
  ];

  for (const url of urls) {
    console.log(`\n[BROWSE] ${url}`);
    try {
      await page.goto(url, { timeout: 15000, waitUntil: "domcontentloaded" });
      await page.waitForTimeout(2000);

      const data = await page.evaluate(() => {
        const result = { title: document.title, sections: [], links: [] };

        document.querySelectorAll("h1, h2, h3, h4, h5").forEach(el => {
          result.sections.push({ tag: el.tagName, text: el.textContent.trim().substring(0, 200) });
        });

        document.querySelectorAll("a[href]").forEach(a => {
          const href = a.href;
          if (href.includes("secretaria") || href.includes("orgao") || href.includes("gestor") || href.includes("equipe")) {
            result.links.push({ text: a.textContent.trim().substring(0, 100), href });
          }
        });

        // Try to find secretary/department info
        const articleContent = document.querySelector("article, .entry-content, .page-content, main");
        if (articleContent) {
          result.mainContent = articleContent.textContent.trim().substring(0, 3000);
        }

        return result;
      });

      save(`website-${url.split("/").filter(Boolean).pop() || "home"}.json`, data);
    } catch (err) {
      console.log(`  ERROR: ${err.message}`);
    }
  }
}

(async () => {
  console.log("=== PREFEITURA TIBAU DO SUL - DATA SOURCE INVESTIGATION ===");
  console.log(`Date: ${new Date().toISOString()}\n`);

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    ignoreHTTPSErrors: true,
  });
  const page = await context.newPage();

  const summary = {};

  try {
    summary.topsolutions = await investigateTopSolutions(page);
    summary.tcern = await investigateTCERN(page);
    summary.ibge = await investigateIBGE(page);
    await investigatePortalTransparencia(page);
    await investigatePrefeituraWebsite(page);
  } catch (err) {
    console.error("Fatal error:", err);
  }

  // Summary report
  console.log("\n\n========================================");
  console.log("DISCOVERY SUMMARY");
  console.log("========================================");

  const countAvailable = (obj) => Object.values(obj).filter(v => v.ok).length;
  const countTotal = (obj) => Object.keys(obj).length;

  if (summary.topsolutions) {
    console.log(`\nTopSolutions Prefeitura: ${countAvailable(summary.topsolutions.prefeitura)}/${countTotal(summary.topsolutions.prefeitura)} endpoints available`);
    console.log(`TopSolutions Camara: ${countAvailable(summary.topsolutions.camara)}/${countTotal(summary.topsolutions.camara)} endpoints available`);
  }
  if (summary.tcern) {
    console.log(`TCE-RN: ${countAvailable(summary.tcern)}/${countTotal(summary.tcern)} endpoints available`);
  }
  if (summary.ibge) {
    console.log(`IBGE: ${countAvailable(summary.ibge)}/${countTotal(summary.ibge)} endpoints available`);
  }

  save("full-discovery-summary.json", summary);

  await browser.close();
  console.log("\nInvestigation complete. Check data/investigation/ for all results.");
})();
