from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from data_storage import carregar_json
from engines.dataset_engine import DatasetEngine


def main():
    caminho_dataset = ROOT / "data" / "raw" / "brasileirao_serie_a_2024.json"

    if not caminho_dataset.exists():
        raise FileNotFoundError(f"Dataset não encontrado: {caminho_dataset}")

    dados = carregar_json(str(caminho_dataset))
    engine = DatasetEngine(dados)
    resumo = engine.resumo()

    print("=== DATASET ENGINE ===")
    print(f"Total recebido: {resumo['total_recebido']}")
    print(f"Partidas válidas: {resumo['total_validas']}")
    print(f"Partidas encerradas: {resumo['total_encerradas']}")
    print(f"Partidas não encerradas: {resumo['total_nao_encerradas']}")
    print(f"Times indexados: {resumo['total_times_indexados']}")
    print(f"Registros descartados: {resumo['total_erros']}")

    contextos = list(engine.iterar_partidas_backtest(minimo_jogos_anteriores=5))
    print(f"Partidas aptas para backtest: {len(contextos)}")

    if contextos:
        primeiro = contextos[0]
        partida = primeiro["partida"]
        print("")
        print("Primeiro contexto apto:")
        print(f"Fixture: {partida['fixture']['id']}")
        print(
            f"Partida: {partida['teams']['home']['name']} x "
            f"{partida['teams']['away']['name']}"
        )
        print(f"Histórico do mandante: {len(primeiro['historico_mandante'])}")
        print(f"Histórico do visitante: {len(primeiro['historico_visitante'])}")


if __name__ == "__main__":
    main()