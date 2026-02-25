# Backend Django (modular)

## Requisitos

- Python 3.11+
- PostgreSQL
- Redis (para Celery)

## Setup rapido

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_vereadores_2025
python manage.py load_legacy_snapshot
python manage.py runserver
```

Stack local profissional com Docker (PostgreSQL + Redis):

```bash
docker compose up -d
cp .env.docker.example .env
POSTGRES_PORT=5433 python manage.py migrate
POSTGRES_PORT=5433 python manage.py create_access_profiles
POSTGRES_PORT=5433 python manage.py load_legacy_snapshot --data-dir ../legacy/painel-estatico/site/data
DJANGO_SETTINGS_MODULE=config.settings.local DJANGO_DB_ENGINE=postgresql POSTGRES_PORT=5433 pytest -q
POSTGRES_PORT=5433 python manage.py validate_legacy_consistency --data-dir ../legacy/painel-estatico/site/data
python manage.py sync_municipio_contexto --output-file ../data/exports/municipio-contexto.json
```

Fallback para ambiente local com SQLite:

```bash
export DJANGO_DB_ENGINE=sqlite
python manage.py migrate
python manage.py load_legacy_snapshot
python manage.py runserver
```

Rodar testes:

```bash
pytest -q
```

API base:

- `http://127.0.0.1:8000/health/`
- `http://127.0.0.1:8000/api/dashboard/overview/`
- `http://127.0.0.1:8000/api/governanca/resumo/`
- `http://127.0.0.1:8000/api/legislativo/vereadores/`
- `http://127.0.0.1:8000/api/financas/resumo/`
- `http://127.0.0.1:8000/api/ingestao/auditoria-manual/` (restrito a analista/admin)

Paginas web (templates Django):

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/governanca/`
- `http://127.0.0.1:8000/legislativo/`
- `http://127.0.0.1:8000/financas/`
- `http://127.0.0.1:8000/licitacoes/`
- `http://127.0.0.1:8000/contratos/`
- `http://127.0.0.1:8000/fornecedores/`
- `http://127.0.0.1:8000/alertas/`
- `http://127.0.0.1:8000/secretarias/`
- `http://127.0.0.1:8000/funcionarios/`
- `http://127.0.0.1:8000/tecnologia/`
- `http://127.0.0.1:8000/fontes/`

Observacao de acesso:

- `/fontes/` e endpoints de ingestao/auditoria exigem usuario com perfil analista/admin.

Obs: para filtros e busca nos endpoints DRF use query params, ex.:

- `/api/contratacoes/contratos/?search=software`
- `/api/pessoal/funcionarios/?orgao=SECRETARIA%20MUNICIPAL%20DE%20SAUDE`
- `/api/financas/por-secretaria/?ano=2025`

Para exportar CSV use `export=csv`, por exemplo:

- `/api/contratacoes/contratos/?export=csv&ordering=-valor`
- `/api/fornecedores/ranking/?export=csv&search=LTDA`

Schema OpenAPI:

- endpoint: `http://127.0.0.1:8000/api/schema/`
- artefato local: `backend/openapi-schema.json`
- gerar manualmente: `python manage.py generateschema --format openapi-json --title "Tibau API" --api_version 1.0.0 --file openapi-schema.json`

## Qualidade

Ferramentas configuradas em `requirements-dev.txt` e `pyproject.toml`:

- `ruff`
- `black`
- `isort`
- `pytest`

## Estrutura de apps

- `apps.governanca`
- `apps.legislativo`
- `apps.pessoal`
- `apps.financas`
- `apps.contratacoes`
- `apps.fornecedores`
- `apps.monitoramento`
- `apps.ingestao`
