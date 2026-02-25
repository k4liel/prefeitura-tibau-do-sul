# Mapeamento inicial - Prefeitura de Tibau do Sul (Portal CR2)

Data da coleta: 2026-02-19

Fonte principal analisada:
- `https://www.portalcr2.com.br/entidade/tibau-do-sul`

## 1) Identificacao da entidade (dados objetivos)

Obtido via endpoint de inicializacao da pagina:
- `https://www.portalcr2.com.br/api/1.1/init/data?location=https%3A%2F%2Fwww.portalcr2.com.br%2Fentidade%2Ftibau-do-sul`

Campos encontrados para a prefeitura:
- Nome exibido: **Prefeitura Municipal de Tibau do Sul - RN (2025-2028)**
- Slug da entidade: `tibau-do-sul`
- Tipo de entidade: `prefeitura_municipal`
- Tipo de cliente: `portal`
- Status: `ativo`
- Cor principal: `#0064AB`
- Usa ouvidoria externa: `false`
- Logo (asset): `//4fdfdc7ecc7eac3fcdc8af2e4ed6ae07.cdn.bubble.io/f1742999789018x358961936571480000/PMTS_HOR_COLOR-1.png`

Indicadores estruturais no cadastro:
- Quantidade de categorias vinculadas: **10**
- Quantidade de modulos vinculados: **59**
- Quantidade de usuarios vinculados: **20**

> Observacao: os IDs de categorias/modulos/usuarios retornam como `__LOOKUP__` (referencias internas), sem expansao completa no endpoint publico usado nesta coleta.

## 2) Rotas/paginas publicas mapeadas para o municipio

### 2.1 Rotas testadas com retorno HTTP 200 (acessiveis)

- `https://www.portalcr2.com.br/entidade/tibau-do-sul`
- `https://www.portalcr2.com.br/centraldetransparencia/tibau-do-sul`
- `https://www.portalcr2.com.br/cadastro-fornecedores/tibau-do-sul`
- `https://www.portalcr2.com.br/consultar-manifestacao/tibau-do-sul`
- `https://www.portalcr2.com.br/plano-de-contratacoes/tibau-do-sul`
- `https://www.portalcr2.com.br/estrutura-organizacional/tibau-do-sul`
- `https://www.portalcr2.com.br/contratados-sancionados/tibau-do-sul`
- `https://www.portalcr2.com.br/aviso-licitacao/tibau-do-sul`
- `https://www.portalcr2.com.br/obras/tibau-do-sul`
- `https://www.portalcr2.com.br/ouvidoria/tibau-do-sul`
- `https://www.portalcr2.com.br/obras-paralisadas/tibau-do-sul`
- `https://www.portalcr2.com.br/balanco-relatorio-anual/tibau-do-sul`
- `https://www.portalcr2.com.br/relatorio-gestao-fiscal/tibau-do-sul`
- `https://www.portalcr2.com.br/relatorio-resumido-rreo/tibau-do-sul`
- `https://www.portalcr2.com.br/relatorios-estatisticos/tibau-do-sul`
- `https://www.portalcr2.com.br/detalhes-licitacoes/tibau-do-sul`
- `https://www.portalcr2.com.br/detalhes-contratos/tibau-do-sul`
- `https://www.portalcr2.com.br/detalhes-convenios/tibau-do-sul`
- `https://www.portalcr2.com.br/detalhes-obras/tibau-do-sul`
- `https://www.portalcr2.com.br/detalhes-servico/tibau-do-sul`
- `https://www.portalcr2.com.br/detalhes-emendas/tibau-do-sul`
- `https://www.portalcr2.com.br/detalhes-repasses/tibau-do-sul`
- `https://www.portalcr2.com.br/detalhes-parlamentar/tibau-do-sul`
- `https://www.portalcr2.com.br/detalhes-comissao/tibau-do-sul`
- `https://www.portalcr2.com.br/detalhes-materias/tibau-do-sul`
- `https://www.portalcr2.com.br/detalhes-sancionados/tibau-do-sul`
- `https://www.portalcr2.com.br/detalhes-estrutura/tibau-do-sul`
- `https://www.portalcr2.com.br/detalhes-estrutura-interna/tibau-do-sul`
- `https://www.portalcr2.com.br/detalhes-manifestacao/tibau-do-sul`
- `https://www.portalcr2.com.br/detalhes-educacao-lista/tibau-do-sul`

