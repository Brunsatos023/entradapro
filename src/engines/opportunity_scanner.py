"""
OpportunityScanner: a Etapa B do roteiro "EntradaPro Autônomo" -
varre automaticamente todos os jogos futuros do Brasileirão,
busca as odds reais de cada um, roda as engines de análise, e
devolve uma lista já pronta das "Melhores Entradas do Dia" -
sem precisar checar partida por partida manualmente.

Combina três engines que já existiam separadas:
- FixturesEngine: quais jogos vão acontecer
- OddsEngine: qual a melhor odd real de cada um
- MatchAnalysisEngine: a análise/Value de cada confronto

Uso típico:

    from engines.opportunity_scanner import escanear_melhores_oportunidades

    resultado = escanear_melhores_oportunidades()

    if resultado["sucesso"]:
        for oportunidade in resultado["oportunidades"]:
            print(oportunidade["mandante"], "x", oportunidade["visitante"])
"""

from data_storage import carregar_json
from engines.fixtures_engine import buscar_jogos_futuros
from engines.match_analysis_engine import MatchAnalysisEngine
from engines.odds_engine import buscar_melhores_odds
from utils.nomes_times import encontrar_time_local
from prediction_history_service import registrar_previsao


JANELA_PADRAO = 5


def _construir_indices_times(partidas):
    """
    Monta dois mapas a partir do dataset local: nome -> id e uma
    lista de nomes (na ordem em que aparecem), para reaproveitar a
    mesma lógica de casamento de nomes já usada em outros lugares.
    """
    nomes_para_id = {}

    for partida in partidas:
        time_casa = partida["teams"]["home"]
        time_fora = partida["teams"]["away"]

        nomes_para_id[time_casa["name"]] = time_casa["id"]
        nomes_para_id[time_fora["name"]] = time_fora["id"]

    return nomes_para_id


def _analisar_um_jogo(jogo, partidas, nomes_para_id):
    """
    Tenta produzir uma oportunidade completa para um único jogo
    futuro. Retorna None se faltar qualquer pré-requisito (time
    fora do dataset local, sem odds disponíveis, sem value) - a
    varredura pula esse jogo e segue para o próximo, sem quebrar.
    """
    nomes_locais = list(nomes_para_id.keys())

    mandante_local = encontrar_time_local(
        jogo["mandante"], nomes_locais
    )
    visitante_local = encontrar_time_local(
        jogo["visitante"], nomes_locais
    )

    if not mandante_local or not visitante_local:
        return None

    odds = buscar_melhores_odds(jogo["fixture_id"])

    if not odds.get("sucesso"):
        return None

    mercados = odds.get("mercados", {})
    odd_over15 = mercados.get("over_1_5")
    odd_btts = mercados.get("btts")

    if not odd_over15 and not odd_btts:
        return None

    # Usa a melhor odd real encontrada; se um dos dois mercados
    # não tiver odd disponível numa das casas, usa um valor
    # neutro para não quebrar o cálculo do outro mercado.
    valor_odd_over15 = (
        odd_over15["odd"] if odd_over15 else 1.01
    )
    valor_odd_btts = (
        odd_btts["odd"] if odd_btts else 1.01
    )

    try:
        analise = MatchAnalysisEngine(
            partidas=partidas,
            id_mandante=nomes_para_id[mandante_local],
            id_visitante=nomes_para_id[visitante_local],
            odd_over15=valor_odd_over15,
            odd_btts=valor_odd_btts,
            janela=JANELA_PADRAO,
        ).analisar()
    except Exception:
        return None

    if analise.get("erro"):
        return None

    if not analise.get("recomendacao_validada"):
        return None

    resultado_value = analise["resultado_value"]

    if not resultado_value.get("value_bet"):
        return None

    oportunidade = {
        "fixture_id": jogo["fixture_id"],
        "data_iso": jogo.get("data_iso"),
        "mandante": mandante_local,
        "visitante": visitante_local,
        "melhor_mercado": analise["melhor_mercado"],
        "odd": resultado_value["odd_casa"],
        "casa_da_odd": (
            odd_over15["casa"]
            if analise["melhor_mercado"] == "Mais de 1,5 gols" and odd_over15
            else (odd_btts["casa"] if odd_btts else None)
        ),
        "probabilidade": resultado_value["probabilidade_footballai"],
        "edge": resultado_value["edge"],
        "valor_esperado": resultado_value["valor_esperado"],
        "classificacao": resultado_value["classificacao"],
    }

    # Etapa C do roteiro autônomo: toda oportunidade encontrada
    # já fica registrada sozinha na "memória" do sistema, para
    # depois ser conferida contra o resultado real. Uma falha
    # aqui não pode impedir a oportunidade de aparecer na tela.
    try:
        registrar_previsao(
            fixture_id=oportunidade["fixture_id"],
            mandante=oportunidade["mandante"],
            visitante=oportunidade["visitante"],
            mercado=oportunidade["melhor_mercado"],
            odd=oportunidade["odd"],
            probabilidade=oportunidade["probabilidade"],
            edge=oportunidade["edge"],
            data_jogo=oportunidade["data_iso"],
        )
    except Exception:
        pass

    return oportunidade
def escanear_melhores_oportunidades(
    dias_a_frente=3,
    limite=10,
    nome_arquivo_dataset="brasileirao_serie_a_2024.json",
):
    """
    Varre os jogos futuros dos próximos "dias_a_frente" dias,
    calcula o Value real (com odds de mercado de verdade) de cada
    um, e devolve os "limite" melhores, ordenados do maior edge
    para o menor.

    Retorna:
        {"sucesso": True, "oportunidades": [ {...}, ... ]}
    ou
        {"sucesso": False, "mensagem": "..."}
    """
    busca_jogos = buscar_jogos_futuros(dias_a_frente=dias_a_frente)

    if not busca_jogos.get("sucesso"):
        return busca_jogos

    jogos = busca_jogos.get("jogos", [])

    if not jogos:
        return {"sucesso": True, "oportunidades": []}

    dados = carregar_json(nome_arquivo_dataset)
    partidas = dados.get("response", [])

    nomes_para_id = _construir_indices_times(partidas)

    oportunidades = []

    for jogo in jogos:
        try:
            oportunidade = _analisar_um_jogo(
                jogo, partidas, nomes_para_id
            )
        except Exception:
            # Um jogo com problema não pode derrubar a varredura
            # inteira - pula e continua com os demais.
            oportunidade = None

        if oportunidade:
            oportunidades.append(oportunidade)

    oportunidades.sort(
        key=lambda o: o["edge"],
        reverse=True,
    )

    return {
        "sucesso": True,
        "oportunidades": oportunidades[:limite],
    }
