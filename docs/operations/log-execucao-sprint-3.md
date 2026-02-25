# Log de execucao Sprint 3

Data: 2026-02-19

## Objetivo

Fechar lacunas de seguranca e operacao, validar PostgreSQL com Docker e atualizar documentacao/checklist.

## Comandos executados (resumo)

```bash
cd backend
docker compose up -d
POSTGRES_PORT=5433 python manage.py migrate
POSTGRES_PORT=5433 python manage.py create_access_profiles
POSTGRES_PORT=5433 python manage.py load_legacy_snapshot --data-dir ../legacy/painel-estatico/site/data
DJANGO_SETTINGS_MODULE=config.settings.local DJANGO_DB_ENGINE=postgresql POSTGRES_PORT=5433 pytest -q
python manage.py generateschema --format openapi-json --title "Tibau API" --api_version 1.0.0 --file openapi-schema.json
```

## Evidencias

- migracoes aplicadas no PostgreSQL sem erro
- carga legada finalizada com sucesso
- perfis `publico`, `analista`, `admin` criados/atualizados
- testes passando em SQLite e PostgreSQL (18/18)
- schema OpenAPI atualizado com endpoints de auditoria
- backup e restore validados em base `tibau_restore`
