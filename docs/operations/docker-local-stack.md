# Stack local com Docker (PostgreSQL + Redis)

Objetivo: subir infraestrutura local padrao para desenvolvimento profissional do backend Django.

## Servicos

- PostgreSQL 16 em `127.0.0.1:5433`
- Redis 7 em `127.0.0.1:6379`

Arquivo: `backend/docker-compose.yml`

## Subir stack

```bash
cd backend
docker compose up -d
docker compose ps
```

## Validar backend em PostgreSQL

```bash
cd backend
POSTGRES_PORT=5433 python manage.py migrate
POSTGRES_PORT=5433 python manage.py create_access_profiles
POSTGRES_PORT=5433 python manage.py load_legacy_snapshot --data-dir ../legacy/painel-estatico/site/data
DJANGO_SETTINGS_MODULE=config.settings.local DJANGO_DB_ENGINE=postgresql POSTGRES_PORT=5433 pytest -q
```

## Derrubar stack

```bash
cd backend
docker compose down
```

Para limpar volumes/dados locais:

```bash
cd backend
docker compose down -v
```
