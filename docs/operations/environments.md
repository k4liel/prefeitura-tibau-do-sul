# Ambientes do sistema

## Local

- arquivo base: `backend/.env.local.example`
- arquivo opcional (Docker PostgreSQL): `backend/.env.docker.example`
- objetivo: desenvolvimento e testes locais
- banco recomendado: SQLite para inicio rapido
- alternativa profissional local: PostgreSQL via Docker em `127.0.0.1:5433`

## Homolog

- arquivo base: `backend/.env.homolog.example`
- objetivo: validacao integrada antes de producao
- banco: PostgreSQL

## Producao

- arquivo base: `backend/.env.production.example`
- objetivo: execucao oficial
- banco: PostgreSQL + Redis

## Padrao de variaveis

- `DJANGO_ENV`
- `DJANGO_DEBUG`
- `DJANGO_SECRET_KEY`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_DB_ENGINE`
- `POSTGRES_*`
- `REDIS_URL`

## Infra local com Docker

- compose: `backend/docker-compose.yml`
- PostgreSQL: `localhost:5433`
- Redis: `localhost:6379`
