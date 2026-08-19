import os
import requests
from dotenv import load_dotenv


load_dotenv()


API_KEY = os.getenv("API_FOOTBALL_KEY")

BASE_URL = "https://v3.football.api-sports.io"

URL_ODDS = f"{BASE_URL}/odds"
URL_FIXTURE = f"{BASE_URL}/fixtures"


BOOKMAKERS_ENTRADAPRO = {
    8: "Bet365",
    32: "Betano",
    23: "Sportingbet",
    24: "Betway",
    3: "Betfair",
    34: "Superbet",
}


def headers():
    return {
        "x-apisports-key": API_KEY
    }


def consultar_odds():
    """
    Consulta diretamente o endpoint /odds.
    Não dependemos mais de procurar uma partida
    antecipadamente pelo /fixtures.
    """

    resposta = requests.get(
        URL_ODDS,
        headers=headers(),
        params={
            "page": 1
        },
        timeout=30
    )

    resposta.raise_for_status()

    return resposta.json()


def buscar_dados_partida(fixture_id):
    """
    Depois que /odds nos entregar um fixture ID,
    consultamos /fixtures apenas para descobrir
    os nomes dos times, liga e horário.
    """

    resposta = requests.get(
        URL_FIXTURE,
        headers=headers(),
        params={
            "id": fixture_id,
            "timezone": "America/Sao_Paulo"
        },
        timeout=30
    )

    resposta.raise_for_status()

    dados = resposta.json()

    partidas = dados.get(
        "response",
        []
    )

    if not partidas:
        return None

    return partidas[0]


def extrair_casas_entradapro(item_odds):
    """
    Mantém somente as seis casas escolhidas
    para o EntradaPro.
    """

    encontradas = {}

    bookmakers = item_odds.get(
        "bookmakers",
        []
    )

    for bookmaker in bookmakers:

        bookmaker_id = bookmaker.get("id")

        if bookmaker_id not in BOOKMAKERS_ENTRADAPRO:
            continue

        encontradas[bookmaker_id] = bookmaker

    return encontradas


def escolher_partida(response_odds):
    """
    Procura uma partida que tenha pelo menos
    uma das casas selecionadas pelo EntradaPro.
    """

    for item in response_odds:

        casas = extrair_casas_entradapro(
            item
        )

        if casas:
            return item, casas

    return None, {}


def mostrar_partida(item_odds):
    fixture = item_odds.get(
        "fixture",
        {}
    )

    fixture_id = fixture.get("id")

    print()
    print("=" * 70)
    print("PARTIDA ENCONTRADA")
    print("=" * 70)

    print(
        "Fixture ID:",
        fixture_id
    )

    try:
        partida = buscar_dados_partida(
            fixture_id
        )

    except requests.RequestException as erro:

        print(
            "Não foi possível consultar "
            "os dados da partida:",
            erro
        )

        return

    if not partida:
        print(
            "Fixture encontrado nas odds, "
            "mas sem detalhes em /fixtures."
        )

        return

    times = partida.get(
        "teams",
        {}
    )

    liga = partida.get(
        "league",
        {}
    )

    fixture_dados = partida.get(
        "fixture",
        {}
    )

    home = (
        times.get(
            "home",
            {}
        ).get(
            "name"
        )
    )

    away = (
        times.get(
            "away",
            {}
        ).get(
            "name"
        )
    )

    print(
        f"Jogo: {home} x {away}"
    )

    print(
        "Liga:",
        liga.get("name")
    )

    print(
        "País:",
        liga.get("country")
    )

    print(
        "Data:",
        fixture_dados.get("date")
    )


def mostrar_odds(casas):
    print()
    print("=" * 70)
    print("ODDS DAS CASAS DO ENTRADAPRO")
    print("=" * 70)

    for bookmaker_id, nome in BOOKMAKERS_ENTRADAPRO.items():

        bookmaker = casas.get(
            bookmaker_id
        )

        if not bookmaker:
            print()
            print(
                f"{nome}: SEM ODDS "
                "NESTA PARTIDA"
            )

            continue

        print()
        print("-" * 70)

        print(nome)

        print("-" * 70)

        mercados = bookmaker.get(
            "bets",
            []
        )

        for mercado in mercados:

            mercado_id = mercado.get(
                "id"
            )

            mercado_nome = mercado.get(
                "name"
            )

            print()
            print(
                f"[{mercado_id}] "
                f"{mercado_nome}"
            )

            valores = mercado.get(
                "values",
                []
            )

            for valor in valores:

                nome_aposta = valor.get(
                    "value"
                )

                odd = valor.get(
                    "odd"
                )

                print(
                    f"    {nome_aposta}: "
                    f"{odd}"
                )


def mostrar_resumo(casas):
    print()
    print("=" * 70)
    print("CASAS ENCONTRADAS")
    print("=" * 70)

    total = 0

    for bookmaker_id, nome in BOOKMAKERS_ENTRADAPRO.items():

        if bookmaker_id in casas:
            status = "OK"
            total += 1

        else:
            status = "SEM ODDS"

        print(
            f"{nome}: {status}"
        )

    print()
    print(
        f"Total: {total}/"
        f"{len(BOOKMAKERS_ENTRADAPRO)}"
    )


def main():

    if not API_KEY:

        print(
            "ERRO: API_FOOTBALL_KEY "
            "não encontrada no .env."
        )

        return

    print()
    print(
        "Consultando odds disponíveis "
        "na API-Football..."
    )

    try:

        dados = consultar_odds()

    except requests.RequestException as erro:

        print()
        print(
            "Erro na API:",
            erro
        )

        return

    erros = dados.get(
        "errors"
    )

    if erros:

        print()
        print(
            "ERROS DA API:"
        )

        print(
            erros
        )

        return

    response_odds = dados.get(
        "response",
        []
    )

    paging = dados.get(
        "paging",
        {}
    )

    print()
    print(
        "Resultados recebidos:",
        len(response_odds)
    )

    print(
        "Página:",
        paging.get("current"),
        "/",
        paging.get("total")
    )

    if not response_odds:

        print()
        print(
            "A API não retornou odds "
            "nesta consulta."
        )

        return

    item_odds, casas = escolher_partida(
        response_odds
    )

    if not item_odds:

        print()
        print(
            "Existem partidas com odds, "
            "mas nenhuma das 6 casas do "
            "EntradaPro apareceu nesta página."
        )

        return

    mostrar_partida(
        item_odds
    )

    mostrar_odds(
        casas
    )

    mostrar_resumo(
        casas
    )


if __name__ == "__main__":
    main()