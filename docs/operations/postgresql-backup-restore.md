# Backup e restore PostgreSQL

Objetivo: garantir rotina minima de seguranca operacional para dados locais/homolog.

## Backup logico (SQL)

Exemplo com container Docker local (`tibau-postgres`):

```bash
docker exec tibau-postgres pg_dump -U postgres tibau > /tmp/tibau-backup.sql
```

## Restore em base de validacao

```bash
docker exec tibau-postgres psql -U postgres -c "DROP DATABASE IF EXISTS tibau_restore;"
docker exec tibau-postgres psql -U postgres -c "CREATE DATABASE tibau_restore;"
docker exec -i tibau-postgres psql -U postgres -d tibau_restore < /tmp/tibau-backup.sql
```

## Verificacao pos-restore

```bash
docker exec tibau-postgres psql -U postgres -d tibau_restore -c "SELECT COUNT(*) AS secretarias FROM governanca_secretaria;"
```

## Politica recomendada

- local: backup sob demanda antes de cargas/reprocessamentos
- homolog: backup diario + retencao de 14 dias
- producao: backup diario + retencao de 30 dias + teste de restore semanal
