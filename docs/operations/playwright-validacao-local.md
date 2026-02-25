# Validacao local com Playwright

Objetivo: validar navegacao, filtros, APIs principais e responsividade em desktop/mobile.

## Execucao

```bash
npm install
npx playwright install chromium webkit
npm run e2e:test
```

## Cobertura atual

- paginas publicas principais
- filtros de licitacoes e contratos
- acesso restrito a `/fontes/` (redirect para login)
- endpoints principais de API
- exportacao CSV em endpoints centrais
- validacao de acessibilidade basica (skip link e foco)
- validacao em desktop (Chromium) e mobile (WebKit iPhone 13)

## Evidencia mais recente

- `npm run e2e:test` -> **12 passed**
