# Carga inicial da base legada

Objetivo: carregar os JSON do painel estatico legado no banco do Django.

## Origem dos dados

- `legacy/painel-estatico/site/data/receitas2025.json`
- `legacy/painel-estatico/site/data/despesasOrgao2025.json`
- `legacy/painel-estatico/site/data/licitacoes2025.json`
- `legacy/painel-estatico/site/data/contratos2025.json`
- `legacy/painel-estatico/site/data/servidores2025.json`

## Comando de carga

```bash
python manage.py load_legacy_snapshot
```

Para preparar perfis de acesso antes da operacao:

```bash
python manage.py create_access_profiles
```

Se estiver usando SQLite local de desenvolvimento:

```bash
export DJANGO_DB_ENGINE=sqlite
python manage.py migrate
python manage.py load_legacy_snapshot
```

Opcional (diretorio customizado):

```bash
python manage.py load_legacy_snapshot --data-dir /caminho/para/json
```

## O que o comando popula

- governanca: `Secretaria`
- legislativo: `Vereador`
- pessoal: `Servidor` (snapshot dezembro/2025)
- financas: `ReceitaResumo`, `DespesaSecretaria`
- contratacoes: `Licitacao`, `Contrato`
- fornecedores: `Fornecedor`
- ingestao: `SyncRun` (trilha da execucao)

## Pos-carga (verificacao)

- `GET /api/financas/resumo?ano=2025`
- `GET /api/contratacoes/contratos`
- `GET /api/legislativo/vereadores`
- `GET /api/ingestao/status`
- `GET /api/ingestao/auditoria-manual`

## Testes recomendados apos carga

```bash
pytest -q
```

Validacao numerica cruzada com base legada:

```bash
python manage.py validate_legacy_consistency --data-dir ../legacy/painel-estatico/site/data
```

Cobertura minima esperada nesta fase:

- healthcheck
- endpoints principais de API
- comando `load_legacy_snapshot`
- paginas web iniciais (`/`, `/governanca/`, `/legislativo/`, `/financas/`)
