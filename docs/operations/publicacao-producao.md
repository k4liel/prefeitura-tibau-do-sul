# Publicacao em producao

## Checklist de release

- [x] `manage.py check --deploy` sem bloqueios criticos
- [x] testes automatizados aprovados
- [x] schema OpenAPI atualizado
- [x] backup antes do deploy
- [x] plano de rollback documentado

## Passo a passo

1. aplicar migracoes em producao
2. executar carga/sincronizacao inicial
3. validar endpoints criticos (`/health/`, `/api/dashboard/overview/`)
4. validar pagina inicial e modulo de alertas
5. monitorar `monitor_sync_health` nas primeiras 24h

## Rollback

1. restaurar backup logico mais recente
2. reverter release de aplicacao
3. revalidar saude e consistencia numerica
