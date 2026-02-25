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

async function fetchJson(page, url, label, timeout = 30000) {
  console.log(`\n[FETCH] ${label}`);
  console.log(`  URL: ${url}`);
  try {
    const resp = await page.request.get(url, { timeout });
    const status = resp.status();
    if (status === 200) {
      const text = await resp.text();
      try {
        const json = JSON.parse(text);
        const data = json.data || json;
        const count = Array.isArray(data) ? data.length : 1;
        console.log(`  OK - ${count} records`);
        return { ok: true, data: json, count };
      } catch {
        console.log(`  OK - text (${text.length} chars)`);
        return { ok: true, data: text, count: 0 };
      }
    }
    console.log(`  FAIL - Status ${status}`);
    return { ok: false, status, data: null };
  } catch (err) {
    console.log(`  ERROR: ${err.message.substring(0, 120)}`);
    return { ok: false, data: null, error: err.message };
  }
}

(async () => {
  console.log("=== CORRECT URL INVESTIGATION ===\n");

  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({
    userAgent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    ignoreHTTPSErrors: true,
  });
  const page = await ctx.newPage();

  const TS_BASE = "https://dadosabertos.topsolutionsrn.com.br/pmtibausulrn";
  const TS_PREF = "https://pmtibausulrn.apitransparencia.topsolutionsrn.com.br";
  const TS_CAM = "https://camaratibaudosul.apitransparencia.topsolutionsrn.com.br";
  const TCE = "https://apidadosabertos.tce.rn.gov.br";

  const results = {};

  // ====== TOPSOLUTIONS - DADOS ABERTOS (correct format) ======
  console.log("========================================");
  console.log("TOPSOLUTIONS - DADOS ABERTOS");
  console.log("========================================");

  const tsEndpoints = [
    { url: `${TS_BASE}/receitaprevistaarrecadada/receitaprevistaarrecadadaasync?classificacaoPor=receita&numExercicio=2025&mesIni=1&mesFim=12`, label: "Receita 2025", file: "ts-receita-2025" },
    { url: `${TS_BASE}/despesa/despesaporclassificacaoasync?strClassificarPor=orgao&dtIni=01/01/2025&dtFim=31/12/2025`, label: "Despesa por Orgao 2025", file: "ts-despesa-orgao-2025" },
    { url: `${TS_BASE}/licitacao/licitacaopordataasync?dtInicio=2025-01-01&dtFim=2025-12-31`, label: "Licitacoes 2025", file: "ts-licitacoes-2025" },
    { url: `${TS_BASE}/contrato/contratopordataasync?dtInicio=2025-01-01&dtFim=2025-12-31`, label: "Contratos 2025", file: "ts-contratos-2025" },
    { url: `${TS_BASE}/orcamento/orcamentoasync?dataInicio=01/01/2025&dataFim=31/12/2025`, label: "Orcamento 2025", file: "ts-orcamento-2025" },
    { url: `${TS_BASE}/emendaparlamentar/emendaparlamentarasync`, label: "Emendas Parlamentares", file: "ts-emendas" },
    // Test new endpoints
    { url: `${TS_BASE}/folhapagamento/folhapagamentoasync?numExercicio=2026&numMes=1`, label: "Folha Jan 2026", file: "ts-folha-2026-01" },
    { url: `${TS_BASE}/folhapagamento/folhapagamentoasync?numExercicio=2025&numMes=12`, label: "Folha Dez 2025", file: "ts-folha-2025-12" },
    { url: `${TS_BASE}/servidor/servidorasync?numExercicio=2026&numMes=1`, label: "Servidores Jan 2026", file: "ts-servidores-2026-01" },
    { url: `${TS_BASE}/diaria/diariaasync`, label: "Diarias (sem params)", file: "ts-diarias" },
    { url: `${TS_BASE}/diaria/diariaasync?numExercicio=2025`, label: "Diarias 2025", file: "ts-diarias-2025" },
    { url: `${TS_BASE}/obra/ObraAsync`, label: "Obras (sem params)", file: "ts-obras" },
    { url: `${TS_BASE}/planocontratacaoanual/planocontratacaoanualasync`, label: "PCA", file: "ts-pca" },
    { url: `${TS_BASE}/despesa/despesaporclassificacaoasync?strClassificarPor=elemento&dtIni=01/01/2025&dtFim=31/12/2025`, label: "Despesa por Elemento 2025", file: "ts-despesa-elemento-2025" },
    { url: `${TS_BASE}/despesa/despesaporclassificacaoasync?strClassificarPor=funcao&dtIni=01/01/2025&dtFim=31/12/2025`, label: "Despesa por Funcao 2025", file: "ts-despesa-funcao-2025" },
    { url: `${TS_BASE}/despesa/despesaporclassificacaoasync?strClassificarPor=fonte&dtIni=01/01/2025&dtFim=31/12/2025`, label: "Despesa por Fonte 2025", file: "ts-despesa-fonte-2025" },
    // Transparency portal endpoints
    { url: `${TS_PREF}/receitaprevistaarrecadada/receitaprevistaarrecadadaasync?classificacaoPor=receita&numExercicio=2025&mesIni=1&mesFim=12`, label: "Receita 2025 (alt)", file: "ts-alt-receita-2025" },
  ];

  for (const ep of tsEndpoints) {
    const r = await fetchJson(page, ep.url, ep.label, 60000);
    results[ep.label] = { ok: r.ok, count: r.count, error: r.error };
    if (r.ok && r.data) {
      const rows = r.data.data || r.data;
      if (Array.isArray(rows)) {
        save(`${ep.file}-sample.json`, rows.slice(0, 3));
        save(`${ep.file}-full.json`, rows);
        results[ep.label].count = rows.length;
      } else {
        save(`${ep.file}.json`, r.data);
      }
    }
  }

  // ====== TOPSOLUTIONS - CAMARA ======
  console.log("\n========================================");
  console.log("TOPSOLUTIONS - CAMARA");
  console.log("========================================");

  const camEndpoints = [
    { url: `${TS_CAM}/vereador/vereadorasync?exercicio=2025`, label: "Vereadores Cam", file: "cam-vereadores" },
    { url: `${TS_CAM}/mesa/mesadiretoraasync?exercicio=2025`, label: "Mesa Diretora Cam", file: "cam-mesa" },
    { url: `${TS_CAM}/comissao/comissaoasync?exercicio=2025`, label: "Comissoes Cam", file: "cam-comissoes" },
    { url: `${TS_BASE}/vereador/vereadorasync?exercicio=2025`, label: "Vereadores DadosAbertos", file: "cam-vereadores-da" },
    { url: `${TS_CAM}/folhapagamento/folhapagamentoasync?numExercicio=2025&numMes=12`, label: "Folha Cam Dez 2025", file: "cam-folha-2025-12" },
    { url: `${TS_CAM}/despesa/despesaporclassificacaoasync?strClassificarPor=orgao&dtIni=01/01/2025&dtFim=31/12/2025`, label: "Despesa Cam 2025", file: "cam-despesa-2025" },
    { url: `${TS_CAM}/receita/receitaprevistaarrecadadaasync?classificacaoPor=receita&numExercicio=2025&mesIni=1&mesFim=12`, label: "Receita Cam 2025 (v2)", file: "cam-receita-2025" },
  ];

  for (const ep of camEndpoints) {
    const r = await fetchJson(page, ep.url, ep.label, 30000);
    results[ep.label] = { ok: r.ok, count: r.count, error: r.error };
    if (r.ok && r.data) {
      const rows = r.data.data || r.data;
      if (Array.isArray(rows)) {
        save(`${ep.file}-full.json`, rows);
        results[ep.label].count = rows.length;
      } else {
        save(`${ep.file}.json`, r.data);
      }
    }
  }

  // ====== TCE-RN (correct format) ======
  console.log("\n========================================");
  console.log("TCE-RN - CORRECT FORMAT");
  console.log("========================================");

  const tceEndpoints = [
    { url: `${TCE}/api/ProcedimentosLicitatoriosApi/LicitacaoPublica/Json/494/2025-01-01/2025-12-31`, label: "Licitacoes TCE 2025", file: "tce-licitacoes-2025" },
    { url: `${TCE}/api/ContratosApi/Contratos/Json/494/true`, label: "Contratos TCE", file: "tce-contratos" },
    { url: `${TCE}/api/BalancoOrcamentarioApi/Despesa/Json/2025/6/494`, label: "Despesa TCE 2025", file: "tce-despesa-2025" },
    { url: `${TCE}/api/BalancoOrcamentarioApi/Receita/Json/2025/6/494`, label: "Receita TCE 2025", file: "tce-receita-2025" },
  ];

  for (const ep of tceEndpoints) {
    const r = await fetchJson(page, ep.url, ep.label, 120000);
    results[ep.label] = { ok: r.ok, count: r.count, error: r.error };
    if (r.ok && r.data) {
      const rows = Array.isArray(r.data) ? r.data : (r.data.data || []);
      save(`${ep.file}-full.json`, rows);
      results[ep.label].count = rows.length;
    }
  }

  // ====== WEBSITE SECRETARIAS ======
  console.log("\n========================================");
  console.log("WEBSITE - SECRETARIAS");
  console.log("========================================");

  try {
    await page.goto("https://tibaudosul.rn.gov.br/secretarias/", { timeout: 15000, waitUntil: "domcontentloaded" });
    await page.waitForTimeout(3000);

    const secretarias = await page.evaluate(() => {
      const items = [];
      document.querySelectorAll("a[href*='secretaria'], a[href*='gabinete'], a[href*='controladoria'], a[href*='procuradoria']").forEach(a => {
        items.push({ name: a.textContent.trim(), url: a.href });
      });
      // Also try to find in menu
      document.querySelectorAll(".menu-item a, .nav-item a, li a").forEach(a => {
        const text = a.textContent.trim();
        if (text.match(/secretaria|gabinete|controlad|procurad|fundo|instituto/i) && !items.find(i => i.url === a.href)) {
          items.push({ name: text, url: a.href });
        }
      });
      return items;
    });

    console.log(`  Found ${secretarias.length} secretaria links`);
    save("website-secretarias-links.json", secretarias);

    // Visit each secretaria page to find gestor info
    const gestoresInfo = [];
    for (const sec of secretarias.slice(0, 25)) {
      if (!sec.url || sec.url === "#") continue;
      try {
        await page.goto(sec.url, { timeout: 10000, waitUntil: "domcontentloaded" });
        await page.waitForTimeout(1000);

        const info = await page.evaluate(() => {
          const title = document.querySelector("h1, .entry-title, .page-title");
          const content = document.querySelector("article, .entry-content, .page-content, main");
          return {
            title: title ? title.textContent.trim() : "",
            content: content ? content.textContent.trim().substring(0, 2000) : "",
          };
        });
        gestoresInfo.push({ ...sec, ...info });
        console.log(`  ${sec.name}: ${info.title}`);
      } catch (err) {
        console.log(`  ${sec.name}: ERROR ${err.message.substring(0, 60)}`);
      }
    }
    save("website-secretarias-detail.json", gestoresInfo);
  } catch (err) {
    console.log(`  ERROR: ${err.message}`);
  }

  // ====== SUMMARY ======
  console.log("\n\n========================================");
  console.log("FINAL DISCOVERY RESULTS");
  console.log("========================================\n");

  for (const [label, r] of Object.entries(results)) {
    const status = r.ok ? `OK (${r.count} records)` : `FAIL${r.error ? ": " + r.error.substring(0, 60) : ""}`;
    console.log(`  ${r.ok ? "+" : "-"} ${label}: ${status}`);
  }

  save("correct-urls-discovery.json", results);

  await browser.close();
  console.log("\nDone.");
})();
