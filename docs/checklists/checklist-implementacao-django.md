# Checklist Mestre de Implementacao (Django Modular)

Projeto: Sistema de Inteligencia Publica - Tibau do Sul

Como usar:

- siga as fases em ordem;
- marque apenas quando houver evidencia (commit, print, teste, log);
- nao avance de fase sem fechar os criterios de saida.

---

## 1) Preparacao e governanca do projeto

- [x] Confirmar stack oficial: `Python + Django + DRF + PostgreSQL + Celery + Redis + HTMX`
- [x] Definir ambientes: `local`, `homolog`, `producao`
- [x] Criar convencoes: branch, commit, PR, code review, versionamento
- [x] Organizar estrutura base: `apps/`, `config/`, `scripts/`, `docs/`, `tests/`
- [x] Configurar `.env` por ambiente (`.env.example` completo)
- [x] Configurar CI inicial: lint + testes + build

Criterio de saida:

- [x] Repositorio pronto para desenvolvimento em equipe

## 2) Fundacao tecnica (backend)

- [x] Criar projeto Django com `settings` separados por ambiente
- [x] Configurar PostgreSQL e conexao segura
- [x] Configurar DRF (pagination, filter, auth, permissions)
- [x] Configurar Celery + Redis
- [x] Configurar logging estruturado (app + jobs)
- [x] Configurar Django Admin com padrao visual e permissoes
- [x] Configurar qualidade: `ruff`/`flake8`, `black`, `isort`, `pytest`

Criterio de saida:

- [x] `python manage.py check` sem erros
- [x] `pytest` baseline passando

## 3) Arquitetura modular por dominio

Criar apps Django:

- [x] `apps.governanca` (prefeito, vice, secretarios, estrutura)
- [x] `apps.legislativo` (vereadores, mesa, comissoes)
- [x] `apps.pessoal` (servidores, folha, vinculos)
- [x] `apps.financas` (receitas, despesas, orcamento)
- [x] `apps.contratacoes` (licitacoes, contratos)
- [x] `apps.fornecedores` (empresas, concentracao)
- [x] `apps.monitoramento` (alertas, indicadores, qualidade de dados)
- [x] `apps.ingestao` (conectores, jobs, historico de sincronizacao)

Criterio de saida:

- [x] Todos os apps com `models`, `admin`, `services`, `selectors`, `api` e testes iniciais

## 4) Modelagem e migrations

- [x] Modelar entidades centrais com chaves e indices corretos
- [x] Criar tabela de rastreabilidade: fonte, endpoint, data_coleta, hash, versao
- [x] Criar tabela de execucao de jobs: inicio/fim/status/erros
- [x] Definir constraints de qualidade (unicidade, obrigatoriedade, validacoes)
- [x] Criar migrations incrementais e reversiveis

Criterio de saida:

- [x] Banco sobe do zero e popula seed sem erro

## 5) Ingestao de dados (ETL)

- [x] Conector prefeitura (TopSolutions executivo)
- [x] Conector camara (TopSolutions legislativo)
- [x] Conector camara CMS/portal (quando necessario)
- [x] Normalizacao de orgaos/secretarias
- [x] Deduplicacao de fornecedores por CNPJ/nome
- [x] Deduplicacao de servidores por matricula/chave composta
- [x] Persistir origem de cada linha de dado
- [x] Criar comando de reprocessamento (`management command`)

Criterio de saida:

- [x] Jobs rodam idempotentes (repetir nao duplica indevidamente)

## 6) API de dominio (DRF)

- [x] `GET /api/dashboard/overview`
- [x] `GET /api/governanca/resumo`
- [x] `GET /api/legislativo/vereadores`
- [x] `GET /api/financas/resumo`
- [x] `GET /api/financas/por-secretaria`
- [x] `GET /api/pessoal/funcionarios`
- [x] `GET /api/contratacoes/licitacoes`
- [x] `GET /api/contratacoes/contratos`
- [x] `GET /api/fornecedores/ranking`
- [x] `GET /api/monitoramento/alertas`
- [x] Filtros, ordenacao, paginacao e exportacao CSV

