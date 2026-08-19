from footballai_engine import FootballAIEngine


class TeamProfile:

    def __init__(self, partidas, team_id, team_name):

        self.partidas = partidas
        self.team_id = team_id
        self.team_name = team_name

    def gerar(self):

        engine = FootballAIEngine(
            self.partidas,
            self.team_id
        )

        resultado = engine.analisar()

        if resultado.get("erro"):
            return resultado

        return {

            "team_id": self.team_id,

            "team_name": self.team_name,

            "intelligence": resultado[
                "intelligence_score"
            ],

            "categoria": resultado[
                "categoria_intelligence"
            ],

            "rating": resultado[
                "rating"
            ]["rating"],

            "forma": resultado[
                "form"
            ]["nota_forma"],

            "pulse": resultado[
                "pulse"
            ]["pulse_score"],

            "opponent": resultado[
                "opponent"
            ]["opponent_strength_score"],

            "casa": resultado[
                "home_away"
            ]["casa"]["nota"],

            "fora": resultado[
                "home_away"
            ]["fora"]["nota"]
        }