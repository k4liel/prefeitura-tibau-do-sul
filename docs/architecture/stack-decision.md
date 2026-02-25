# Stack recomendada para o sistema Tibau do Sul

Data: 2026-02-19

## Contexto do projeto

O sistema precisa consolidar dados publicos de multiplas fontes:

- Portal executivo (prefeitura) via API TopSolutions;
- Portal legislativo (camara), com partes em API e partes em CMS;
- Documentos e paginas institucionais;
- Dados historicos com atualizacao recorrente.

Tambem precisa entregar:

- varias paginas de negocio (dashboard, financas, contratos, licitacoes, funcionarios, vereadores, etc.);
- filtros, busca textual, tabelas grandes e graficos;
- trilha de auditoria da origem do dado;
- base preparada para escalar e manter no longo prazo.

## Opcoes avaliadas

### Opcao A - Next.js fullstack (recomendada)

Frontend + backend no mesmo projeto:

- Next.js (App Router) + TypeScript
- Tailwind CSS + shadcn/ui
- TanStack Table + Recharts
- API Routes / Server Actions para BFF
- Prisma + PostgreSQL
- Zod para validacao de contratos de dados
- Playwright para extracao onde API nao e direta

Vantagens:

- stack unica, menos friccao de manutencao;
- SSR/SSG/hibrido para performance e SEO;
- deploy simples em Vercel, Railway, Render ou VPS;
- facilita autenticacao e controle de acesso em um unico lugar.

Pontos de atencao:

- requer disciplina para separar bem camadas (UI, dominio, ingestao).

### Opcao B - React + API separada (Nest/Fastify)

Vantagens:

- separacao forte de responsabilidades;
- muito boa para times maiores.

Desvantagens:

- mais custo inicial de setup, deploy e observabilidade;
- maior complexidade para o momento atual.

### Opcao C - Site estatico evoluido (atual)

Vantagens:

- rapido para prototipo.

Desvantagens:

- manutencao cresce rapido com aumento de paginas;
- sem camada de dominio robusta;
- risco de acoplamento alto entre dados e UI.

## Decisao recomendada

Adotar **Opcao A: Next.js fullstack com PostgreSQL**.

Motivo:

- melhor equilibrio entre velocidade de entrega, qualidade profissional e escalabilidade;
- reduz risco operacional comparado a separar frontend/backend agora;
- permite migrar gradualmente o que ja foi construido no legado em `legacy/painel-estatico/site/`.

## Stack final proposta

- **App:** Next.js 15 + TypeScript
- **UI:** Tailwind + shadcn/ui
- **Graficos:** Recharts
- **Tabelas/filtros:** TanStack Table
- **Estado de dados:** TanStack Query
- **Backend app:** Route Handlers + Services (arquitetura em camadas)
- **Banco:** PostgreSQL
- **ORM:** Prisma
- **Validacao:** Zod
- **Ingestao:** Node scripts + Playwright + cron scheduler
- **Qualidade:** ESLint + Prettier + Vitest + Playwright E2E
- **Observabilidade:** Sentry + logs estruturados

## Estrutura de pastas sugerida

```text
app/
  (public)/
    dashboard/
    financas/
    secretarias/
    funcionarios/
    licitacoes/
    contratos/
    fornecedores/
    tecnologia/
    vereadores/
    documentos/
  api/
    dashboard/
    financas/
    ingestao/

src/
  modules/
    dashboard/
    financas/
    pessoas/
    contratacoes/
    legislativo/
  shared/
    ui/
    lib/
    schemas/
    utils/

prisma/
  schema.prisma
  migrations/

scripts/
  ingest/
  sync/

docs/
  arquitetura/
  plano/
  operacao/
```

## Modelo de evolucao (sem quebra)

1. manter o painel atual como baseline;
2. iniciar novo sistema em pasta `apps/web`;
3. migrar modulo por modulo;
4. substituir antigo apenas quando paridade funcional for atingida.
