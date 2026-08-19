"""
OddsEngine: busca odds reais de várias casas de apostas (via
API-Football) para uma partida, e identifica a melhor odd
disponível em cada mercado - a peça que faltava para o usuário não
precisar mais digitar a odd manualmente.

Uso típico:

    from engines.odds_engine import buscar_melhores_odds

    resultado = buscar_melhores_odds(fixture_id=1180408)

    if resultado["sucesso"]:
        melhor = resultado["mercados"]["over_1_5"]
        print(melhor["odd"], melhor["casa"])
"""

import os

import requests


BASE_URL = "https://v3.football.api-sports.io"

# As mesmas seis casas já validadas no script exploratório
# (scripts/testes_manuais/testar_odds_partida.py) - mantidas aqui
# como a lista oficial usada pelo produto.
CASAS_ENTRADAPRO = {
    8: "Bet365",
    32: "Betano",
    23: "Sportingbet",
    24: "Betway",
    3: "Betfair",
    34: "Superbet",
}

# Nomes dos mercados como a API-Football os identifica, mapeados
# para as chaves internas que o EntradaPro usa (as mesmas que o
# ValueEngine e o dashboard já esperam).
MERCADOS_SUPORTADOS = {
    "over_1_5": {
        "nome_mercado_api": "Goals Over/Under",
        "valor_aposta": "Over 1.5",
    },
    "btts": {
        "nome_mercado_api": "Both Teams Score",
        "valor_aposta": "Yes",
    },
}


def _chave_api():
    return os.getenv("API_FOOTBALL_KEY")


def _cabecalhos():
    return {"x-apisports-key": _chave_api()}


def buscar_odds_brutas(fixture_id):
    """
    Consulta a API-Football para uma partida específica.
    Retorna o JSON bruto da resposta, ou None em caso de erro.
    """
    chave = _chave_api()

    if not chave:
        return {
            "sucesso": False,
            "mensagem": "API_FOOTBALL_KEY não configurada no .env.",
        }

    try:
        resposta = requests.get(
            f"{BASE_URL}/odds",
            headers=_cabecalhos(),
            params={"fixture": fixture_id},
            timeout=20,
        )
    except requests.RequestException as erro:
        return {
            "sucesso": False,
            "mensagem": f"Erro de conexão com a API-Football: {erro}",
        }

    if resposta.status_code != 200:
        return {
            "sucesso": False,
            "mensagem": (
                f"API-Football respondeu com status "
                f"{resposta.status_code}."
            ),
        }

    dados = resposta.json()
    itens = dados.get("response", [])

    if not itens:
        return {
            "sucesso": False,
            "mensagem": "Nenhuma odd disponível para esta partida ainda.",
        }

    return {"sucesso": True, "dados": itens[0]}


def _extrair_casas_relevantes(item_odds):
    casas_encontradas = {}

    for bookmaker in item_odds.get("bookmakers", []):
        bookmaker_id = bookmaker.get("id")

        if bookmaker_id in CASAS_ENTRADAPRO:
            casas_encontradas[bookmaker_id] = bookmaker

    return casas_encontradas


def _odd_da_casa(bookmaker, nome_mercado_api, valor_aposta):
    for mercado in bookmaker.get("bets", []):
        if mercado.get("name") != nome_mercado_api:
            continue

        for valor in mercado.get("values", []):
            if valor.get("value") == valor_aposta:
                try:
                    return float(valor.get("odd"))
                except (TypeError, ValueError):
                    return None

    return None


def melhor_odd_do_mercado(casas, nome_mercado_api, valor_aposta):
    """
    Procura, entre as casas do EntradaPro, qual oferece a MAIOR odd
    (a mais vantajosa para quem aposta) para um mercado específico.

    Retorna {"odd": float, "casa": str} ou None se nenhuma casa
    tiver esse mercado disponível para a partida.
    """
    melhor = None

    for bookmaker_id, nome_casa in CASAS_ENTRADAPRO.items():
        bookmaker = casas.get(bookmaker_id)

        if not bookmaker:
            continue

        odd = _odd_da_casa(bookmaker, nome_mercado_api, valor_aposta)

        if odd is None:
            continue

        if melhor is None or odd > melhor["odd"]:
            melhor = {"odd": odd, "casa": nome_casa}

    return melhor


def buscar_melhores_odds(fixture_id):
    """
    Função principal: busca as odds reais de uma partida e devolve
    a melhor odd disponível (e em qual casa) para cada mercado que
    o EntradaPro analisa (over_1.5, BTTS).

    Retorno:
        {
            "sucesso": True,
            "mercados": {
                "over_1_5": {"odd": 1.85, "casa": "Bet365"} ou None,
                "btts": {"odd": 1.72, "casa": "Betano"} ou None,
            },
            "casas_encontradas": 4,  # quantas das 6 casas tinham odds
        }
    ou
        {"sucesso": False, "mensagem": "..."}
    """
    resultado_busca = buscar_odds_brutas(fixture_id)

    if not resultado_busca["sucesso"]:
        return resultado_busca

    casas = _extrair_casas_relevantes(resultado_busca["dados"])

    mercados = {}
    for chave_interna, config in MERCADOS_SUPORTADOS.items():
        mercados[chave_interna] = melhor_odd_do_mercado(
            casas,
            config["nome_mercado_api"],
            config["valor_aposta"],
        )

    return {
        "sucesso": True,
        "mercados": mercados,
        "casas_encontradas": len(casas),
    }
