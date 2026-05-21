# Dashboard de Colisões de Trânsito

Projeto final da disciplina para análise exploratória e construção de dois dashboards interativos em Python com Dash.

<img width="1686" height="895" alt="image" src="https://github.com/user-attachments/assets/f624bbd1-af1a-4baf-9694-09a75ef0e18c" />

## Tema

Colisões de trânsito com foco em  gravidade, localização e comparação entre grupos.

## Estrutura do projeto

- `data/raw/`: arquivos brutos do dataset público, separados por ano.
- `scripts/`: utilitários para gerar dados de demonstração ou preparar a base.
- `src/traffic_accidents/`: código principal do pipeline e do dashboard.

## Fonte de dados
A fote de bados foram coletadas do PRF:

`https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dados-abertos-da-prf`

Baixadas 3 csv:
Documento CSV de Acidentes 2026 (Agrupados por ocorrência)
Documento CSV de Acidentes 2026 (Agrupados por pessoa - Todas as causas e tipos de acidentes)
Documento CSV de Acidentes 2025 (Agrupados por pessoa - Todas as causas e tipos de acidentes)

## Como executar

1. Instale as dependências:

```bash
pip install -r requirements.txt
```
2. Tratamentos de dados e upload dos dataset:

Upar na pasta `Data/raw`

3. Execute o app:

```bash
python app.py
```

## O que o projeto entrega

- Dashboard 1: visão geral executiva.
- Dashboard 2: exploração interativa com filtros e comparações.
- Pipeline de limpeza, transformação e agregação.
