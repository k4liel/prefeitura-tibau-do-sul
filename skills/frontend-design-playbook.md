# Frontend Design Playbook

Baseado na skill: `custom/skills/frontend-design/SKILL.md`

## Principios obrigatorios

1. Mobile-first
2. Simplicidade com hierarquia clara
3. Consistencia visual entre paginas
4. Acessibilidade por padrao
5. Performance primeiro

## Regras para este sistema

- usar componentes padronizados (cards, tabelas, filtros, badges, alertas);
- manter mesma linguagem visual em todas as paginas;
- evitar sobrecarga visual em telas com muito dado;
- garantir navegacao por teclado e foco visivel;
- usar contraste adequado para leitura prolongada.

## Componentes base do projeto

- `KpiCard`
- `SectionPanel`
- `DataTable`
- `FilterBar`
- `SearchBox`
- `ChartCard`
- `AlertCard`
- `SourceBadge`

## Checklist de qualidade visual

- [ ] Layout funciona no mobile (>= 360px)
- [ ] Layout funciona no desktop (>= 1366px)
- [ ] Tabelas com overflow horizontal controlado
- [ ] Tipografia legivel em todo o sistema
- [ ] Cores sem ambiguidade em status (ok, alerta, risco)
- [ ] Graficos com legenda clara e tooltip
