# Dashboard de Colisões de Trânsito

Projeto final da disciplina para análise exploratória e construção de dois dashboards interativos em Python com Dash.

## Tema

Colisões de trânsito em Nova York, com foco em padrões temporais, gravidade, localização e comparação entre grupos.

## Estrutura do projeto

- `data/raw/`: arquivos brutos do dataset público, separados por ano.
- `data/processed/`: base tratada para análise.
- `scripts/`: utilitários para gerar dados de demonstração ou preparar a base.
- `src/traffic_accidents/`: código principal do pipeline e do dashboard.

## Fonte de dados

O projeto usa a base pública de colisões de trânsito de Nova York, disponibilizada pela NYC Open Data.

Os arquivos brutos são coletados em dois recortes anuais distintos para atender ao requisito de múltiplos arquivos e permitir concatenação no pipeline.

O código suporta a lógica de integração por `merge` e `concat`, além de tratamento de ausentes, padronização de campos e geração de variáveis derivadas.

## Como executar

1. Instale as dependências:

```bash
pip install -r requirements.txt
```

2. Baixe os arquivos brutos em `data/raw/` executando o coletor em `scripts/download_nyc_collisions.py`.

Se você quiser usar dados públicos do ecossistema do Base dos Dados, use também:

```bash
python scripts/crawler_basedosdados.py --billing-project-id SEU_PROJETO_GCP
```

Observação: consultas via `basedosdados` usam BigQuery e exigem credenciais + projeto de faturamento.

Para os seus arquivos PRF/Datatran já colocados em `data/raw/`, não precisa do crawler: o pipeline já lê CSV local automaticamente.

3. Execute o app:

```bash
python app.py
```

## O que o projeto entrega

- Dashboard 1: visão geral executiva.
- Dashboard 2: exploração interativa com filtros e comparações.
- Pipeline de limpeza, transformação e agregação.
- Base estruturada para relatório e apresentação.
