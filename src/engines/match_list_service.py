"""
MatchListService: monta a lista de próximos jogos já com o
EntradaPro Score, a odd real (quando disponível) e o Value —
a base da nova tela principal, no estilo Forebet/R10 Score.

Diferente do OpportunityScanner (que só retorna as oportunidades
que passaram no critério de Value), este serviço retorna TODOS os
jogos encontrados, com o que conseguir calcular de cada um -
mesmo os que não têm Value, ainda mostra o Score e o placar
provável.
"""

from data_storage import carregar_json
from engines.fixtures_engine import buscar_jogos_futuros
from engines.match_analysis_engine import MatchAnalysisEngine
from engines.odds_engine import buscar_melhores_odds
from utils.nomes_times import encontrar_time_local

import logging
logger = logging.getLogger("entradapro.dashboard")


ODD_PLACEHOLDER = 1.01  # usada so para o calculo rodar quando nao ha odd real


def _construir_indices_times(partidas):
    nomes_para_id = {}

    for partida in partidas:
        time_casa = partida["teams"]["home"]
        time_fora = partida["teams"]["away"]
        nomes_para_id[time_casa["name"]] = time_casa["id"]
        nomes_para_id[time_fora["name"]] = time_fora["id"]

    return nomes_para_id


def _analisar_um_jogo_para_lista(jogo, partidas, nomes_para_id):
    nomes_locais = list(nomes_para_id.keys())

    mandante_local = encontrar_time_local(
        jogo["mandante"], nomes_locais
    )
    visitante_local = encontrar_time_local(
        jogo["visitante"], nomes_locais
    )

    if not mandante_local or not visitante_local:
        return None

    odds = None
    try:
        odds = buscar_melhores_odds(jogo["fixture_id"])
    except Exception:
        odds = None

    odd_over15 = None
    casa_da_odd = None
    if odds and odds.get("sucesso"):
        mercado = odds.get("mercados", {}).get("over_1_5")
        if mercado:
            odd_over15 = mercado["odd"]
            casa_da_odd = mercado["casa"]

    try:
        analise = MatchAnalysisEngine(
            partidas=partidas,
            id_mandante=nomes_para_id[mandante_local],
            id_visitante=nomes_para_id[visitante_local],
            odd_over15=odd_over15 or ODD_PLACEHOLDER,
            odd_btts=ODD_PLACEHOLDER,
        ).analisar()
    except Exception:
        return None

    if analise.get("erro"):
        return None

    resultado_match = analise.get("resultado_match", {})

    score_casa = float(
        resultado_match.get("intelligence_casa", 0)
    )
    score_fora = float(
        resultado_match.get("intelligence_fora", 0)
    )
    entradapro_score = round((score_casa + score_fora) / 2)

    valor_esperado = analise.get("resultado_value", {})
    tem_odd_real = odd_over15 is not None

    return {
        "fixture_id": jogo["fixture_id"],
        "data_iso": jogo.get("data_iso"),
        "mandante": mandante_local,
        "visitante": visitante_local,
        "entradapro_score": entradapro_score,
        "odd": odd_over15 if tem_odd_real else None,
        "casa_da_odd": casa_da_odd,
        "edge": (
            valor_esperado.get("edge") if tem_odd_real else None
        ),
        "value_bet": (
            bool(valor_esperado.get("value_bet"))
            if tem_odd_real else False
        ),
    }


def construir_lista_jogos(
    dias_a_frente=7,
    nome_arquivo_dataset="brasileirao_serie_a_2024.json",
):
    """
    Retorna a lista de próximos jogos do Brasileirão com Score,
    odd (quando disponível) e Value, ordenados por data/horário.

    Jogos cujos times não estão no dataset local, ou cuja análise
    falhar por qualquer motivo, são omitidos silenciosamente - a
    lista mostra o que der para mostrar, sem quebrar.
    """
    busca_jogos = buscar_jogos_futuros(dias_a_frente=dias_a_frente)

    if not busca_jogos.get("sucesso"):
        logger.warning(
            "construir_lista_jogos: buscar_jogos_futuros falhou - %s",
            busca_jogos.get("mensagem", "sem mensagem"),
        )
        return busca_jogos

    jogos = busca_jogos.get("jogos", [])

    logger.info(
        "construir_lista_jogos: API retornou %d jogo(s) no bruto "
        "para os proximos %d dias.",
        len(jogos), dias_a_frente,
    )

    if not jogos:
        return {"sucesso": True, "jogos": []}

    dados = carregar_json(nome_arquivo_dataset)
    partidas = dados.get("response", [])
    nomes_para_id = _construir_indices_times(partidas)

    resultados = []

    for jogo in jogos:
        try:
            entrada = _analisar_um_jogo_para_lista(
                jogo, partidas, nomes_para_id
            )
        except Exception as erro:
            logger.exception(
                "construir_lista_jogos: erro ao analisar %s x %s: %s",
                jogo.get("mandante"), jogo.get("visitante"), erro,
            )
            entrada = None

        if entrada:
            resultados.append(entrada)
        else:
            logger.info(
                "construir_lista_jogos: jogo %s x %s descartado "
                "(time fora do dataset local, ou analise falhou).",
                jogo.get("mandante"), jogo.get("visitante"),
            )

    logger.info(
        "construir_lista_jogos: %d de %d jogos passaram no filtro "
        "e serao exibidos.",
        len(resultados), len(jogos),
    )

    resultados.sort(key=lambda j: j.get("data_iso") or "")

    return {"sucesso": True, "jogos": resultados}
