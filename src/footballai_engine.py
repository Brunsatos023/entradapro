from engines.form_engine import FormEngine
from engines.home_away_engine import HomeAwayEngine
from engines.rating_engine import RatingEngine
from engines.opponent_strength_engine import OpponentStrengthEngine
from engines.pulse_engine import PulseEngine


class FootballAIEngine:

    def __init__(self, partidas, team_id, janela=5):
        self.partidas = partidas
        self.team_id = team_id
        self.janela = janela

    def analisar(self):
        resultado = {}

        resultado["form"] = FormEngine(
            self.partidas,
            self.team_id,
            self.janela
        ).analisar()

        resultado["home_away"] = HomeAwayEngine(
            self.partidas,
            self.team_id,
            self.janela
        ).analisar()

        resultado["rating"] = RatingEngine(
            self.partidas,
            self.team_id,
            self.janela
        ).analisar()

        resultado["opponent"] = OpponentStrengthEngine(
            self.partidas,
            self.team_id
        ).analisar()

        resultado["pulse"] = PulseEngine(
            self.partidas,
            self.team_id,
            self.janela
        ).analisar()

        if (
            resultado["form"].get("erro")
            or resultado["rating"].get("erro")
            or resultado["opponent"].get("erro")
            or resultado["pulse"].get("erro")
        ):
            return {
                "erro": (
                    "Não foi possível calcular o Intelligence Score "
                    "porque um dos motores retornou erro."
                ),
                "detalhes": resultado
            }

        if (
            resultado["home_away"]["casa"].get("erro")
            or resultado["home_away"]["fora"].get("erro")
        ):
            return {
                "erro": (
                    "Não foi possível calcular o Intelligence Score "
                    "por falta de histórico suficiente de casa ou fora."
                ),
                "detalhes": resultado
            }

        nota_rating = resultado["rating"]["rating"]
        nota_forma = resultado["form"]["nota_forma"]
        nota_pulse = resultado["pulse"]["pulse_score"]

        nota_casa = resultado["home_away"]["casa"]["nota"]
        nota_fora = resultado["home_away"]["fora"]["nota"]

        nota_home_away = (
            nota_casa + nota_fora
        ) / 2

        nota_opponent = resultado["opponent"][
            "opponent_strength_score"
        ]

        intelligence_score = (
            nota_rating * 0.35
            + nota_forma * 0.25
            + nota_pulse * 0.15
            + nota_home_away * 0.15
            + nota_opponent * 0.10
        )

        resultado["intelligence_score"] = round(
            intelligence_score,
            2
        )

        if intelligence_score >= 90:
            categoria = "Elite"
        elif intelligence_score >= 80:
            categoria = "Muito Forte"
        elif intelligence_score >= 70:
            categoria = "Forte"
        elif intelligence_score >= 60:
            categoria = "Competitivo"
        elif intelligence_score >= 50:
            categoria = "Instável"
        else:
            categoria = "Em queda"

        resultado["categoria_intelligence"] = categoria

        resultado["notas_resumidas"] = {
            "rating": round(nota_rating, 2),
            "forma": round(nota_forma, 2),
            "pulse": round(nota_pulse, 2),
            "home_away": round(nota_home_away, 2),
            "opponent": round(nota_opponent, 2)
        }

        return resultado