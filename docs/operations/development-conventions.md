# Convencoes de desenvolvimento

## Branches

- feature: `feat/<contexto>-<slug>`
- fix: `fix/<contexto>-<slug>`
- chore: `chore/<contexto>-<slug>`

## Commits

- `feat:` nova funcionalidade
- `fix:` correcao
- `chore:` tarefa tecnica
- `docs:` documentacao
- `test:` testes

## Pull Requests

- titulo curto e objetivo
- descricao com contexto, alteracoes e validacao
- incluir evidencias (testes, prints, logs)
- obrigatorio CI verde

## Qualidade minima

- `ruff check .`
- `black --check .`
- `isort --check-only .`
- `pytest -q`

## Ordem de execucao recomendada

1. implementar alteracao
2. rodar format/lint
3. rodar testes
4. atualizar docs/checklist