Criterio de saida:

- [x] Esquema OpenAPI atualizado e validado

## 7) Frontend web (Django templates + HTMX)

- [x] Layout base institucional e navegacao lateral
- [x] Dashboard executivo
- [x] Pagina Governanca (prefeito, vice, secretarios)
- [x] Pagina Legislativo (vereadores e estrutura)
- [x] Pagina Secretarias e Orcamento
- [x] Pagina Funcionarios (busca, filtros, export)
- [x] Pagina Financas (receita x despesa + serie)
- [x] Pagina Licitacoes
- [x] Pagina Contratos
- [x] Pagina Fornecedores
- [x] Pagina Tecnologia e afins
- [x] Pagina Alertas e Riscos
- [x] Pagina Fontes e Auditoria

Criterio de saida:

- [x] Todas as paginas com responsividade e acessibilidade basica

## 8) Seguranca, perfis e auditoria

- [x] Definir perfis: publico, analista, admin
- [x] Aplicar permissao por view e por acao sensivel
- [x] Registrar trilha de auditoria para alteracoes manuais
- [x] Proteger endpoints internos e comandos administrativos
- [x] Configurar politicas de backup e restore

Criterio de saida:

- [x] Teste de permissao e auditoria aprovado

## 9) Qualidade e observabilidade

- [x] Testes unitarios de regras criticas
- [x] Testes de integracao de API
- [x] Testes E2E das jornadas principais
- [x] Validacao numerica cruzada com documentos-base
- [x] Monitoramento de jobs (latencia, falha, retry)
- [x] Monitoramento de app (erro 5xx, tempo de resposta)

Criterio de saida:

- [x] Suite de testes minima aprovada no CI

## 10) Go-live e operacao continua

- [x] Homologacao tecnica local (ambiente de desenvolvimento)
- [x] Correcao de pendencias tecnicas identificadas
- [x] Plano de publicacao em producao documentado
- [x] Treinamento de uso (time interno) documentado
- [x] Definir calendario de sync: diario/semanal/mensal
- [x] Definir backlog trimestral de evolucao

Criterio de saida:

- [x] Sistema local validado com runbook e dono operacional definido

### Dependencias externas (fora do escopo local atual)

- [ ] Homologacao funcional com stakeholders finais
- [ ] Deploy em infraestrutura oficial de producao
- [ ] Aceite formal e treinamento presencial concluido

---

## Proximos passos imediatos (Sprint 1)

- [x] Criar migrations iniciais de todos os apps Django
- [x] Subir banco local PostgreSQL e validar `python manage.py migrate`
- [x] Implementar comando de ingestao inicial usando `legacy/painel-estatico/site/data/*.json`
- [x] Popular tabelas de governanca, legislativo, financas e contratacoes (via `load_legacy_snapshot` em SQLite)
- [x] Expor endpoints DRF com serializers e filtros reais (sem placeholders)
- [x] Configurar Django Admin por modulo com list_filter e search_fields
- [x] Criar dashboard inicial em template Django (HTMX) consumindo API interna
- [x] Registrar trilha de ingestao em `apps.ingestao.SyncRun`
- [x] Documentar procedimento de carga inicial e reprocessamento
- [x] Fechar Sprint 1 com teste automatizado de API + smoke test UI (executado em SQLite)

### Bloqueio atual

- [x] Instalar `python3-pip` e `python3-venv` no ambiente para executar `migrate`, `pytest` e carga inicial

### Status de execucao Sprint 1 (2026-02-19)

- [x] `python manage.py migrate` executado com `DJANGO_DB_ENGINE=sqlite`
- [x] `python manage.py load_legacy_snapshot` executado com sucesso
- [x] `pytest -q` executado com sucesso (11 testes passando)
- [x] Paginas e APIs validadas com dados carregados (HTTP 200)
- [x] Migrar validacao local de SQLite para PostgreSQL com credenciais corretas

### Status de execucao Sprint 2 (2026-02-19)

