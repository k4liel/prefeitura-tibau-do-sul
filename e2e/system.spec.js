const { test, expect } = require("@playwright/test");

const publicPages = [
  "/",
  "/hierarquia/",
  "/remuneracoes/",
  "/governanca/",
  "/legislativo/",
  "/financas/",
  "/secretarias/",
  "/funcionarios/",
  "/licitacoes/",
  "/contratos/",
  "/fornecedores/",
  "/emendas/",
  "/orcamento-detalhado/",
  "/tecnologia/",
  "/alertas/",
];

const apiEndpoints = [
  "/health/",
  "/api/dashboard/overview/?ano=2025",
  "/api/governanca/resumo/",
  "/api/legislativo/vereadores/",
  "/api/financas/resumo/?ano=2025",
  "/api/financas/por-secretaria/?ano=2025",
  "/api/pessoal/funcionarios/",
  "/api/contratacoes/licitacoes/",
  "/api/contratacoes/contratos/",
  "/api/fornecedores/ranking/",
  "/api/monitoramento/alertas/",
  "/api/monitoramento/jobs/",
  "/api/schema/",
];

test("carrega paginas publicas principais", async ({ page }) => {
  for (const route of publicPages) {
    const response = await page.goto(route);
    expect(response && response.ok()).toBeTruthy();
  }
});

test("aplica filtros em paginas de consulta", async ({ page }) => {
  await page.goto("/licitacoes/");
  await page.fill("#licitacoes-search", "internet");
  await page.click("button:has-text('Filtrar')");
  await expect(page.locator("table tbody tr").first()).toBeVisible();

  await page.goto("/contratos/");
  await page.fill("#contratos-search", "software");
  await page.click("button:has-text('Filtrar')");
  await expect(page.locator("table tbody tr").first()).toBeVisible();
});

test("valida acessibilidade basica e responsividade", async ({ page }) => {
  await page.goto("/");
  await page.keyboard.press("Tab");
  const skipLink = page.locator("text=Pular para conteudo principal");
  await expect(skipLink).toBeVisible();
  await skipLink.click();
  await expect(page.locator("main#main-content")).toBeVisible();
});

test("pagina restrita exige autenticacao", async ({ page }) => {
  await page.goto("/fontes/");
  await expect(page).toHaveURL(/\/admin\/login/);
});

test("respostas de API principais", async ({ request }) => {
  for (const endpoint of apiEndpoints) {
    const response = await request.get(endpoint);
    expect(response.ok()).toBeTruthy();
  }
});

test("exportacao csv responde com content-type csv", async ({ request }) => {
  const csvEndpoints = [
    "/api/contratacoes/licitacoes/?export=csv",
    "/api/contratacoes/contratos/?export=csv",
    "/api/fornecedores/ranking/?export=csv",
  ];
  for (const endpoint of csvEndpoints) {
    const response = await request.get(endpoint);
    expect(response.ok()).toBeTruthy();
    expect(response.headers()["content-type"] || "").toContain("text/csv");
  }
});
