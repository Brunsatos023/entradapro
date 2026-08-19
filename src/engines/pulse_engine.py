STATUS_ENCERRADOS = {"FT", "AET", "PEN"}


class PulseEngine:

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
            key=lambda partida: partida["fixture"]["timestamp"]
        )[-janela:]

    @staticmethod
    def limitar_nota(valor):
        return max(0.0, min(float(valor), 100.0))

    @staticmethod
    def media_ponderada(valores):
        """
        Dá mais importância aos jogos mais recentes.

        Exemplo com 5 jogos:
        pesos = 1, 2, 3, 4 e 5
        """

        if not valores:
            return 0.0

        pesos = list(range(1, len(valores) + 1))

        soma_ponderada = sum(
            valor * peso
            for valor, peso in zip(valores, pesos)
        )

        return soma_ponderada / sum(pesos)

    def analisar(self):
        if len(self.partidas) < 2:
            return {
                "erro": (
                    "Não há partidas suficientes "
                    "para calcular o Pulse."
                )
            }

        pontos_por_jogo = []
        saldo_por_jogo = []
        resultados = []

        for partida in self.partidas:
            time_em_casa = (
                partida["teams"]["home"]["id"]
                == self.team_id
            )

            gols_casa = partida["goals"]["home"]
            gols_fora = partida["goals"]["away"]

            if gols_casa is None or gols_fora is None:
                continue

            if time_em_casa:
                gols_time = gols_casa
                gols_adversario = gols_fora
            else:
                gols_time = gols_fora
                gols_adversario = gols_casa

            if gols_time > gols_adversario:
                pontos = 3
                resultado = "V"
            elif gols_time == gols_adversario:
                pontos = 1
                resultado = "E"
            else:
                pontos = 0
                resultado = "D"

            pontos_por_jogo.append(pontos)

            saldo_por_jogo.append(
                gols_time - gols_adversario
            )

            resultados.append(resultado)

        if len(pontos_por_jogo) < 2:
            return {
                "erro": (
                    "Não há resultados válidos suficientes "
                    "para calcular o Pulse."
                )
            }

        quantidade_jogos = len(pontos_por_jogo)

        pontos_ponderados = self.media_ponderada(
            pontos_por_jogo
        )

        saldo_ponderado = self.media_ponderada(
            saldo_por_jogo
        )

        nota_desempenho = self.limitar_nota(
            pontos_ponderados / 3 * 100
        )

        nota_saldo = self.limitar_nota(
            50 + saldo_ponderado * 20
        )

        metade = quantidade_jogos // 2

        primeira_parte_pontos = pontos_por_jogo[:metade]
        segunda_parte_pontos = pontos_por_jogo[metade:]

        primeira_parte_saldo = saldo_por_jogo[:metade]
        segunda_parte_saldo = saldo_por_jogo[metade:]

        media_pontos_inicio = (
            sum(primeira_parte_pontos)
            / len(primeira_parte_pontos)
        )

        media_pontos_fim = (
            sum(segunda_parte_pontos)
            / len(segunda_parte_pontos)
        )

        media_saldo_inicio = (
            sum(primeira_parte_saldo)
            / len(primeira_parte_saldo)
        )

        media_saldo_fim = (
            sum(segunda_parte_saldo)
            / len(segunda_parte_saldo)
        )

        tendencia_pontos = (
            media_pontos_fim
            - media_pontos_inicio
        )

        tendencia_saldo = (
            media_saldo_fim
            - media_saldo_inicio
        )

        nota_tendencia = self.limitar_nota(
            50
            + tendencia_pontos * 12
            + tendencia_saldo * 8
        )

        pulse_score = (
            nota_desempenho * 0.55
            + nota_saldo * 0.25
            + nota_tendencia * 0.20
        )

        pulse_score = round(
            self.limitar_nota(pulse_score),
            2
        )

        if pulse_score >= 80:
            tendencia = "Forte alta"

        elif pulse_score >= 65:
            tendencia = "Alta"

        elif pulse_score >= 45:
            tendencia = "Estável"

        elif pulse_score >= 30:
            tendencia = "Queda"

        else:
            tendencia = "Forte queda"

        return {
            "jogos_analisados": quantidade_jogos,
            "resultados": resultados,
            "pontos_por_jogo": pontos_por_jogo,
            "saldo_por_jogo": saldo_por_jogo,
            "pontos_ponderados": round(
                pontos_ponderados,
                2
            ),
            "saldo_ponderado": round(
                saldo_ponderado,
                2
            ),
            "nota_desempenho": round(
                nota_desempenho,
                2
            ),
            "nota_saldo": round(
                nota_saldo,
                2
            ),
            "nota_tendencia": round(
                nota_tendencia,
                2
            ),
            "tendencia_pontos": round(
                tendencia_pontos,
                2
            ),
            "tendencia_saldo": round(
                tendencia_saldo,
                2
            ),
            "pulse_score": pulse_score,
            "tendencia": tendencia
        }