- [x] Paginas de Licitacoes, Contratos, Fornecedores e Alertas implementadas
- [x] Filtros e busca avancada na UI implementados
- [x] Ordenacao e paginacao nas novas paginas implementadas
- [x] Testes atualizados e passando (28/28)
- [x] Exportacao CSV nas paginas e APIs

### Status de execucao Sprint 3 (2026-02-19)

- [x] Stack Docker local configurada (`backend/docker-compose.yml`)
- [x] Validacao completa em PostgreSQL (migrate + carga + testes)
- [x] Perfis de acesso criados e aplicados (`publico`, `analista`, `admin`)
- [x] Endpoint de auditoria manual implementado (`/api/ingestao/auditoria-manual/`)
- [x] Backup/restore PostgreSQL documentado e validado
- [x] Validacao numerica cruzada executada (`validate_legacy_consistency`)
- [x] Testes E2E, unitarios e integracao passando (28/28)

### Status de validacao local final (2026-02-20)

- [x] Monitoramento de jobs implementado (`/api/monitoramento/jobs/` + `monitor_sync_health`)
- [x] Suite Python atualizada e passando (36/36)
- [x] Suite Playwright local executada (12/12)
- [x] Checklist reorganizado para escopo local e dependencias externas

### Status de execucao Sprint UI (2026-02-20)

- [x] Base visual institucional redesenhada (layout, tokens, cards, tabelas)
- [x] Paginas financeiras priorizadas com KPIs e padrao monetario (`R$`)
- [x] Filtros e tabelas refatorados para leitura analitica
- [x] Validacao regressiva backend + Playwright concluida

### Status de enriquecimento de contexto municipal (2026-02-20)

- [x] Pesquisa de fontes oficiais complementares (IBGE e TCE-RN)
- [x] Comando `sync_municipio_contexto` implementado
- [x] Panorama geral do municipio exibido no dashboard
- [x] Informacoes de habitantes, area, densidade e contexto fiscal integradas
- [x] Varredura web com Playwright (prefeitura, estado, federal) documentada
- [x] Integracao de dados complementares TopSolutions (orcamento e emendas)

### Status de clareza analitica e apresentacao (2026-02-20)

- [x] Licitacoes com leitura executiva sem duplicidade (processo x lote)
- [x] Diagnostico do Municipio com blocos (Demografia, Educacao, Saude, Fiscal, Contratacoes)
- [x] Insights automaticos em linguagem simples nas paginas financeiras
- [x] Dashboard com leitura gerencial de 1 minuto e top riscos

### Status de continuidade (2026-02-20)

- [x] Rotas dedicadas para Emendas e Orcamento Detalhado publicadas
- [x] Sincronizacao exporta arquivos dedicados de emendas/orcamento
- [x] Painel Fontes exibe score de qualidade por fonte (confiabilidade, completude, desempenho)
- [x] Diagnostico operacional de endpoints TopSolutions (diarias, obras e PCA) integrado ao dashboard
- [ ] Homologar parametros finais para endpoints que seguem em 400 no provedor externo

---

## Definition of Done (aplicar em toda entrega)

- [x] Dados rastreaveis (origem, data, endpoint, versao)
- [x] Regra de negocio coberta por teste
- [x] Endpoint/documentacao atualizados
- [ ] UI validada em mobile e desktop
- [x] UI validada em mobile e desktop
- [x] Acessibilidade basica atendida (foco, labels, contraste)
- [x] Log/observabilidade de erro implementado
- [x] Documentacao atualizada em `docs/`

## O que falta para fechamento profissional

- [x] Validacao completa em PostgreSQL (migrate + carga + testes)
- [x] Perfis de acesso completos (publico, analista, admin)
- [x] Trilha de auditoria para alteracoes manuais
- [x] Testes E2E das jornadas principais
- [x] Validacao numerica cruzada com fontes oficiais
- [x] Backup/restore documentado e testado

## O que falta para fechamento institucional (dependencias externas)

- [ ] Homologacao funcional com stakeholders finais
- [ ] Aceite formal de negocio
- [ ] Publicacao em infraestrutura oficial de producao
