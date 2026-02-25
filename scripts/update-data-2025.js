const fs = require("fs");
const https = require("https");
const path = require("path");

const API = "https://pmtibausulrn.apitransparencia.topsolutionsrn.com.br";
const OUT = path.join(__dirname, "..", "legacy", "painel-estatico", "site", "data");

function get(url) {
  return new Promise((resolve, reject) => {
    https
      .get(url, (res) => {
        let body = "";
        res.on("data", (c) => (body += c));
        res.on("end", () => resolve({ status: res.statusCode || 0, body }));
      })
      .on("error", reject);
  });
}

async function fetchJson(endpoint) {
  const { status, body } = await get(`${API}${endpoint}`);
  if (status >= 400) {
    return { ok: false, error: `HTTP ${status}`, endpoint, body: body.slice(0, 300) };
  }
  return JSON.parse(body);
}

function sum(arr, key) {
  return arr.reduce((acc, row) => acc + (Number(row[key]) || 0), 0);
}

function writeJson(fileName, value) {
  fs.writeFileSync(path.join(OUT, fileName), JSON.stringify(value, null, 2));
}

async function main() {
  if (!fs.existsSync(OUT)) fs.mkdirSync(OUT, { recursive: true });

  const receitas = await fetchJson(
    "/receitaprevistaarrecadada/receitaprevistaarrecadadaasync?classificacaoPor=receita&numExercicio=2025&mesIni=1&mesFim=12"
  );
  const despesas = await fetchJson(
    "/despesa/despesaporclassificacaoasync?strClassificarPor=orgao&dtIni=01/01/2025&dtFim=31/12/2025"
  );
  const contratos = await fetchJson("/contrato/contratopordataasync?dtInicio=2025-01-01&dtFim=2025-12-31");
  const licitacoes = await fetchJson("/licitacao/licitacaopordataasync?dtInicio=2025-01-01&dtFim=2025-12-31");

  const servidores2025 = [];
  for (let mes = 1; mes <= 12; mes += 1) {
    const payload = await fetchJson(`/Servidor/ServidorPorMesAnoAsync?numMes=${mes}&numAno=2025`);
    servidores2025.push({ mes, payload });
  }

  writeJson("receitas2025.json", receitas);
  writeJson("despesasOrgao2025.json", despesas);
  writeJson("contratos2025.json", contratos);
  writeJson("licitacoes2025.json", licitacoes);
  writeJson("servidores2025.json", servidores2025);

  const recData = receitas.data || [];
  const despData = (despesas.data || []).filter((r) => Number(r.exercicio) === 2025);
  const ctrData = contratos.data || [];
  const licData = licitacoes.data || [];

  const monthMap = {};
  for (const m of servidores2025) monthMap[String(m.mes).padStart(2, "0")] = m.payload.data || [];
  const snap = monthMap["12"] || [];

  const funcionariosPorSec = {};
  for (const f of snap) {
    const sec = f.orgao || "SEM ORGAO";
    if (!funcionariosPorSec[sec]) {
      funcionariosPorSec[sec] = { secretaria: sec, totalFuncionarios: 0, folhaBruta: 0, folhaLiquida: 0, funcionarios: [] };
    }
    funcionariosPorSec[sec].totalFuncionarios += 1;
    funcionariosPorSec[sec].folhaBruta += Number(f.vlrRemuneracaoBruta) || 0;
    funcionariosPorSec[sec].folhaLiquida += Number(f.vlrRemuAposDescObrig) || 0;
    funcionariosPorSec[sec].funcionarios.push({
      nome: f.nome,
      vinculo: f.vinculo,
      funcao: f.funcao || f.cargoFuncao || f.cargo,
      cargaHoraria: f.cargaHoraria,
      bruto: Number(f.vlrRemuneracaoBruta) || 0,
      liquido: Number(f.vlrRemuAposDescObrig) || 0
    });
  }

  const contratosPorEmpresa = {};
  for (const c of ctrData) {
    const e = (c.txtNomeRazaoContratada || "Nao informado").trim();
    if (!contratosPorEmpresa[e]) contratosPorEmpresa[e] = { empresa: e, quantidade: 0, valorTotal: 0 };
    contratosPorEmpresa[e].quantidade += 1;
    contratosPorEmpresa[e].valorTotal += Number(c.vlrContrato) || 0;
  }

  const techRegex = /(tecnolog|software|sistema|informat|comput|dados|internet|telecom|digital|rede|servidor)/i;
  const empresasTecnologia = ctrData
    .filter((c) => techRegex.test(`${c.txtNomeRazaoContratada || ""} ${c.txtObjeto || ""}`))
    .map((c) => ({
      tipo: "contrato",
      empresa: c.txtNomeRazaoContratada,
      modalidade: c.txtModalidade,
      valor: Number(c.vlrContrato) || 0,
      objeto: c.txtObjeto,
      contrato: c.numContrato
    }));

  const contratosDetalhes = ctrData.map((c) => ({
    contrato: c.numContrato,
    empresa: c.txtNomeRazaoContratada,
    modalidade: c.txtModalidade,
    valor: Number(c.vlrContrato) || 0,
    objeto: c.txtObjeto
  }));
  const licitacoesDetalhes = licData.map((l) => ({
    certame: l.numCertame,
    empresa: l.txtNomeRazaoSocial,
    modalidade: l.txtModalidadeLicit,
    valor: Number(l.vlrTotal) || 0,
    objeto: l.txtObjeto,
    unidade: l.txtUnidadeOrcamentaria
  }));

  const contratosTop = contratosDetalhes.slice().sort((a, b) => b.valor - a.valor).slice(0, 30);
  const totalContratos = sum(ctrData, "vlrContrato");
  const top10 = contratosTop.slice(0, 10);
  const top10Valor = top10.reduce((acc, c) => acc + c.valor, 0);

  const fornecedores = Object.values(contratosPorEmpresa).sort((a, b) => b.valorTotal - a.valorTotal);
  const top5 = fornecedores.slice(0, 5);
  const top5Valor = top5.reduce((acc, c) => acc + c.valorTotal, 0);
  const valorTech = empresasTecnologia.reduce((acc, c) => acc + c.valor, 0);

  const processed = {
    referencia: { ano: 2025, snapshotFuncionariosMes: 12, geradoEm: new Date().toISOString() },
    visaoGeral: {
      receitaPrevista: sum(recData, "vlrPrevisaoAtualizado"),
      receitaArrecadada: sum(recData, "vlrArrecadacao"),
      despesaOrcamento: sum(despData, "vlrOrcadoAtualizado"),
      despesaEmpenhada: sum(despData, "vlrEmpenhado"),
      despesaLiquidada: sum(despData, "vlrLiquidado"),
      despesaPaga: sum(despData, "vlrPago"),
      contratosQuantidade: ctrData.length,
      contratosValorTotal: totalContratos,
      licitacoesQuantidade: licData.length,
      licitacoesValorTotal: sum(licData, "vlrTotal"),
      funcionariosUnicosAno: new Set(Object.values(monthMap).flat().map((f) => f.numMatricula || f.nome)).size,
      funcionariosSnapshotMes: snap.length
    },
    orcamentoPorSecretaria: despData
      .map((d) => ({
        orgaoCodigo: `${d.codOrgao}.${d.codUnidade}`,
        secretaria: d.txtDescricaoUnidade,
        orcamentoAtualizado: Number(d.vlrOrcadoAtualizado) || 0,
        empenhado: Number(d.vlrEmpenhado) || 0,
        liquidado: Number(d.vlrLiquidado) || 0,
        pago: Number(d.vlrPago) || 0
      }))
      .sort((a, b) => b.orcamentoAtualizado - a.orcamentoAtualizado),
    funcionariosPorSecretariaSnapshot: Object.values(funcionariosPorSec).sort((a, b) => b.totalFuncionarios - a.totalFuncionarios),
    licitacoesTop: licData
      .map((l) => ({
        certame: l.numCertame,
        secretaria: l.txtUnidadeOrcamentaria,
        modalidade: l.txtModalidadeLicit,
        valor: Number(l.vlrTotal) || 0,
        objeto: l.txtObjeto,
        situacao: l.txtSituacao
      }))
      .sort((a, b) => b.valor - a.valor)
      .slice(0, 30),
    licitacoesDetalhes,
    contratosPorEmpresa: fornecedores,
    contratosTop,
    contratosDetalhes,
    empresasTecnologia: empresasTecnologia.sort((a, b) => b.valor - a.valor),
    alertas: {
      top10Contratos: top10,
      top10ContratosValor: top10Valor,
      top10Participacao: totalContratos ? top10Valor / totalContratos : 0,
      concentracaoTop5Fornecedores: {
        fornecedores: top5,
        valor: top5Valor,
        participacao: totalContratos ? top5Valor / totalContratos : 0
      },
      tecnologiaNosContratos: {
        valorTecnologia: valorTech,
        totalContratos: totalContratos,
        participacao: totalContratos ? valorTech / totalContratos : 0,
        registrosTecnologiaContratos: empresasTecnologia.length
      }
    }
  };

  writeJson("processed_2025.json", processed);
  fs.writeFileSync(path.join(OUT, "processed_2025.js"), `window.PROCESSED_2025 = ${JSON.stringify(processed)};\n`);

  console.log("Dados atualizados em legacy/painel-estatico/site/data/");
}

main().catch((err) => {
  console.error("Falha ao atualizar dados:", err.message);
  process.exit(1);
});
