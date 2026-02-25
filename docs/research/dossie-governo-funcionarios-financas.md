# Dossie institucional e financeiro - Prefeitura de Tibau do Sul/RN

Data de consolidacao: 2026-02-19

## 1) Quem e quem (governo municipal)

### Prefeito
- **Nome:** Valdenicio Jose da Costa
- **Funcao na folha:** Prefeito(a)
- **Orgao:** Gabinete do Prefeito
- **Mes de referencia da folha usada:** 2026-01

### Vice-prefeito
- **Nome:** Manoel Messias Marinho
- **Funcao na folha:** Vice Prefeito(a)
- **Orgao:** Gabinete do Prefeito
- **Mes de referencia da folha usada:** 2026-01

### Secretarios municipais identificados (ativos na folha 2026-01)

1. SEC. MUN. DE SAUDE - Jucileide Barros de Albuquerque Costa
2. SEC. MUN. DE TRIBUTACAO - Walter Jose da Costa
3. SEC. MUN. DE EDUCACAO - Charles Clayton Galvao Soares
4. SEC. MUN. DE CULTURA E ECONOMIA CRIATIVA - Natalia Keller Magalhaes Gomes
5. SEC. MUN. AGRIC/PEC/AQUICULRURA - Jose Agnaldo Silvino Frades
6. SEC. MUN. MOBILIDADE URBANA E TRANSITO - Rhanyer Riccelle Costa da Silva
7. SEC. MUN. PLANEJAMENTO E FINANCAS - Gilkissa Jacqueline Candido da Silva Costa
8. SEC. MUN. TRANSPORTE E SERVICOS URBANOS - Thomas Aurelio Albuquerque Dionisio
9. SEC. MUN. DE TURISMO - Lavoisyer Emerson Macena
10. SEC. MUN. DESENVOLVIMENTO ECONOMICO - Nuno Frederico Rocha Martins
11. SEC. MUN. ADMINISTRACAO - Hully Tainara Silva de Albuquerque
12. SEC. MUN. TRAB/HABIT/A.SOCIAL - Luciana de Albuquerque Borges
13. SEC. MUN. MEIO AMBIENTE E URBANISMO - Katarine Maria Freire Diesel
14. SEC. MUN. DE ESPORTE E LAZER - Gilson Barboza do Nascimento
15. SEC. MUN. DE INFRAESTRUTURA - Adaebson Santos da Silva
16. SECRETARIA MUNICIPAL DE PESCA - Geraldo Jose da Silva

Arquivo detalhado desta secao:
- `data/exports/secretarios-ativos-folha-2026-01.csv`

## 2) Todos os funcionarios (quadro funcional)

Base usada: folha mensal do portal de transparencia (mes 2026-01).

Indicadores consolidados:
- **Total de registros de servidores/colaboradores:** 966
- **Total bruto (soma):** R$ 4.007.983,96
- **Total liquido apos descontos obrigatorios (soma):** R$ 3.504.671,53
- **Descontos obrigatorios (soma):** R$ 1.279.450,95

Composicao por vinculo:
- Comissionado: 147
- Efetivo: 359
- Contratado: 444
- Plantonista: 12
- Eletivo: 3
- Pensionista: 1

Arquivo completo com todos os funcionarios (nome, vinculo, orgao, funcao, matricula, remuneracao):
- `data/exports/funcionarios-folha-2026-01.csv`

## 3) Financas da cidade (visao executiva)

## 3.1 Receitas municipais (2025)
- **Previsao atualizada total:** R$ 144.759.762,00
- **Arrecadacao total:** R$ 123.399.081,94

Categorias retornadas no endpoint:
- Receitas Correntes
- Receitas de Capital

## 3.2 Despesas municipais (2025, classificacao por orgao)
- **Orcamento atualizado total:** R$ 137.422.762,00
- **Empenhado total:** R$ 117.613.755,74
- **Liquidado total:** R$ 117.208.027,87
- **Pago total:** R$ 115.802.204,03

## 3.3 Contratos
- **Registros totais no dataset consultado:** 1.085
- **Contratos publicados em 2025:** 226
- **Valor total dos contratos publicados em 2025:** R$ 75.910.291,21

## 4) Fontes e rastreabilidade

Fontes principais utilizadas nesta consolidacao:
- Site institucional oficial: `https://tibaudosul.rn.gov.br/`
- Portal da Transparencia CR2: `https://www.portalcr2.com.br/entidade/tibau-do-sul`
- API do portal de transparencia TopSolutions (tenant de Tibau do Sul)

Endpoints utilizados (amostra):
- `https://pmtibausulrn.apitransparencia.topsolutionsrn.com.br/Servidor/ServidorPorMesAnoAsync?numMes=1&numAno=2026`
- `https://pmtibausulrn.apitransparencia.topsolutionsrn.com.br/receitaprevistaarrecadada/receitaprevistaarrecadadaasync?classificacaoPor=receita&numExercicio=2025&mesIni=1&mesFim=12`
- `https://pmtibausulrn.apitransparencia.topsolutionsrn.com.br/despesa/despesaporclassificacaoasync?strClassificarPor=orgao&dtIni=01/01/2025&dtFim=31/12/2025`
- `https://pmtibausulrn.apitransparencia.topsolutionsrn.com.br/contrato/contratoasync?dtInicio=2025-01-01&dtFim=2025-12-31`

Arquivo tecnico de apoio (resumo numerico em JSON):
- `data/exports/resumo-dados.json`

## 5) Observacoes de governanca de dados

- Os nomes de prefeito, vice e secretarios acima foram consolidados a partir da folha de pagamento (referencia 2026-01) e do site institucional.
- A lista de funcionarios corresponde ao recorte de folha consultado (mensal), podendo variar em meses seguintes (admissoes, vacancias, substituicoes, etc.).
- Para acompanhamento continuo, o ideal e automatizar coleta mensal dos endpoints de servidores, receitas, despesas, contratos e licitacoes.
