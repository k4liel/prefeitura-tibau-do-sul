# Sistema Tibau do Sul

Repositorio organizado para evoluir de painel estatico para sistema modular em Django.

## Estrutura principal

- `backend/`: novo backend Django modular (core do sistema).
- `docs/`: arquitetura, planos, checklists e pesquisas.
- `data/exports/`: arquivos consolidados (CSV/JSON) ja coletados.
- `legacy/painel-estatico/`: versao anterior em HTML/CSS/JS (referencia historica).
- `skills/`: playbooks de execucao e frontend.
- `scripts/`: utilitarios do painel legado.

## Iniciar backend Django

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_vereadores_2025
python manage.py runserver
```

Endpoints iniciais:

- `http://127.0.0.1:8000/health/`
- `http://127.0.0.1:8000/api/governanca/resumo/`
- `http://127.0.0.1:8000/api/legislativo/vereadores/`

## Painel legado (opcional)

Servir versao esttica antiga:

```bash
npm run legacy:serve
```

Atualizar datasets legados:

```bash
npm run legacy:data:update
```

## Testes E2E locais (Playwright)

```bash
npm install
npx playwright install chromium webkit
npm run e2e:test
```

## Documentos chave

- Stack/decisao tecnica: `docs/architecture/stack-decision.md`
- Plano de implementacao: `docs/plans/implementacao-django-modular.md`
- Checklist mestre: `docs/checklists/checklist-implementacao-django.md`
