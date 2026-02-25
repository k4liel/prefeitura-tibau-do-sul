const BRL = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });
const INT = new Intl.NumberFormat("pt-BR");

const fmtMoney = (v) => BRL.format(Number(v || 0));
const fmtInt = (v) => INT.format(Number(v || 0));
const fmtPct = (v) => `${(Number(v || 0) * 100).toFixed(1)}%`;

const COLORS = [
  "#0e5ea7",
  "#1f7ec8",
  "#3a95d8",
  "#65abd8",
  "#89bde2",
  "#2b6f9e",
  "#5e8db1",
  "#3c7da6",
  "#6da0c6",
  "#8db5d2"
];

const vereadoresEleitos = [
  { nome: "Antonio Henrique", partido: "MDB" },
  { nome: "Chiquinho do Munim", partido: "PL" },
  { nome: "Eronaldo Bezerra", partido: "UNIAO" },
  { nome: "Geraldo", partido: "UNIAO" },
  { nome: "Ilana Inacio", partido: "PL" },
  { nome: "Italo Caetano", partido: "REPUBLICANOS" },
  { nome: "Lalinha Galvao", partido: "REPUBLICANOS" },
  { nome: "Leandro Barros", partido: "PL" },
  { nome: "Mano do Camarao", partido: "PL" },
  { nome: "Manoel Padi", partido: "UNIAO" },
  { nome: "Mourinha", partido: "UNIAO" }
];

function setKpis(data) {
  const kpis = [
    ["Receita arrecadada", fmtMoney(data.visaoGeral.receitaArrecadada)],
    ["Despesa paga", fmtMoney(data.visaoGeral.despesaPaga)],
    ["Licitacoes 2025", fmtInt(data.visaoGeral.licitacoesQuantidade)],
    ["Contratos 2025", fmtInt(data.visaoGeral.contratosQuantidade)],
    ["Valor total contratos", fmtMoney(data.visaoGeral.contratosValorTotal)],
    ["Valor total licitacoes", fmtMoney(data.visaoGeral.licitacoesValorTotal)],
    ["Funcionarios unicos no ano", fmtInt(data.visaoGeral.funcionariosUnicosAno)],
    ["Funcionarios no snapshot", fmtInt(data.visaoGeral.funcionariosSnapshotMes)]
  ];

  const root = document.getElementById("kpiGrid");
  root.innerHTML = kpis
    .map(
      ([label, value]) => `<article class="kpi-card"><div class="kpi-label">${label}</div><div class="kpi-value">${value}</div></article>`
    )
    .join("");
}

function renderPieChart(data) {
  const top = data.orcamentoPorSecretaria.slice(0, 8);
  const total = top.reduce((acc, item) => acc + item.orcamentoAtualizado, 0);
  let offset = 0;
  const segments = top.map((item, idx) => {
    const pct = total ? (item.orcamentoAtualizado / total) * 100 : 0;
    const color = COLORS[idx % COLORS.length];
    const seg = `${color} ${offset.toFixed(2)}% ${(offset + pct).toFixed(2)}%`;
    offset += pct;
    return { seg, color, pct, item };
  });

  const root = document.getElementById("pieChart");
  root.innerHTML = `
    <div class="pie" style="background: conic-gradient(${segments.map((s) => s.seg).join(",")});"></div>
    <ul class="legend">
      ${segments
        .map(
          (s) => `<li><span class="dot" style="background:${s.color}"></span><span>${s.item.secretaria}</span><strong>${fmtPct(
            s.pct / 100
          )}</strong></li>`
        )
        .join("")}
    </ul>
  `;
}

function renderBarChart(data) {
  const top = data.orcamentoPorSecretaria.slice(0, 10);
  const max = top.length ? top[0].orcamentoAtualizado : 1;
  const root = document.getElementById("barChart");
  root.innerHTML = top
    .map((item) => {
      const pct = max ? (item.orcamentoAtualizado / max) * 100 : 0;
      return `
        <div class="bar-row">
          <div class="bar-label" title="${item.secretaria}">${item.secretaria}</div>
          <div class="bar-track"><div class="bar-fill" style="width:${pct.toFixed(1)}%"></div></div>
          <div class="bar-val">${fmtMoney(item.orcamentoAtualizado)}</div>
        </div>
      `;
    })
    .join("");
}

