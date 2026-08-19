from footballai_engine import FootballAIEngine
from match_engine import MatchEngine
from predictor import MatchPredictor
from engines.recommendation_engine import RecommendationEngine
from engines.value_engine import ValueEngine


class AnalysisPipeline:

    def __init__(
        self,
        partidas,
        id_mandante,
        id_visitante,
        odd_over15,
        odd_btts,
        janela=5
    ):
        self.partidas = partidas
        self.id_mandante = id_mandante
        self.id_visitante = id_visitante
        self.odd_over15 = odd_over15
        self.odd_btts = odd_btts
        self.janela = janela

    def executar(self):

        analise_mandante = FootballAIEngine(
            partidas=self.partidas,
            team_id=self.id_mandante,
            janela=self.janela
        ).analisar()

        if analise_mandante.get("erro"):
            return analise_mandante

        analise_visitante = FootballAIEngine(
            partidas=self.partidas,
            team_id=self.id_visitante,
            janela=self.janela
        ).analisar()

        if analise_visitante.get("erro"):
            return analise_visitante

        resultado_match = MatchEngine(
            analise_casa=analise_mandante,
            analise_fora=analise_visitante
        ).analisar()

        if resultado_match.get("erro"):
            return resultado_match

        dados_mandante = analise_mandante[
            "home_away"
        ]["casa"]

        dados_visitante = analise_visitante[
            "home_away"
        ]["fora"]

        resultado_prediction = MatchPredictor(
            analise_casa=dados_mandante,
            analise_fora=dados_visitante
        ).gerar_previsao()

        if resultado_prediction.get("erro"):
            return resultado_prediction

        resultado_recommendation = RecommendationEngine(
            analise_mandante=analise_mandante,
            analise_visitante=analise_visitante
        ).analisar()

        if resultado_recommendation.get("erro"):
            return resultado_recommendation

        resultado_value_over15 = ValueEngine(
            probabilidade_footballai=resultado_prediction[
                "mais_15"
            ],
            odd_casa=self.odd_over15
        ).analisar()

        if resultado_value_over15.get("erro"):
            return resultado_value_over15

        resultado_value_btts = ValueEngine(
            probabilidade_footballai=resultado_prediction[
                "ambas_marcam"
            ],
            odd_casa=self.odd_btts
        ).analisar()

        if resultado_value_btts.get("erro"):
            return resultado_value_btts

        return {

            "analise_mandante":
                analise_mandante,

            "analise_visitante":
                analise_visitante,

            "resultado_match":
                resultado_match,

            "resultado_prediction":
                resultado_prediction,

            "resultado_recommendation":
                resultado_recommendation,

            "resultados_value_mercados": {

                "over_15":
                    resultado_value_over15,

                "btts":
                    resultado_value_btts
            }
        }