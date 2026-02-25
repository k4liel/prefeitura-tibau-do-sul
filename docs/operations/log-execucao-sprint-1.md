# Log de execucao - Sprint 1

Data: 2026-02-19

## Ambiente

- `python3-pip` instalado
- `python3-venv` instalado
- virtualenv criado em `backend/.venv`

## Comandos executados

```bash
export DJANGO_DB_ENGINE=sqlite
python manage.py migrate
python manage.py load_legacy_snapshot
pytest -q
```

## Resultados

- Migrations aplicadas com sucesso
- Carga legada finalizada com sucesso
- Testes automatizados: **11 passed**

## Validacao de paginas/APIs (com dados reais)

Status HTTP 200 confirmado para:

- `/`
- `/governanca/`
- `/legislativo/`
- `/financas/`
- `/api/dashboard/overview/`
- `/api/governanca/secretarias/`
- `/api/legislativo/vereadores/`
- `/api/pessoal/funcionarios/`
- `/api/contratacoes/contratos/`
- `/api/financas/por-secretaria/?ano=2025`

## Volumetria validada

- secretarias: 94
- vereadores: 11
- servidores: 1188
- contratos: 200
- licitacoes: 93
- receitas: 1
- despesas: 20

## Pendencia aberta

- Repetir o mesmo fluxo em PostgreSQL com credenciais validas no `.env`.
