# Varredura externa de fontes (Playwright)

Data: 2026-02-20

## Metodologia

- varredura automatizada com Playwright em portais municipal, estadual e federal
- validacao de disponibilidade, links relevantes e documentacao de API
- consolidacao de fontes com potencial de integracao no projeto

## Fontes com alto valor (confirmadas)

1. Prefeitura de Tibau do Sul (site institucional)

- URL: `https://tibaudosul.rn.gov.br/`
- descoberta: links oficiais para transparencia, licitacoes, contratos, servidores, diario oficial, ouvidoria
- uso recomendado: monitorar noticias oficiais e avisos de saude/educacao/turismo

2. Portal de Transparencia TopSolutions (Prefeitura)

- URL: `https://pmtibausulrn.transparencia.topsolutionsrn.com.br/`
- descoberta: modulos de receita, despesa, contratos, diarias, servidores e link para dados abertos
- uso recomendado: base principal para ingestao executiva local

3. Dados Abertos TopSolutions (Swagger)

- URL: `https://dadosabertos.topsolutionsrn.com.br/pmtibausulrn/swagger/index.html`
- descoberta: endpoints adicionais importantes:
  - `orcamento/orcamentoasync`
  - `emendaparlamentar/emendaparlamentarasync`
  - `planocontratacaoanual/planocontratacaoanualasync`
  - `obra/obraasync`
  - `diaria/diariaasync`
  - `terceirizado/terceirizadoasync`
- status de integracao atual:
  - **integrado**: orcamento + emendas parlamentares
  - **pendente**: diaria, obra, terceirizado, PCA (retornando 400 sem parametros documentados suficientes)

4. TCE-RN (Portal + Dados Abertos)

- URLs:
  - `https://www.tce.rn.gov.br/`
  - `https://apidadosabertos.tce.rn.gov.br/swagger`
- descoberta: API com balanco orcamentario, licitacoes, contratos e empenhos/liquidacoes/pagamentos
- uso recomendado: segunda fonte oficial para validacao cruzada e auditoria externa

5. IBGE (Localidades + SIDRA + Cidades e Estados)

- URLs:
  - `https://servicodados.ibge.gov.br/api/docs`
  - `https://apisidra.ibge.gov.br`
  - `https://www.ibge.gov.br/cidades-e-estados/rn/tibau-do-sul.html`
- uso recomendado: panorama municipal (demografia, area, densidade, IDHM, PIB per capita, escolarizacao)

## Fontes com uso potencial (federal)

- `https://dados.gov.br/` (catalogo nacional)
- `https://www.gov.br/cgu/pt-br/acesso-a-informacao/dados-abertos`
- `https://www.gov.br/tesouronacional/pt-br/estatisticas-fiscais-e-planejamento`

Aplicacao no projeto:

- principalmente como referencia de padrao e cruzamento metodologico (metadados, taxonomias, series)

## Melhorias implementadas apos a varredura

- comando `sync_municipio_contexto` ampliado para agregar:
  - IBGE
  - TCE-RN
  - TopSolutions (orcamento + emendas)
- dashboard atualizado com:
  - diagnostico municipal por blocos
  - leitura de 1 minuto
  - top riscos automaticos
  - contratacoes sem duplicidade (processo x lote)

## Proximas integracoes recomendadas

1. resolver parametros dos endpoints que retornam 400 (diarias, obras, terceirizados, PCA)
2. criar pagina dedicada de emendas parlamentares (autoria, previsto, realizado, pago)
3. incluir painel de obras e convenios quando endpoint estiver validado
4. incluir indicador de qualidade de dados por fonte (completude, latencia, falhas)
