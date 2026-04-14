# Projeto: Análise de Ações

## Objetivo
Extrair dados de ações da B3 de um banco PostgreSQL e gerar
relatórios de análise de investimentos em Markdown.

## Stack
- Python 3.11, pandas, psycopg2, SQLAlchemy
- PostgreSQL (credenciais em .env)

## Tabelas relevantes
- `empresa` — cadastro (id, sigla, nome, setor)
- `stock_guide` — dados atuais da ação
- `stock_guide_historico` — histórico diário
- `historico_resultado_empresa` — resultados trimestrais
- `estimativa_tri` / `estimativa_historica` — projeções de analistas
#- `latest_analysis` — análise textual mais recente (por ticker)
#- `noticias_empresa` — notícias

## Função principal
`src/extractor.py::extrair_dados_acao(conn, sigla)` retorna dict
de DataFrames com todos os dados da ação.

## Convenções
- Siglas sempre em minúsculo internamente; tickers em `latest_analysis`
  ficam em maiúsculo.
- Relatórios salvos em `reports/{SIGLA}_{YYYY-MM-DD}.md`.

## Como rodar
`python -m src.report BBAS3`