function renderOrcamento(data) {
  const tb = document.querySelector("#tblOrcamento tbody");
  tb.innerHTML = data.orcamentoPorSecretaria
    .map(
      (r) => `
      <tr>
        <td>${r.secretaria}</td>
        <td>${fmtMoney(r.orcamentoAtualizado)}</td>
        <td>${fmtMoney(r.empenhado)}</td>
        <td>${fmtMoney(r.liquidado)}</td>
        <td>${fmtMoney(r.pago)}</td>
      </tr>
    `
    )
    .join("");
}

function initFuncionariosSection(data) {
  const select = document.getElementById("secSelect");
  const secList = data.funcionariosPorSecretariaSnapshot;

  select.innerHTML = secList.map((s, idx) => `<option value="${idx}">${s.secretaria}</option>`).join("");

  function renderOne(index) {
    const sec = secList[index];
    const kpiRoot = document.getElementById("funcKpis");
    kpiRoot.innerHTML = `
      <article class="mini"><div class="label">Total funcionarios</div><div class="val">${fmtInt(sec.totalFuncionarios)}</div></article>
      <article class="mini"><div class="label">Folha bruta (mes)</div><div class="val">${fmtMoney(sec.folhaBruta)}</div></article>
      <article class="mini"><div class="label">Folha liquida (mes)</div><div class="val">${fmtMoney(sec.folhaLiquida)}</div></article>
    `;

    const tb = document.querySelector("#tblFuncionarios tbody");
    tb.innerHTML = sec.funcionarios
      .map(
        (f) => `
        <tr>
          <td>${f.nome}</td>
          <td>${f.vinculo || "-"}</td>
          <td>${f.funcao || "-"}</td>
          <td>${f.cargaHoraria || "-"}</td>
          <td>${fmtMoney(f.bruto)}</td>
          <td>${fmtMoney(f.liquido)}</td>
        </tr>
      `
      )
      .join("");
  }

  select.addEventListener("change", (e) => renderOne(Number(e.target.value)));
  renderOne(0);
}

function renderLicitacoesTop(data) {
  const tb = document.querySelector("#tblLicitacoesTop tbody");
  tb.innerHTML = data.licitacoesTop
    .slice(0, 20)
    .map(
      (l) => `
      <tr>
        <td>${l.certame || "-"}</td>
        <td>${l.secretaria || "-"}</td>
        <td>${l.modalidade || "-"}</td>
        <td>${fmtMoney(l.valor)}</td>
      </tr>
    `
    )
    .join("");
}

function renderEmpresasTop(data) {
  const tb = document.querySelector("#tblEmpresasTop tbody");
  tb.innerHTML = data.contratosPorEmpresa
    .slice(0, 20)
    .map(
      (e) => `
      <tr>
        <td>${e.empresa || "-"}</td>
        <td>${fmtInt(e.quantidade)}</td>
        <td>${fmtMoney(e.valorTotal)}</td>
      </tr>
    `
    )
    .join("");
}

function renderTech(data) {
  const tb = document.querySelector("#tblTech tbody");
  tb.innerHTML = data.empresasTecnologia
    .slice(0, 80)
    .map(
      (r) => `
      <tr>
        <td>${r.tipo}</td>
        <td>${r.empresa || "-"}</td>
        <td>${r.modalidade || "-"}</td>
        <td>${fmtMoney(r.valor)}</td>
        <td>${r.objeto || "-"}</td>
      </tr>
    `
    )
    .join("");
}

