from __future__ import annotations

import argparse
from pathlib import Path

import basedosdados as bd


DEFAULT_QUERY = """
SELECT *
FROM `basedosdados.br_ibge_pnadc.microdados`
LIMIT 10000
"""


def run_query(query: str, output: Path, billing_project_id: str) -> None:
    df = bd.read_sql(query, billing_project_id=billing_project_id)
    output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output, index=False)
    print(f"Saved {len(df):,} rows to {output}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Crawler com basedosdados para exportar dados públicos em CSV.")
    parser.add_argument(
        "--query",
        type=str,
        default=DEFAULT_QUERY.strip(),
        help="SQL que será executada no BigQuery via basedosdados.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/raw/basedosdados_export.csv"),
        help="Arquivo CSV de saída.",
    )
    parser.add_argument(
        "--billing-project-id",
        type=str,
        required=True,
        help="Project ID do GCP para faturamento da consulta.",
    )
    args = parser.parse_args()

    run_query(args.query, args.output, args.billing_project_id)


if __name__ == "__main__":
    main()
