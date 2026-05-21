import sys
from pathlib import Path
import os
import pandas as pd

# Make project root importable
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.traffic_accidents.data import load_raw_accidents
from src.traffic_accidents.analysis import build_kpis


def _read_preview(path: Path) -> pd.DataFrame:
    attempts = [
        {"sep": ",", "encoding": "utf-8"},
        {"sep": ";", "encoding": "utf-8"},
        {"sep": ";", "encoding": "latin-1"},
    ]
    for options in attempts:
        try:
            frame = pd.read_csv(path, **options)
        except Exception:
            continue
        if frame.shape[1] > 1:
            return frame
    raise RuntimeError("Could not parse CSV with supported combinations")


def main():
    raw_dir = Path('data/raw')
    files = sorted(raw_dir.glob('*.csv'))
    print('raw files:')
    for f in files:
        try:
            df = _read_preview(f)
            print(f.name, len(df))
        except Exception as e:
            print(f.name, 'error', e)

    print('\nloading processed dataset...')
    df = load_raw_accidents()
    print('processed rows, cols:', df.shape)
    print('columns sample:', ', '.join(df.columns[:12]))

    cols = [c for c in ['occurred_at','state','borough_group','fatalities','injured','accident_type','source_file'] if c in df.columns]
    print('\nfirst 5 processed rows (selected columns):')
    print(df[cols].head().to_dict(orient='records'))

    print('\nmin/max date:')
    if 'occurred_at' in df.columns:
        print(df['occurred_at'].min(), df['occurred_at'].max())

    print('\nKPIs:')
    print(build_kpis(df))


if __name__ == '__main__':
    main()
