"""
StandingsService: calcula a tabela de classificação do
Brasileirão a partir do dataset histórico local — pontos, jogos,
vitórias, empates, derrotas e saldo de gols, exatamente como uma
tabela de campeonato de verdade. Não depende de nenhuma API
externa (mesma vantagem do ShowcaseService).
"""

from data_storage import carregar_json


def calcular_tabela_classificacao(
    nome_arquivo_dataset="brasileirao_serie_a_2024.json",
):
    """
    Retorna a tabela final de classificação da temporada, já
    ordenada por pontos (critério de desempate: saldo de gols,
    depois gols marcados).
    """
    dados = carregar_json(nome_arquivo_dataset)
    partidas = dados.get("response", [])

    estatisticas = {}

    def _time(nome):
        if nome not in estatisticas:
            estatisticas[nome] = {
                "time": nome,
                "pontos": 0,
                "jogos": 0,
                "vitorias": 0,
                "empates": 0,
                "derrotas": 0,
                "gols_marcados": 0,
                "gols_sofridos": 0,
            }
        return estatisticas[nome]

    for partida in partidas:
        gols = partida.get("goals", {})
        gols_casa = gols.get("home")
        gols_fora = gols.get("away")

        if gols_casa is None or gols_fora is None:
            continue

        nome_casa = partida["teams"]["home"]["name"]
        nome_fora = partida["teams"]["away"]["name"]

        casa = _time(nome_casa)
        fora = _time(nome_fora)

        casa["jogos"] += 1
        fora["jogos"] += 1
        casa["gols_marcados"] += gols_casa
        casa["gols_sofridos"] += gols_fora
        fora["gols_marcados"] += gols_fora
        fora["gols_sofridos"] += gols_casa

        if gols_casa > gols_fora:
            casa["vitorias"] += 1
            casa["pontos"] += 3
            fora["derrotas"] += 1
        elif gols_fora > gols_casa:
            fora["vitorias"] += 1
            fora["pontos"] += 3
            casa["derrotas"] += 1
        else:
            casa["empates"] += 1
            fora["empates"] += 1
            casa["pontos"] += 1
            fora["pontos"] += 1

    tabela = list(estatisticas.values())

    for linha in tabela:
        linha["saldo_gols"] = (
            linha["gols_marcados"] - linha["gols_sofridos"]
        )

    tabela.sort(
        key=lambda t: (
            t["pontos"], t["saldo_gols"], t["gols_marcados"]
        ),
        reverse=True,
    )

    for posicao, linha in enumerate(tabela, start=1):
        linha["posicao"] = posicao

    return {"sucesso": True, "tabela": tabela}
