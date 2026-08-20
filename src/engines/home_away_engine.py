STATUS_ENCERRADOS = {"FT", "AET", "PEN"}


class HomeAwayEngine:
    def __init__(self, partidas, team_id, janela=5):
        self.team_id = team_id
        self.janela = janela

        self.partidas = [
            partida
            for partida in partidas
            if (
                partida["fixture"]["status"]["short"]
                in STATUS_ENCERRADOS
                and (
                    partida["teams"]["home"]["id"] == team_id
                    or partida["teams"]["away"]["id"] == team_id
                )
            )
        ]

    @staticmethod
    def limitar_nota(valor):
        return max(0.0, min(valor, 100.0))

    def _selecionar_partidas(self, mando):
        if mando == "casa":
            partidas_filtradas = [
                partida
                for partida in self.partidas
                if partida["teams"]["home"]["id"] == self.team_id
            ]

        else:
            partidas_filtradas = [
                partida
                for partida in self.partidas
                if partida["teams"]["away"]["id"] == self.team_id
            ]

        return sorted(
            partidas_filtradas,
            key=lambda partida: partida["fixture"]["timestamp"],
            reverse=True
        )[:self.janela]

    def _analisar_mando(self, mando):
        partidas = self._selecionar_partidas(mando)

        total_jogos = len(partidas)

        if total_jogos == 0:
            return {
                "erro": f"Nenhuma partida encontrada como {mando}."
            }

        vitorias = 0
        empates = 0
        derrotas = 0

        gols_marcados = 0
        gols_sofridos = 0
        jogos_over15 = 0
        jogos_over25 = 0
        jogos_btts = 0

        for partida in partidas:
            gols_casa = partida["goals"]["home"]
            gols_fora = partida["goals"]["away"]

            if mando == "casa":
                gols_time = gols_casa
                gols_adversario = gols_fora
            else:
                gols_time = gols_fora
                gols_adversario = gols_casa

            gols_marcados += gols_time
            gols_sofridos += gols_adversario

            if gols_time > gols_adversario:
                vitorias += 1
            elif gols_time == gols_adversario:
                empates += 1
            else:
                derrotas += 1

            if gols_casa + gols_fora >= 2:
                jogos_over15 += 1

            if gols_casa + gols_fora >= 3:
                jogos_over25 += 1

            if gols_casa > 0 and gols_fora > 0:
                jogos_btts += 1

        pontos = vitorias * 3 + empates

        aproveitamento = (
            pontos / (total_jogos * 3) * 100
        )

        media_gols_marcados = (
            gols_marcados / total_jogos
        )

        media_gols_sofridos = (
            gols_sofridos / total_jogos
        )

        percentual_over15 = (
            jogos_over15 / total_jogos * 100
        )

        percentual_over25 = (
            jogos_over25 / total_jogos * 100
        )

        percentual_btts = (
            jogos_btts / total_jogos * 100
        )

        nota_ataque = self.limitar_nota(
            media_gols_marcados / 2.5 * 100
        )

        nota_defesa = self.limitar_nota(
            100 - media_gols_sofridos / 2.5 * 100
        )

        nota_mando = (
            aproveitamento * 0.50
            + nota_ataque * 0.30
            + nota_defesa * 0.20
        )

        nota_mando = self.limitar_nota(
            nota_mando
        )

        return {
            "jogos_analisados": total_jogos,
            "vitorias": vitorias,
            "empates": empates,
            "derrotas": derrotas,
            "aproveitamento": aproveitamento,
            "media_gols_marcados": media_gols_marcados,
            "media_gols_sofridos": media_gols_sofridos,
            "percentual_over15": percentual_over15,
            "percentual_over25": percentual_over25,
            "percentual_btts": percentual_btts,
            "nota": nota_mando
        }

    def analisar(self):
        return {
            "casa": self._analisar_mando("casa"),
            "fora": self._analisar_mando("fora")
        }