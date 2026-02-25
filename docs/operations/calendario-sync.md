# Calendario de sincronizacao

## Politica operacional

- contratacoes (licitacoes/contratos): diario, 06:00
- monitoramento de saude dos jobs: diario, 06:30
- pessoal (servidores): semanal, segunda 07:00
- financeiro consolidado: mensal, dia 5, 08:00
- legislativo (camara): semanal, quarta 07:30

## Comandos

- `python manage.py sync_prefeitura_topsolutions`
- `python manage.py sync_camara_topsolutions`
- `python manage.py sync_camara_portal`
- `python manage.py reprocess_snapshot --data-dir ...`
- `python manage.py monitor_sync_health`

## Janela de reprocessamento

- janela padrao: 22:00-23:30
- usar `--truncate` somente com backup concluido
