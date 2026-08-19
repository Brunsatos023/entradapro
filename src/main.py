from data_storage import carregar_json
from footballai_engine import FootballAIEngine
from engines.recommendation_engine import RecommendationEngine


ARQUIVO_PARTIDAS = "brasileirao_serie_a_2024.json"

TEAM_ID_MANDANTE = 127
TEAM_ID_VISITANTE = 121


def extrair_partidas(dados):
    """
    Aceita tanto o JSON completo da API-Football quanto
    uma lista direta de partidas.
    """

    if isinstance(dados, list):
        return dados

    if isinstance(dados, dict):
        partidas = dados.get("response")

        if isinstance(partidas, list):
            return partidas

    raise ValueError(
        "O arquivo não possui uma lista válida de partidas."
    )


def main():
    dados = carregar_json(ARQUIVO_PARTIDAS)
    partidas = extrair_partidas(dados)

    print(
        f"Arquivo carregado: {ARQUIVO_PARTIDAS}"
    )
    print(
        f"Total de partidas: {len(partidas)}"
    )

    analise_mandante = FootballAIEngine(
        partidas=partidas,
        team_id=TEAM_ID_MANDANTE,
        janela=5
    ).analisar()

    analise_visitante = FootballAIEngine(
        partidas=partidas,
        team_id=TEAM_ID_VISITANTE,
        janela=5
    ).analisar()

    recommendation_engine = RecommendationEngine(
        analise_mandante=analise_mandante,
        analise_visitante=analise_visitante
    )

    resultado = recommendation_engine.analisar()

    print("\n=== RECOMMENDATION ENGINE ===")
    print(resultado)


if __name__ == "__main__":
    main()