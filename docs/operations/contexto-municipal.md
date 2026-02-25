# Contexto municipal (IBGE + TCE-RN + TopSolutions)

Objetivo: enriquecer o painel com indicadores gerais do municipio e contexto fiscal oficial.

## Fonte oficial

- IBGE Cidades e Estados + SIDRA
- API de Dados Abertos TCE-RN
- API de Dados Abertos TopSolutions (Prefeitura)

## Atualizacao

```bash
python3 backend/manage.py sync_municipio_contexto --output-file data/exports/municipio-contexto.json
```

## Saida

- arquivo: `data/exports/municipio-contexto.json`
- arquivos complementares:
  - `data/exports/topsolutions-orcamento-2025.json`
  - `data/exports/topsolutions-emendas-2025.json`
  - `data/exports/topsolutions-operacionais-2025.json`
- consumo: dashboard (`/`) com panorama geral, contexto fiscal, emendas e status operacional (diarias, obras e PCA)
