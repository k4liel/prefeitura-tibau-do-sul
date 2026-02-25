# Status Sprint 1 (Django Modular)

Data: 2026-02-19

## Concluido

- estrutura modular dos apps Django criada;
- migrations iniciais adicionadas manualmente;
- serializers e endpoints DRF com filtros/busca/ordenacao;
- endpoint `api/dashboard/overview` adicionado;
- admin configurado por modulo (`list_display`, `list_filter`, `search_fields`);
- comando de carga legado criado: `load_legacy_snapshot`;
- dashboard inicial em template Django + HTMX + paginas (governanca, legislativo, financas);
- trilha de ingestao em `SyncRun` integrada ao comando;
- documentacao de carga inicial criada;
- testes de integracao de endpoints, comando de ingestao e paginas adicionados (pendente execucao no ambiente).
- ambiente preparado com `python3-pip` e `python3-venv`;
- migracoes executadas com `DJANGO_DB_ENGINE=sqlite`;
- carga `load_legacy_snapshot` executada com sucesso;
- suite `pytest -q` executada com sucesso (11 passed);
- validacao de paginas e APIs com dados reais (todos endpoints/paginas principais com HTTP 200).

## Pendente imediato

- ajustar e validar acesso PostgreSQL local (credenciais/usuario/banco);
- repetir `migrate`, `load_legacy_snapshot` e `pytest` em PostgreSQL;
- iniciar Sprint 2 (paginas de licitacoes, contratos, fornecedores, alertas e exportacoes CSV).

## Observacao operacional

- houve bloqueio inicial por falta de `pip/venv`, ja resolvido.
- para PostgreSQL, ainda e necessario alinhar credenciais validas no `.env`.
