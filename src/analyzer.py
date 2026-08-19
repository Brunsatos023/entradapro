class TeamAnalyzer:
    def __init__(self, team_id, partidas, quantidade=10):
        self.team_id = team_id
        self.quantidade = quantidade

        partidas_encerradas = [
            partida
            for partida in partidas
            if partida["fixture"]["status"]["short"] in {"FT", "AET", "PEN"}
        ]

        self.partidas = sorted(
            partidas_encerradas,
            key=lambda partida: partida["fixture"]["timestamp"],
            reverse=True
        )[:quantidade]

    def analisar(self):
        total_jogos = len(self.partidas)

        if total_jogos == 0:
            return {
                "jogos_analisados": 0,
                "erro": "Nenhuma partida encerrada encontrada."
            }

        vitorias = 0
        empates = 0
        derrotas = 0

        gols_marcados = 0
        gols_sofridos = 0

        jogos_mais_15 = 0
        jogos_ambas_marcam = 0

        for jogo in self.partidas:
            gols_casa = jogo["goals"]["home"]
            gols_fora = jogo["goals"]["away"]

            time_jogou_em_casa = (
                jogo["teams"]["home"]["id"] == self.team_id
            )

            if time_jogou_em_casa:
                gols_do_time = gols_casa
                gols_do_adversario = gols_fora
            else:
                gols_do_time = gols_fora
                gols_do_adversario = gols_casa

            gols_marcados += gols_do_time
            gols_sofridos += gols_do_adversario

            if gols_do_time > gols_do_adversario:
                vitorias += 1
            elif gols_do_time == gols_do_adversario:
                empates += 1
            else:
                derrotas += 1

            if gols_casa + gols_fora >= 2:
                jogos_mais_15 += 1

            if gols_casa > 0 and gols_fora > 0:
                jogos_ambas_marcam += 1

        aproveitamento = (
            (vitorias * 3 + empates)
            / (total_jogos * 3)
            * 100
        )

        return {
            "jogos_analisados": total_jogos,
            "vitorias": vitorias,
            "empates": empates,
            "derrotas": derrotas,
            "aproveitamento": aproveitamento,
            "media_gols_marcados": gols_marcados / total_jogos,
            "media_gols_sofridos": gols_sofridos / total_jogos,
            "percentual_mais_15": jogos_mais_15 / total_jogos * 100,
            "percentual_ambas_marcam": (
                jogos_ambas_marcam / total_jogos * 100
            )
        }