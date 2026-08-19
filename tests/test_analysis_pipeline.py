import os
import sys


DIRETORIO_TESTES = os.path.dirname(
    os.path.abspath(__file__)
)

DIRETORIO_PROJETO = os.path.dirname(
    DIRETORIO_TESTES
)

DIRETORIO_SRC = os.path.join(
    DIRETORIO_PROJETO,
    "src"
)

if DIRETORIO_SRC not in sys.path:
    sys.path.insert(
        0,
        DIRETORIO_SRC
    )


from analysis_pipeline import AnalysisPipeline
from data_storage import carregar_json


ARQUIVO_JSON = "brasileirao_serie_a_2024.json"

ID_FLAMENGO = 127
ID_PALMEIRAS = 121

ODD_OVER15 = 1.40
ODD_BTTS = 1.70


def carregar_partidas():
    dados = carregar_json(
        ARQUIVO_JSON
    )

    if not isinstance(dados, dict):
        raise TypeError(
            "O arquivo JSON precisa retornar "
            "um dicionário."
        )

    partidas = dados.get(
        "response"
    )

    if not isinstance(partidas, list):
        raise TypeError(
            "A chave 'response' precisa conter "
            "uma lista de partidas."
        )

    if not partidas:
        raise ValueError(
            "Nenhuma partida foi localizada "
            "no dataset."
        )

    return partidas


def validar_chaves(
    resultado
):
    chaves_obrigatorias = {
        "analise_mandante",
        "analise_visitante",
        "resultado_match",
        "resultado_prediction",
        "resultado_recommendation",
        "resultados_value_mercados"
    }

    chaves_recebidas = set(
        resultado.keys()
    )

    chaves_faltantes = (
        chaves_obrigatorias
        - chaves_recebidas
    )

    if chaves_faltantes:
        raise AssertionError(
            "Chaves ausentes no pipeline: "
            f"{sorted(chaves_faltantes)}"
        )


def validar_resultados_value(
    resultado
):
    mercados = resultado[
        "resultados_value_mercados"
    ]

    if "over_15" not in mercados:
        raise AssertionError(
            "O resultado do ValueEngine para "
            "Over 1.5 não foi retornado."
        )

    if "btts" not in mercados:
        raise AssertionError(
            "O resultado do ValueEngine para "
            "BTTS não foi retornado."
        )

    for mercado, analise in mercados.items():

        if analise.get("erro"):
            raise AssertionError(
                f"Erro no ValueEngine de "
                f"{mercado}: "
                f"{analise['erro']}"
            )

        if "probabilidade_footballai" not in analise:
            raise AssertionError(
                "O ValueEngine não retornou "
                "'probabilidade_footballai' "
                f"para {mercado}."
            )

        if "value_bet" not in analise:
            raise AssertionError(
                "O ValueEngine não retornou "
                f"'value_bet' para {mercado}."
            )


def executar_teste():
    partidas = carregar_partidas()

    resultado = AnalysisPipeline(
        partidas=partidas,
        id_mandante=ID_FLAMENGO,
        id_visitante=ID_PALMEIRAS,
        odd_over15=ODD_OVER15,
        odd_btts=ODD_BTTS,
        janela=5
    ).executar()

    if not isinstance(resultado, dict):
        raise AssertionError(
            "O AnalysisPipeline não retornou "
            "um dicionário."
        )

    if resultado.get("erro"):
        raise AssertionError(
            "O AnalysisPipeline retornou erro: "
            f"{resultado['erro']}"
        )

    validar_chaves(
        resultado
    )

    validar_resultados_value(
        resultado
    )

    analise_mandante = resultado[
        "analise_mandante"
    ]

    analise_visitante = resultado[
        "analise_visitante"
    ]

    prediction = resultado[
        "resultado_prediction"
    ]

    recommendation = resultado[
        "resultado_recommendation"
    ]

    value_over15 = resultado[
        "resultados_value_mercados"
    ]["over_15"]

    value_btts = resultado[
        "resultados_value_mercados"
    ]["btts"]

    print()
    print("=== ANALYSIS PIPELINE ===")
    print(
        f"Total de partidas: "
        f"{len(partidas)}"
    )

    print()
    print("Intelligence Score")

    print(
        f"Mandante: "
        f"{analise_mandante['intelligence_score']}"
    )

    print(
        f"Visitante: "
        f"{analise_visitante['intelligence_score']}"
    )

    print()
    print("Mercados de gols")

    print(
        f"Over 1.5: "
        f"{prediction['mais_15']}%"
    )

    print(
        f"BTTS: "
        f"{prediction['ambas_marcam']}%"
    )

    print()
    print("ValueEngine")

    print(
        f"Over 1.5 value bet: "
        f"{value_over15['value_bet']}"
    )

    print(
        f"BTTS value bet: "
        f"{value_btts['value_bet']}"
    )

    print()
    print("RecommendationEngine")

    print(
        f"Chaves retornadas: "
        f"{list(recommendation.keys())}"
    )

    print()
    print(
        "TESTE APROVADO: "
        "AnalysisPipeline executado com sucesso."
    )


if __name__ == "__main__":
    executar_teste()