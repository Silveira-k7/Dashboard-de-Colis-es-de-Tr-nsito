from pathlib import Path

from src.traffic_accidents.data import generate_demo_data


if __name__ == "__main__":
    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)
    demo = generate_demo_data(rows=20000)
    first_half = demo.iloc[:10000].copy()
    second_half = demo.iloc[10000:].copy()
    first_path = output_dir / "acidentes_demo_1.csv"
    second_path = output_dir / "acidentes_demo_2.csv"
    first_half.to_csv(first_path, index=False)
    second_half.to_csv(second_path, index=False)
    print(f"Arquivos gerados em {first_path} e {second_path}")
