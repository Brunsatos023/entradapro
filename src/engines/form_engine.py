STATUS_ENCERRADOS = {"FT", "AET", "PEN"}


class FormEngine:
    def __init__(self, partidas, team_id, janela=5):
        self.team_id = team_id
        self.janela = janela

        partidas_encerradas = [
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

        self.partidas = sorted(
            partidas_encerradas,
            key=lambda partida: partida["fixture"]["timestamp"],
            reverse=True
        )[:janela]

    @staticmethod
    def limitar_nota(valor):
        return max(0.0, min(valor, 100.0))

    def analisar(self):
        total_jogos = len(self.partidas)

        if total_jogos == 0:
            return {
                "erro": "Nenhuma partida encontrada para essa equipe."
            }

        vitorias = 0
        empates = 0
        derrotas = 0

        gols_marcados = 0
        gols_sofridos = 0

        sequencia = []

        for partida in self.partidas:
            time_em_casa = (
                partida["teams"]["home"]["id"] == self.team_id
            )

            gols_casa = partida["goals"]["home"]
            gols_fora = partida["goals"]["away"]

            if time_em_casa:
                gols_time = gols_casa
                gols_adversario = gols_fora
            else:
                gols_time = gols_fora
                gols_adversario = gols_casa

            gols_marcados += gols_time
            gols_sofridos += gols_adversario

            if gols_time > gols_adversario:
                vitorias += 1
                sequencia.append("V")

            elif gols_time == gols_adversario:
                empates += 1
                sequencia.append("E")

            else:
                derrotas += 1
                sequencia.append("D")

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

        saldo_medio = (
            media_gols_marcados
            - media_gols_sofridos
        )

        nota_saldo = self.limitar_nota(
            ((saldo_medio + 2) / 4) * 100
        )

        nota_ofensiva = self.limitar_nota(
            media_gols_marcados / 2.5 * 100
        )

        nota_forma = (
            aproveitamento * 0.60
            + nota_saldo * 0.25
            + nota_ofensiva * 0.15
        )

        nota_forma = self.limitar_nota(
            nota_forma
        )

        return {
            "jogos_analisados": total_jogos,
            "vitorias": vitorias,
            "empates": empates,
            "derrotas": derrotas,
            "sequencia": sequencia,
            "aproveitamento": aproveitamento,
            "media_gols_marcados": media_gols_marcados,
            "media_gols_sofridos": media_gols_sofridos,
            "saldo_medio": saldo_medio,
            "nota_forma": nota_forma
        }