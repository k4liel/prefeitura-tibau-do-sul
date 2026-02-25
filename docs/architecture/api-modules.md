# Mapa de APIs por modulo

## Dashboard

- `GET /api/dashboard/overview/`

## Governanca

- `GET /api/governanca/resumo/`
- `GET /api/governanca/secretarias/`

## Legislativo

- `GET /api/legislativo/vereadores/`

## Pessoal

- `GET /api/pessoal/resumo/`
- `GET /api/pessoal/funcionarios/`

## Financas

- `GET /api/financas/resumo/?ano=2025`
- `GET /api/financas/por-secretaria/?ano=2025`

## Contratacoes

- `GET /api/contratacoes/licitacoes/`
- `GET /api/contratacoes/contratos/`

## Fornecedores

- `GET /api/fornecedores/ranking/`

## Monitoramento

- `GET /api/monitoramento/alertas/`

## Ingestao

- `GET /api/ingestao/status/`

## Capacidades comuns

Nos endpoints listados em DRF:

- paginacao padrao (`count`, `next`, `previous`, `results`)
- busca textual via `?search=`
- ordenacao via `?ordering=`
- filtros por campos conforme cada endpoint
