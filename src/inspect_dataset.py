from pathlib import Path

import pandas as pd


CAMINHO_DATASET = Path(
    "data/processed/brasileirao_dataset.csv"
)


def main():
    if not CAMINHO_DATASET.exists():
        print("Dataset não encontrado.")
        print(f"Caminho esperado: {CAMINHO_DATASET}")
        return

    dados = pd.read_csv(CAMINHO_DATASET)

    print("=" * 55)
    print("FOOTBALLAI — VERIFICAÇÃO DO DATASET")
    print("=" * 55)

    print(f"Quantidade de partidas: {len(dados)}")
    print(f"Quantidade de colunas: {len(dados.columns)}")

    print()
    print("Colunas encontradas:")
    for coluna in dados.columns:
        print(f"• {coluna}")

    print()
    print("Primeiras 5 partidas:")
    print(dados.head())

    print()
    print("Valores ausentes por coluna:")
    print(dados.isnull().sum())

    print()
    print("Distribuição dos resultados:")

    percentual_over15 = dados["over15"].mean() * 100
    percentual_btts = dados["btts"].mean() * 100

    print(f"Mais de 1,5 gols: {percentual_over15:.1f}%")
    print(f"Ambas marcam: {percentual_btts:.1f}%")


if __name__ == "__main__":
    main()