### 2.2 Rotas testadas com 404

- `https://www.portalcr2.com.br/contratos-de-programa/tibau-do-sul`
- `https://www.portalcr2.com.br/contratos-de-rateio/tibau-do-sul`

### 2.3 Rota que redireciona para home

- `https://www.portalcr2.com.br/dashboard-relatorios/tibau-do-sul` -> redireciona para `https://www.portalcr2.com.br/`

## 3) Hierarquia funcional inferida (menu/modulos)

Com base nos scripts dinamicos do portal, os seguintes eixos funcionais aparecem como estrutura de navegacao e catalogo de modulos:

- Transparencia/Central:
  - `centraldetransparencia`
  - `estrutura-organizacional`
  - `cadastro-fornecedores`
  - `plano-de-contratacoes`
- Controle social e ouvidoria:
  - `consultar-manifestacao`
  - `detalhes-manifestacao`
- Contratacoes e compras:
  - `aviso-licitacao`
  - `detalhes-licitacoes`
  - `detalhes-contratos`
  - `detalhes-convenios`
- Obras e servicos:
  - `obras`
  - `obras-paralisadas`
  - `detalhes-obras`
  - `detalhes-servico`
- Integridade e sancoes:
  - `contratados-sancionados`
  - `detalhes-sancionados`
- Legislativo/controle externo (presentes na estrutura tecnica do portal):
  - `detalhes-parlamentar`
  - `detalhes-comissao`
  - `detalhes-materias`
- Educacao (presenca estrutural no portal):
  - `detalhes-educacao-lista`
  - referencias tecnicas a `educacao-planejamento` e `educacao-lista-espera`
- Relatorios fiscais/contabeis:
  - `balanco-relatorio-anual`
  - `relatorio-gestao-fiscal`
  - `relatorio-resumido-rreo`
  - `relatorios-estatisticos`

> Observacao importante: varios desses caminhos existem no portal e podem estar condicionados a disponibilidade de dados por modulo/entidade em runtime.

## 4) Indicacoes de paginas de detalhe e parametros

Foram encontrados indicios de que paginas `detalhes-*` dependem de contexto/parametros de item (na navegacao interna Bubble), com chaves como:

- `entidade_id`
- `entidade_name`
- `module_id`
- `item_id`
- campos de referencia como `numeroContrato`, `numeroLicitacao`, `identificacaoEmpenho`

Isso explica por que algumas paginas carregam sem pre-dados no `init/data` quando acessadas apenas com o slug da entidade.

## 5) Endpoints tecnicos observados no codigo do portal

Endpoints encontrados no codigo cliente (nao necessariamente todos especificos de Tibau do Sul, mas parte da arquitetura da plataforma):

- `https://portalcr2.bubbleapps.io/version-test/api/1.1/wf/retorno-n8n`
- `https://wcbtpmslqjedtspgybua.supabase.co/rest/v1/logs?...`
- `https://wcbtpmslqjedtspgybua.supabase.co/rest/v1/rpc/[table]`
- webhooks n8n em dominios `*.easypanel.host`

## 6) Lacunas desta etapa (para aprofundamento)

Mesmo com varredura ampla de rotas, os endpoints publicos de bootstrap retornaram principalmente o cadastro da entidade e nao expandiram automaticamente:

- nomes completos das 10 categorias
- nomes completos dos 59 modulos
- listagens de registros detalhados (licitacoes, contratos, despesas, etc.)

Para extracao completa desses datasets, recomendacao tecnica da proxima fase:

1. Executar navegacao real no browser (Playwright) capturando chamadas XHR/fetch por modulo.
2. Registrar payloads de filtro (entidade, periodo, pagina) e endpoints efetivos.
3. Montar dicionario de dados por modulo (campos, tipos, periodicidade, cobertura historica).

## 7) Resumo executivo para inicio do projeto

- A entidade da Prefeitura de Tibau do Sul esta ativa no Portal CR2 e com estrutura robusta (10 categorias/59 modulos).
- A arquitetura usa rotas tematicas e diversas paginas de detalhe, com contexto dinamico de navegacao.
- O portal apresenta trilhas claras para transparencia fiscal, compras, obras, ouvidoria e sancoes.
- O proximo passo para consolidar "todas as informacoes" e instrumentar captura de rede em browser para desbloquear os dados que nao vem no bootstrap publico.
