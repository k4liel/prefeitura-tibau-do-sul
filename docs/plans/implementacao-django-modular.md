# Plano de implementacao Django modular

Projeto: Sistema de Inteligencia Publica - Tibau do Sul

## Objetivo

Entregar uma plataforma institucional, auditavel e escalavel em Django para consolidar dados municipais de governanca, legislativo, pessoal, financas, contratacoes, fornecedores e monitoramento.

## Stack oficial

- Backend: Python 3.12, Django 5, Django REST Framework
- Banco: PostgreSQL (fallback local em SQLite)
- Filas: Celery + Redis
- Frontend: Django Templates + HTMX
- Qualidade: pytest, ruff, black, isort

## Entregue ate agora

- arquitetura modular com apps por dominio e rotas separadas
- ingestao inicial de legado via `load_legacy_snapshot`
- rastreabilidade por `DataProvenance` e controle de execucoes em `SyncRun`
- APIs com filtros, ordenacao, paginacao e exportacao CSV (`export=csv`)
- paginas web operacionais:
  - dashboard, governanca, legislativo, financas
  - licitacoes, contratos, fornecedores, alertas
  - secretarias, funcionarios, tecnologia, fontes
- endpoints sensiveis de ingestao e pagina de auditoria protegidos por perfil
- CI com lint, testes, `manage.py check` e geracao de OpenAPI
- validacao completa em PostgreSQL via Docker (migrate, carga e testes)
- perfis de acesso implementados (`publico`, `analista`, `admin`)
- trilha de auditoria manual disponibilizada por `/api/ingestao/auditoria-manual/`
- runbook de backup e restore PostgreSQL documentado

## Pendencias prioritarias

1. Qualidade funcional

- ampliar testes de regras de negocio criticas por dominio
- consolidar cobertura de testes unitarios de regras criticas por dominio

2. UX e conformidade

- revisar responsividade mobile em todas as paginas
- fechar acessibilidade basica (foco visivel, labels, contraste, teclado)

3. Operacao

- definir calendario de sincronizacao por dominio (diario/semanal/mensal)
- monitoramento de jobs (latencia, falha e retry) com alertas operacionais

## Criterios de pronto por entrega

- dado rastreavel (fonte, endpoint, hash, versao, data)
- endpoint documentado no schema OpenAPI
- testes automatizados cobrindo regra alterada
- pagina validada em desktop e mobile
- documentacao e checklist atualizados

## Proxima execucao recomendada

1. ampliar testes unitarios de regras criticas por dominio
2. fechar rodada final de acessibilidade/responsividade com evidencia
3. formalizar monitoramento de jobs e calendario de sincronizacao
