class OpportunityEngine:

    def __init__(
        self,
        resultado_match,
        resultado_prediction,
        melhor_mercado,
        resultado_value
    ):
        self.resultado_match = resultado_match
        self.resultado_prediction = resultado_prediction
        self.melhor_mercado = melhor_mercado
        self.resultado_value = resultado_value

    def obter_score_mercado_selecionado(self):

        if self.melhor_mercado == "Mais de 1,5 gols":
            return float(
                self.resultado_prediction["mais_15"]
            )

        return float(
            self.resultado_prediction["ambas_marcam"]
        )

    def calcular_score(self):

        inteligencia = (
            self.resultado_match["intelligence_casa"]
            + self.resultado_match["intelligence_fora"]
        ) / 2

        probabilidade = (
            self.obter_score_mercado_selecionado()
        )

        edge = self.resultado_value["edge"]

        valor = self.resultado_value["valor_esperado"]

        score = (
            inteligencia * 0.40
            + probabilidade * 0.30
            + edge * 1.50
            + valor * 0.30
        )

        return min(
            round(score, 2),
            100
        )

    def classificar_confianca(self, score):

        if score >= 90:
            return "MUITO ALTA"

        if score >= 80:
            return "ALTA"

        if score >= 70:
            return "BOA"

        if score >= 60:
            return "MÉDIA"

        return "BAIXA"

    def gerar_motivos(self):

        motivos = []

        probabilidade = (
            self.obter_score_mercado_selecionado()
        )

        if self.resultado_value["edge"] >= 10:
            motivos.append(
                "Edge acima de 10%."
            )

        if self.resultado_value["valor_esperado"] >= 10:
            motivos.append(
                "Valor esperado positivo."
            )

        if probabilidade >= 75:
            motivos.append(
                "Score elevado no mercado selecionado."
            )

        if not motivos:
            motivos.append(
                "Sem fatores fortes encontrados."
            )

        return motivos

    def analisar(self):

        score = self.calcular_score()

        return {
            "footballai_score": score,
            "confianca": (
                self.classificar_confianca(
                    score
                )
            ),
            "mercado_analisado": (
                self.melhor_mercado
            ),
            "score_mercado": (
                self.obter_score_mercado_selecionado()
            ),
            "motivos": self.gerar_motivos()
        }