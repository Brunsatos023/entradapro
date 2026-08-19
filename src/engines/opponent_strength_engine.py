from engines.rating_engine import RatingEngine


STATUS_ENCERRADOS = {"FT", "AET", "PEN"}


class OpponentStrengthEngine:
    def __init__(
        self,
        partidas,
        team_id,
        janela_adversarios=5,
        janela_rating=3
    ):
        self.partidas = partidas
        self.team_id = team_id
        self.janela_adversarios = janela_adversarios
        self.janela_rating = janela_rating

    @staticmethod
    def limitar_nota(valor):
        return max(0.0, min(valor, 100.0))

    @staticmethod
    def classificar_dificuldade(nota):
        if nota >= 80:
            return "Muito difícil"

        if nota >= 70:
            return "Difícil"

        if nota >= 60:
            return "Moderada"

        if nota >= 50:
            return "Acessível"

        return "Baixa"

    def _buscar_ultimos_confrontos(self):
        partidas_do_time = [
            partida
            for partida in self.partidas
            if (
                partida["fixture"]["status"]["short"]
                in STATUS_ENCERRADOS
                and (
                    partida["teams"]["home"]["id"]
                    == self.team_id
                    or partida["teams"]["away"]["id"]
                    == self.team_id
                )
            )
        ]

        return sorted(
            partidas_do_time,
            key=lambda partida: partida["fixture"]["timestamp"],
            reverse=True
        )[:self.janela_adversarios]

    def _identificar_adversario(self, partida):
        time_casa = partida["teams"]["home"]
        time_fora = partida["teams"]["away"]

        if time_casa["id"] == self.team_id:
            return time_fora

        return time_casa

    def analisar(self):
        confrontos = self._buscar_ultimos_confrontos()

        if not confrontos:
            return {
                "erro": "Nenhum confronto encontrado para a equipe."
            }

        adversarios_analisados = []

        for confronto in confrontos:
            adversario = self._identificar_adversario(
                confronto
            )

            timestamp_confronto = (
                confronto["fixture"]["timestamp"]
            )

            partidas_anteriores = [
                partida
                for partida in self.partidas
                if (
                    partida["fixture"]["status"]["short"]
                    in STATUS_ENCERRADOS
                    and partida["fixture"]["timestamp"]
                    < timestamp_confronto
                )
            ]

            rating_engine = RatingEngine(
                partidas=partidas_anteriores,
                team_id=adversario["id"],
                janela=self.janela_rating
            )

            rating_adversario = rating_engine.analisar()

            if rating_adversario.get("erro"):
                continue

            adversarios_analisados.append({
                "nome": adversario["name"],
                "rating": rating_adversario["rating"],
                "categoria": rating_adversario["categoria"],
                "data_confronto": confronto["fixture"]["date"]
            })

        if not adversarios_analisados:
            return {
                "erro": (
                    "Não houve histórico suficiente para "
                    "calcular os ratings dos adversários."
                )
            }

        ratings = [
            adversario["rating"]
            for adversario in adversarios_analisados
        ]

        media_rating = sum(ratings) / len(ratings)

        return {
            "adversarios": adversarios_analisados,
            "quantidade_analisada": len(
                adversarios_analisados
            ),
            "rating_medio_adversarios": media_rating,
            "maior_rating": max(ratings),
            "menor_rating": min(ratings),
            "dificuldade": self.classificar_dificuldade(
                media_rating
            ),
            "opponent_strength_score": self.limitar_nota(
                media_rating
            )
        }