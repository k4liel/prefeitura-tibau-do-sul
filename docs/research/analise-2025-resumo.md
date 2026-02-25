# Analise 2025 - Tibau do Sul (resumo)

## Fontes
- API de transparencia TopSolutions (`pmtibausulrn.apitransparencia.topsolutionsrn.com.br`)
- Endpoint de funcionarios por mes (12 meses de 2025)
- Endpoints de receitas, despesas por orgao, licitacoes por data e contratos por data

## Numeros principais (2025)
- Receita prevista atualizada: **R$ 144.759.762,00**
- Receita arrecadada: **R$ 123.399.081,94**
- Orcamento atualizado de despesa: **R$ 137.422.762,00**
- Despesa empenhada: **R$ 117.613.755,74**
- Despesa paga: **R$ 115.802.204,03**
- Licitacoes no periodo: **200** (valor total aproximado **R$ 89.174.396,68**)
- Contratos no periodo: **226** (valor total **R$ 75.910.291,21**)

## Estrutura por secretaria
- Base de orcamento por secretaria: 20 unidades orcamentarias (despesa por orgao)
- Base de funcionarios: quadro por orgao de lotacao no snapshot de dezembro/2025
- Base anual de folha: soma mensal (jan-dez/2025) por orgao

## Empresas e tecnologia
- Ranking de empresas por valor contratual incluido no painel
- Deteccao de empresas/objetos de tecnologia por palavras-chave (software, sistema, tecnologia, telecom, internet, dados, etc.)
- Ocorrencias detectadas: **42 registros** (entre contratos e licitacoes)

## Arquivos do painel legado
- `legacy/painel-estatico/site/index.html` (pagina principal)
- `legacy/painel-estatico/site/styles.css` (estilo)
- `legacy/painel-estatico/site/app.js` (renderizacao e interacao)
- `legacy/painel-estatico/site/data/processed_2025.json` (base analitica)
- `legacy/painel-estatico/site/data/processed_2025.js` (base embutida para abrir sem servidor)
