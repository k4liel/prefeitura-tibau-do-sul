# Plano de refatoracao do frontend (foco institucional + financeiro)

Projeto: Sistema de Inteligencia Publica - Tibau do Sul
Data: 2026-02-20

Status: executado localmente (base visual + paginas financeiras + regressao automatizada)

## Objetivo

Elevar o frontend para padrao institucional profissional, com foco em legibilidade de dados financeiros, comparabilidade de valores e navegacao clara em desktop/mobile.

## Direcao visual (padrao inicial)

- tema institucional claro (sem dark mode como default)
- paleta base: azul petroleo, azul medio, areia clara, cinza neutro
- tipografia: familia sem serifa legivel para dados + escala tipografica consistente
- identidade de dados:
  - receita/arrecadacao em verde tecnico
  - despesa/pagamento em vermelho controlado
  - neutros para contexto e metadados

## Fases de implementacao

### Fase 1 - Fundacao de design system

1. criar `tokens` globais (cores, espacamentos, bordas, sombras, tipografia)
2. criar componentes base reutilizaveis:
   - `AppShell`, `PageHeader`, `FilterBar`, `KpiCard`, `DataTable`, `EmptyState`
3. padronizar grid responsivo (mobile-first)
4. revisar estados visuais: hover, focus-visible, disabled, loading

Entregaveis:

- refatoracao de `backend/templates/base.html`
- novo arquivo de estilos globais e utilitarios

### Fase 2 - Refatoracao das paginas financeiras (prioridade maxima)

1. redesenhar `/financas/` com seções claras:
   - resumo executivo (KPIs)
   - comparativo receita x despesa
   - tabela por secretaria com destaque de maiores valores
2. formatacao monetaria unica (`pt-BR`, `R$`, separador de milhar)
3. destacar variacao e proporcao (% do total)
4. adicionar ordenacao visual e filtros mais claros por ano/secretaria

Entregaveis:

- `backend/templates/dashboard/financas.html` refatorada
- ajustes em `secretarias.html`, `contratos.html`, `fornecedores.html`

### Fase 3 - Contratacoes e fornecedores (financeiro expandido)

1. consolidar linguagem de valor em licitacoes/contratos/fornecedores
2. criar blocos de contexto:
   - total filtrado
   - ticket medio
   - top 5 por valor
3. melhorar filtros com hierarquia visual e CTA principal
4. manter exportacao CSV sem quebrar fluxo

Entregaveis:

- refatoracao de `licitacoes.html`, `contratos.html`, `fornecedores.html`

### Fase 4 - Dashboard e consistencia global

1. elevar dashboard inicial para visao executiva real
2. padronizar cabecalhos, subtitulos e cards em todas as paginas
3. harmonizar status/alertas/severidade
4. ajustar densidade visual para leitura rapida

### Fase 5 - Qualidade UX (fechamento)

1. acessibilidade:
   - contraste AA
   - foco por teclado
   - labels e estrutura semantica
2. responsividade:
   - 360px, 768px, 1024px, 1366px
3. testes E2E Playwright atualizados com asserts visuais basicos
4. checklist final de consistencia de interface

## Regras especificas para valores financeiros

- alinhar colunas monetarias a direita
- usar numeros tabulares quando possivel
- sempre mostrar unidade (`R$`)
- evitar truncamento em celulas de valor
- destacar totalizadores e subtotais em linha fixa (quando aplicavel)
- manter cores sem exagero: semaforo apenas para sinal analitico

## Plano de execucao (sprints curtos)

- Sprint UI-1: Fase 1 + base da Fase 2
- Sprint UI-2: conclusao Fase 2 + Fase 3
- Sprint UI-3: Fase 4 + Fase 5 + hardening

## Criterio de pronto

- leitura de valores financeiros mais rapida em ate 2 cliques
- interface consistente em todas as paginas principais
- validacao Playwright desktop/mobile passando
- checklist UI/UX atualizado e aprovado
