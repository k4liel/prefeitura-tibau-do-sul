# Status Sprint 2 (Paginas, Filtros e Exportacao)

Data: 2026-02-19

## Entregas realizadas

- paginas web implementadas:
  - `/licitacoes/`
  - `/contratos/`
  - `/fornecedores/`
  - `/alertas/`
  - `/secretarias/`
  - `/funcionarios/`
  - `/tecnologia/`
  - `/fontes/`
- filtros e busca avancada na UI (query params):
  - busca textual
  - filtros por modalidade/empresa/cnpj/severidade
  - filtros por faixa de valor
  - ordenacao por campos principais
  - paginacao de resultados
- navegacao lateral atualizada para novos modulos
- exportacao CSV nas APIs e paginas (parametro `export=csv`)
- endpoints sensiveis de ingestao protegidos com permissao de admin
- schema OpenAPI gerado em `backend/openapi-schema.json` e endpoint `/api/schema/` validado
- melhorias de acessibilidade e responsividade base (skip link, foco visivel, labels em filtros, tabelas com overflow)
- testes atualizados para cobrir novas paginas, filtros e exportacao

## Validacao executada

- `pytest -q` -> **15 passed**
- validacao manual HTTP 200 em paginas e APIs principais
- `python manage.py check` -> sem issues
- filtros de UI validados com query params:
  - `/licitacoes/?search=internet&valor_min=0`
  - `/contratos/?search=software&ordering=-valor`
  - `/fornecedores/?search=LTDA&ordering=-valor_total`
  - `/alertas/?severidade=alta`

## Pendencias da Sprint 2

- validar responsividade e acessibilidade basica em mobile/desktop
- consolidar validacao completa em PostgreSQL
