from __future__ import annotations

from pathlib import Path
from urllib.parse import urlencode

import pandas as pd


BASE_URL = "https://data.cityofnewyork.us/resource/h9gi-nx95.csv"
OUTPUT_DIR = Path("data/raw")
PAGE_SIZE = 50000


def download_year(year: int, output_path: Path) -> None:
    start = f"{year}-01-01T00:00:00"
    end = f"{year + 1}-01-01T00:00:00"
    query = f"crash_date >= '{start}' and crash_date < '{end}'"

    frames: list[pd.DataFrame] = []
    offset = 0

    while True:
        params = urlencode({"$where": query, "$limit": PAGE_SIZE, "$offset": offset})
        page_url = f"{BASE_URL}?{params}"
        page = pd.read_csv(page_url)
        if page.empty:
            break
        frames.append(page)
        if len(page) < PAGE_SIZE:
            break
        offset += PAGE_SIZE

    if not frames:
        raise RuntimeError(f"No data returned for year {year}")

    data = pd.concat(frames, ignore_index=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(output_path, index=False)
    print(f"Saved {len(data):,} rows to {output_path}")


if __name__ == "__main__":
    download_year(2023, OUTPUT_DIR / "nyc_collisions_2023.csv")
    download_year(2024, OUTPUT_DIR / "nyc_collisions_2024.csv")
