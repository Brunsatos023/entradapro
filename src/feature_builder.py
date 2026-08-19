from collections import defaultdict


class FeatureBuilder:

    def __init__(self, partidas):
        self.partidas = partidas

    def calcular_estatisticas(self):

        estatisticas = defaultdict(lambda: {

            "jogos": 0,

            "vitorias": 0,

            "empates": 0,

            "derrotas": 0,

            "gols_marcados": 0,

            "gols_sofridos": 0

        })

        for partida in self.partidas:

            if partida["fixture"]["status"]["short"] not in [
                "FT",
                "AET",
                "PEN"
            ]:
                continue

            casa = partida["teams"]["home"]["name"]
            fora = partida["teams"]["away"]["name"]

            gols_casa = partida["goals"]["home"]
            gols_fora = partida["goals"]["away"]

            estatisticas[casa]["jogos"] += 1
            estatisticas[fora]["jogos"] += 1

            estatisticas[casa]["gols_marcados"] += gols_casa
            estatisticas[casa]["gols_sofridos"] += gols_fora

            estatisticas[fora]["gols_marcados"] += gols_fora
            estatisticas[fora]["gols_sofridos"] += gols_casa

            if gols_casa > gols_fora:

                estatisticas[casa]["vitorias"] += 1
                estatisticas[fora]["derrotas"] += 1

            elif gols_casa < gols_fora:

                estatisticas[fora]["vitorias"] += 1
                estatisticas[casa]["derrotas"] += 1

            else:

                estatisticas[casa]["empates"] += 1
                estatisticas[fora]["empates"] += 1

        return estatisticas