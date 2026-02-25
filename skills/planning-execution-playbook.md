# Planning and Execution Playbook

Baseado nas skills:

- `superpowers/skills/writing-plans/SKILL.md`
- `superpowers/skills/executing-plans/SKILL.md`

## Modelo de planejamento adotado

Cada funcionalidade deve ter:

1. objetivo claro;
2. arquitetura resumida;
3. arquivos a criar/alterar;
4. passos pequenos e verificaveis;
5. comando de teste por etapa.

## Modelo de execucao adotado

Executar em lotes (batch):

1. escolher 2-3 tarefas;
2. implementar;
3. rodar testes;
4. revisar resultado;
5. seguir proximo lote.

## Regra de bloqueio

Parar e revisar quando houver:

- ambiguidade de requisito;
- divergencia de dado-fonte;
- falha recorrente de teste;
- impacto estrutural nao planejado.

## Padrao de verficacao minima por lote

- lint: ok
- testes unitarios: ok
- teste de integracao (se aplicavel): ok
- smoke test de pagina: ok
- documentacao atualizada: ok