function initBuscaSection(data) {
  const merged = [
    ...data.contratosDetalhes.map((x) => ({
      tipo: "contrato",
      codigo: x.contrato,
      empresa: x.empresa,
      modalidade: x.modalidade,
      valor: x.valor,
      objeto: x.objeto
    })),
    ...data.licitacoesDetalhes.map((x) => ({
      tipo: "licitacao",
      codigo: x.certame,
      empresa: x.empresa,
      modalidade: x.modalidade,
      valor: x.valor,
      objeto: x.objeto
    }))
  ];

  const searchText = document.getElementById("searchText");
  const searchType = document.getElementById("searchType");
  const count = document.getElementById("searchCount");
  const tb = document.querySelector("#tblBusca tbody");

  function render() {
    const term = (searchText.value || "").trim().toLowerCase();
    const type = searchType.value;
    const result = merged.filter((row) => {
      if (type !== "todos" && row.tipo !== type) return false;
      if (!term) return true;
      const blob = `${row.codigo || ""} ${row.empresa || ""} ${row.modalidade || ""} ${row.objeto || ""}`.toLowerCase();
      return blob.includes(term);
    });

    count.textContent = `${fmtInt(result.length)} resultados`;
    tb.innerHTML = result
      .slice(0, 200)
      .map(
        (r) => `
        <tr>
          <td>${r.tipo}</td>
          <td>${r.codigo || "-"}</td>
          <td>${r.empresa || "-"}</td>
          <td>${r.modalidade || "-"}</td>
          <td>${fmtMoney(r.valor)}</td>
          <td>${r.objeto || "-"}</td>
        </tr>
      `
      )
      .join("");
  }

  searchText.addEventListener("input", render);
  searchType.addEventListener("change", render);
  render();
}

function renderAlertas(data) {
  const a = data.alertas;
  const root = document.getElementById("alertGrid");
  root.innerHTML = `
    <article class="alert-card">
      <div class="t">Top 10 contratos</div>
      <div class="v">${fmtPct(a.top10Participacao)}</div>
      <div class="d">Participacao no valor total dos contratos</div>
    </article>
    <article class="alert-card">
      <div class="t">Concentracao fornecedores (Top 5)</div>
      <div class="v">${fmtPct(a.concentracaoTop5Fornecedores.participacao)}</div>
      <div class="d">Peso dos 5 maiores fornecedores</div>
    </article>
    <article class="alert-card">
      <div class="t">Peso de tecnologia</div>
      <div class="v">${fmtPct(a.tecnologiaNosContratos.participacao)}</div>
      <div class="d">Participacao da tecnologia no total contratado</div>
    </article>
  `;

  const tb = document.querySelector("#tblTop10Contratos tbody");
  tb.innerHTML = a.top10Contratos
    .map(
      (c) => `
      <tr>
        <td>${c.contrato || "-"}</td>
        <td>${c.empresa || "-"}</td>
        <td>${c.modalidade || "-"}</td>
        <td>${fmtMoney(c.valor)}</td>
      </tr>
    `
    )
    .join("");
}

function renderVereadores() {
  const tb = document.querySelector("#tblVereadores tbody");
  if (!tb) return;
  tb.innerHTML = vereadoresEleitos
    .map((v, idx) => `<tr><td>${idx + 1}</td><td>${v.nome}</td><td>${v.partido}</td></tr>`)
    .join("");
}

async function init() {
  const meta = document.getElementById("metaRef");
  try {
    let data = window.PROCESSED_2025;
    if (!data) {
      const response = await fetch("./data/processed_2025.json");
      data = await response.json();
    }

    meta.textContent = `Base 2025 | Snapshot funcionarios: ${String(data.referencia.snapshotFuncionariosMes).padStart(
      2,
      "0"
    )}/2025 | Gerado em: ${new Date(data.referencia.geradoEm).toLocaleString("pt-BR")}`;

    setKpis(data);
    renderPieChart(data);
    renderBarChart(data);
    renderOrcamento(data);
    initBuscaSection(data);
    initFuncionariosSection(data);
    renderAlertas(data);
    renderLicitacoesTop(data);
    renderEmpresasTop(data);
    renderTech(data);
    renderVereadores();
  } catch (err) {
    meta.textContent = "Falha ao carregar os dados do painel.";
    console.error(err);
  }
}

init();
