# Runbook de producao

## Dono operacional

- responsavel tecnico: Equipe de Engenharia de Dados (Prefeitura)
- contato de contingencia: equipe de Infra/DevOps municipal

## Rotina diaria

1. verificar `GET /health/`
2. verificar `GET /api/monitoramento/jobs/`
3. executar `python manage.py monitor_sync_health`
4. revisar alertas em `/alertas/`

## Rotina semanal

1. executar backup logico PostgreSQL
2. testar restore em base de validacao
3. revisar taxa de falha por fonte

## Incidente de dados

1. congelar novas cargas
2. coletar evidencias (`SyncRun`, `DataProvenance`, logs)
3. restaurar ultimo backup valido
4. reprocessar snapshot com `reprocess_snapshot`
5. validar com `validate_legacy_consistency`
