"""
ShowcaseService: monta a vitrine de "Análises em Destaque" usando
partidas REAIS já aconteceram (dataset histórico do Brasileirão),
com o EntradaPro Score calculado de verdade e o resultado real
que aconteceu - prova concreta do modelo, sem depender de nenhuma
API externa (funciona sempre, inclusive para visitantes sem login).

Diferente da lista de "jogos futuros" (que depende da API-Football
e está bloqueada no plano atual), esta vitrine usa só o dataset
local já carregado - sem custo, sem chamada externa, sem risco de
ficar vazia.
"""

from data_storage import carregar_json
from engines.match_analysis_engine import MatchAnalysisEngine


TIMES_RECONHECIVEIS = {
    "Flamengo", "Palmeiras", "Corinthians", "Sao Paulo", "Santos",
    "Gremio", "Internacional", "Fluminense", "Botafogo",
    "Vasco DA Gama", "Atletico-MG", "Cruzeiro",
}

ODD_ILUSTRATIVA = 1.85  # media de mercado tipica, so para fins de exibicao


def _construir_indices_times(partidas):
    nomes_para_id = {}
    for partida in partidas:
        time_casa = partida["teams"]["home"]
        time_fora = partida["teams"]["away"]
        nomes_para_id[time_casa["name"]] = time_casa["id"]
        nomes_para_id[time_fora["name"]] = time_fora["id"]
    return nomes_para_id


def construir_vitrine_analises(
    quantidade=5,
    nome_arquivo_dataset="brasileirao_serie_a_2024.json",
):
    """
    Seleciona algumas partidas reais e reconhecíveis do histórico,
    calcula o EntradaPro Score de cada uma (usando só os jogos
    ANTERIORES a ela, como a engine já faz normalmente), e mostra
    lado a lado com o placar real que aconteceu.

    Retorna {"sucesso": True, "analises": [...]}.
    """
    dados = carregar_json(nome_arquivo_dataset)
    partidas = dados.get("response", [])

    if not partidas:
        return {"sucesso": True, "analises": []}

    nomes_para_id = _construir_indices_times(partidas)

    candidatas = [
        p for p in partidas
        if p["teams"]["home"]["name"] in TIMES_RECONHECIVEIS
        and p["teams"]["away"]["name"] in TIMES_RECONHECIVEIS
        and p.get("goals", {}).get("home") is not None
    ]

    # pega uma amostra espalhada pelo campeonato (nao so as primeiras)
    passo = max(1, len(candidatas) // (quantidade * 3))
    amostra = candidatas[::passo][:quantidade * 2]

    analises = []

    for partida in amostra:
        if len(analises) >= quantidade:
            break

        nome_casa = partida["teams"]["home"]["name"]
        nome_fora = partida["teams"]["away"]["name"]

        try:
            resultado = MatchAnalysisEngine(
                partidas=partidas,
                id_mandante=nomes_para_id[nome_casa],
                id_visitante=nomes_para_id[nome_fora],
                odd_over15=ODD_ILUSTRATIVA,
                odd_btts=ODD_ILUSTRATIVA,
            ).analisar()
        except Exception:
            continue

        if resultado.get("erro"):
            continue

        resultado_match = resultado.get("resultado_match", {})
        score_casa = float(resultado_match.get("intelligence_casa", 0))
        score_fora = float(resultado_match.get("intelligence_fora", 0))
        entradapro_score = round((score_casa + score_fora) / 2)

        gols = partida.get("goals", {})
        gc, gf = gols.get("home"), gols.get("away")

        probabilidade_over15 = resultado.get(
            "resultado_prediction", {}
        ).get("mais_15", 0)

        analises.append({
            "data": partida["fixture"]["date"][:10],
            "mandante": nome_casa,
            "visitante": nome_fora,
            "entradapro_score": entradapro_score,
            "probabilidade_over15": round(probabilidade_over15),
            "placar_real": f"{gc} x {gf}",
        })

    return {"sucesso": True, "analises": analises}
