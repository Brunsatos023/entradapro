from footballai_engine import FootballAIEngine
from match_engine import MatchEngine
from predictor import MatchPredictor

from engines.value_engine import ValueEngine
from engines.opportunity_engine import OpportunityEngine
from auto_tuning_service import obter_limiar_validacao_over15


class MatchAnalysisEngine:

    STATUS_OVER15_VALIDOS = {
        "APTO",
        "APTO FORTE",
        "APTO EXPERIMENTAL"
    }

    def __init__(
        self,
        partidas,
        id_mandante,
        id_visitante,
        odd_over15,
        odd_btts,
        odd_over25=None,
        janela=5
    ):
        self.partidas = partidas
        self.id_mandante = id_mandante
        self.id_visitante = id_visitante
        self.odd_over15 = float(odd_over15)
        self.odd_btts = float(odd_btts)
        self.odd_over25 = (
            float(odd_over25) if odd_over25 else None
        )
        self.janela = janela

    def analisar(self):

        analise_mandante = FootballAIEngine(
            partidas=self.partidas,
            team_id=self.id_mandante,
            janela=self.janela
        ).analisar()

        if analise_mandante.get("erro"):
            return {
                "erro": (
                    "Não foi possível analisar "
                    "o time mandante."
                ),
                "detalhes": analise_mandante
            }

        analise_visitante = FootballAIEngine(
            partidas=self.partidas,
            team_id=self.id_visitante,
            janela=self.janela
        ).analisar()

        if analise_visitante.get("erro"):
            return {
                "erro": (
                    "Não foi possível analisar "
                    "o time visitante."
                ),
                "detalhes": analise_visitante
            }

        resultado_match = MatchEngine(
            analise_casa=analise_mandante,
            analise_fora=analise_visitante
        ).analisar()

        if resultado_match.get("erro"):
            return {
                "erro": (
                    "Não foi possível comparar "
                    "as equipes."
                ),
                "detalhes": resultado_match
            }

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
            return {
                "erro": (
                    "Não foi possível gerar "
                    "a previsão da partida."
                ),
                "detalhes": resultado_prediction
            }

        selecao_mercado = (
            self._selecionar_melhor_mercado(
                resultado_prediction
            )
        )

        if selecao_mercado.get("erro"):
            return {
                "erro": (
                    "Não foi possível selecionar "
                    "o melhor mercado."
                ),
                "detalhes": selecao_mercado
            }

        melhor_mercado = selecao_mercado[
            "melhor_mercado"
        ]

        mercado_para_score = selecao_mercado[
            "mercado_para_score"
        ]

        resultado_value = selecao_mercado[
            "resultado_value"
        ]

        resultado_oportunidade = OpportunityEngine(
            resultado_match=resultado_match,
            resultado_prediction=resultado_prediction,
            melhor_mercado=mercado_para_score,
            resultado_value=resultado_value
        ).analisar()

        if resultado_oportunidade.get("erro"):
            return {
                "erro": (
                    "Não foi possível calcular "
                    "o FootballAI Score."
                ),
                "detalhes": resultado_oportunidade
            }

        resultado_oportunidade[
            "recomendacao_validada"
        ] = selecao_mercado[
            "recomendacao_validada"
        ]

        resultado_oportunidade[
            "motivo_validacao"
        ] = selecao_mercado[
            "motivo_validacao"
        ]

        return {
            "analise_mandante": analise_mandante,
            "analise_visitante": analise_visitante,
            "resultado_match": resultado_match,
            "resultado_prediction": resultado_prediction,

            "melhor_mercado": melhor_mercado,

            "mercado_referencia": (
                mercado_para_score
            ),

            "recomendacao_validada": (
                selecao_mercado[
                    "recomendacao_validada"
                ]
            ),

            "motivo_validacao": (
                selecao_mercado[
                    "motivo_validacao"
                ]
            ),

            "resultado_value": resultado_value,

            "resultado_over25": (
                selecao_mercado[
                    "resultado_over25"
                ]
            ),

            "status_over25": (
                selecao_mercado[
                    "status_over25"
                ]
            ),

            "resultado_oportunidade": (
                resultado_oportunidade
            ),

            "comparacao_mercados": {
                "mais_15": selecao_mercado[
                    "resultado_over15"
                ],
                "ambas_marcam": selecao_mercado[
                    "resultado_btts"
                ],
                "mais_25": selecao_mercado[
                    "resultado_over25"
                ]
            }
        }

    def _selecionar_melhor_mercado(
        self,
        resultado_prediction
    ):

        probabilidade_over15 = float(
            resultado_prediction[
                "mais_15"
            ]
        )

        probabilidade_btts = float(
            resultado_prediction[
                "ambas_marcam"
            ]
        )

        resultado_over15 = ValueEngine(
            probabilidade_footballai=(
                probabilidade_over15
            ),
            odd_casa=self.odd_over15
        ).analisar()

        if resultado_over15.get("erro"):
            return {
                "erro": (
                    "Erro ao calcular o valor "
                    "do mercado Mais de 1,5 gols."
                ),
                "detalhes": resultado_over15
            }

        resultado_btts = ValueEngine(
            probabilidade_footballai=(
                probabilidade_btts
            ),
            odd_casa=self.odd_btts
        ).analisar()

        if resultado_btts.get("erro"):
            return {
                "erro": (
                    "Erro ao calcular o valor "
                    "do mercado Ambas marcam."
                ),
                "detalhes": resultado_btts
            }

        # Mais de 2,5 gols: exibido como informação adicional,
        # mas NÃO participa da disputa por "melhor mercado" -
        # diferente do Over 1.5, ainda não passou pela validação
        # multitemporada (backtest) que a regra estratégica V1
        # exige antes de recomendar um mercado formalmente.
        resultado_over25 = None

        if self.odd_over25:
            probabilidade_over25 = float(
                resultado_prediction.get(
                    "mais_25",
                    0
                )
            )

            resultado_over25 = ValueEngine(
                probabilidade_footballai=(
                    probabilidade_over25
                ),
                odd_casa=self.odd_over25
            ).analisar()

        status_over15 = resultado_prediction.get(
            "status_estrategico_over15",
            "NÃO APTO"
        )

        status_btts = resultado_prediction.get(
            "status_estrategico_btts",
            "NÃO VALIDADO"
        )

        status_over25 = resultado_prediction.get(
            "status_estrategico_over25",
            "NÃO APTO"
        )

        # Etapa D do roteiro autonomo: em vez de um criterio fixo
        # no codigo, o limiar minimo para considerar o Over 1.5
        # "validado" vem do auto_tuning_service - que pode ajustar
        # esse numero sozinho, com base no desempenho real
        # acumulado (ver auto_tuning_service.py). Comeca em 70,
        # exatamente igual ao comportamento original ("APTO"),
        # ate que haja dados reais suficientes para mudar.
        try:
            limiar_over15 = obter_limiar_validacao_over15()
        except Exception:
            limiar_over15 = 70.0

        score_over15 = float(
            resultado_prediction.get("mais_15", 0)
        )

        over15_validado = score_over15 >= limiar_over15

        valor_esperado_over15 = float(
            resultado_over15[
                "valor_esperado"
            ]
        )

        valor_esperado_btts = float(
            resultado_btts[
                "valor_esperado"
            ]
        )

        # ==================================================
        # REGRA ESTRATÉGICA V1
        #
        # Over 1.5 foi validado historicamente.
        # BTTS continua sendo analisado, porém ainda não
        # possui validação multitemporada suficiente.
        # ==================================================

        if over15_validado:
            return {
                "melhor_mercado": (
                    "Mais de 1,5 gols"
                ),

                "mercado_para_score": (
                    "Mais de 1,5 gols"
                ),

                "resultado_value": (
                    resultado_over15
                ),

                "resultado_over15": (
                    resultado_over15
                ),

                "resultado_btts": (
                    resultado_btts
                ),

                "resultado_over25": (
                    resultado_over25
                ),

                "recomendacao_validada": True,

                "motivo_validacao": (
                    "Over 1.5 aprovado pela "
                    "validação multitemporada."
                ),

                "status_over15": (
                    status_over15
                ),

                "status_btts": (
                    status_btts
                ),

                "status_over25": (
                    status_over25
                )
            }

        # Nenhum mercado estrategicamente validado.
        #
        # Ainda preservamos o mercado com maior valor
        # esperado como referência analítica para que
        # OpportunityEngine possa calcular suas métricas,
        # mas ele NÃO será apresentado como recomendação.

        if (
            valor_esperado_over15
            >= valor_esperado_btts
        ):
            mercado_referencia = (
                "Mais de 1,5 gols"
            )

            resultado_referencia = (
                resultado_over15
            )

        else:
            mercado_referencia = (
                "Ambas marcam — Sim"
            )

            resultado_referencia = (
                resultado_btts
            )

        return {
            "melhor_mercado": (
                "Nenhuma oportunidade validada"
            ),

            "mercado_para_score": (
                mercado_referencia
            ),

            "resultado_value": (
                resultado_referencia
            ),

            "resultado_over15": (
                resultado_over15
            ),

            "resultado_btts": (
                resultado_btts
            ),

            "resultado_over25": (
                resultado_over25
            ),

            "recomendacao_validada": False,

            "motivo_validacao": (
                "Nenhum mercado atingiu os "
                "critérios estratégicos validados "
                "da V1."
            ),

            "status_over15": (
                status_over15
            ),

            "status_btts": (
                status_btts
            ),

            "status_over25": (
                status_over25
            )
        }