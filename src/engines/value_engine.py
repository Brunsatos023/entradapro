class ValueEngine:

    def __init__(
        self,
        probabilidade_footballai,
        odd_casa
    ):
        self.probabilidade_footballai = (
            float(probabilidade_footballai)
        )

        self.odd_casa = float(odd_casa)

    @staticmethod
    def limitar_percentual(valor):
        return max(
            0.0,
            min(float(valor), 100.0)
        )

    def validar_dados(self):
        if self.probabilidade_footballai <= 0:
            return {
                "erro": (
                    "A probabilidade do FootballAI "
                    "precisa ser maior que zero."
                )
            }

        if self.probabilidade_footballai > 100:
            return {
                "erro": (
                    "A probabilidade do FootballAI "
                    "não pode ser maior que 100%."
                )
            }

        if self.odd_casa <= 1:
            return {
                "erro": (
                    "A odd da casa precisa ser "
                    "maior que 1.00."
                )
            }

        return None

    def calcular_probabilidade_implicita(self):
        return (
            1 / self.odd_casa
        ) * 100

    def calcular_odd_justa(self):
        probabilidade_decimal = (
            self.probabilidade_footballai / 100
        )

        return 1 / probabilidade_decimal

    def calcular_edge(self):
        probabilidade_implicita = (
            self.calcular_probabilidade_implicita()
        )

        return (
            self.probabilidade_footballai
            - probabilidade_implicita
        )

    def calcular_valor_esperado(self):
        probabilidade_decimal = (
            self.probabilidade_footballai / 100
        )

        probabilidade_perda = (
            1 - probabilidade_decimal
        )

        lucro_em_caso_de_acerto = (
            self.odd_casa - 1
        )

        valor_esperado = (
            probabilidade_decimal
            * lucro_em_caso_de_acerto
            - probabilidade_perda
        )

        return valor_esperado * 100

    def classificar_oportunidade(self):
        edge = self.calcular_edge()
        valor_esperado = self.calcular_valor_esperado()

        if edge >= 15 and valor_esperado >= 20:
            return "Excelente"

        if edge >= 10 and valor_esperado >= 10:
            return "Muito boa"

        if edge >= 5 and valor_esperado > 0:
            return "Boa"

        if edge > 0 and valor_esperado > 0:
            return "Marginal"

        return "Sem valor"

    def existe_value_bet(self):
        return (
            self.calcular_edge() > 0
            and self.calcular_valor_esperado() > 0
        )

    def analisar(self):
        erro = self.validar_dados()

        if erro:
            return erro

        probabilidade_implicita = (
            self.calcular_probabilidade_implicita()
        )

        odd_justa = self.calcular_odd_justa()
        edge = self.calcular_edge()
        valor_esperado = self.calcular_valor_esperado()

        return {
            "probabilidade_footballai": round(
                self.probabilidade_footballai,
                2
            ),

            "odd_casa": round(
                self.odd_casa,
                2
            ),

            "probabilidade_implicita": round(
                self.limitar_percentual(
                    probabilidade_implicita
                ),
                2
            ),

            "odd_justa": round(
                odd_justa,
                2
            ),

            "edge": round(
                edge,
                2
            ),

            "valor_esperado": round(
                valor_esperado,
                2
            ),

            "value_bet": self.existe_value_bet(),

            "classificacao": (
                self.classificar_oportunidade()
            )
        }