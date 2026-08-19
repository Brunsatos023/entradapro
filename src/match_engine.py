class MatchEngine:

    def __init__(
        self,
        analise_casa,
        analise_fora
    ):
        self.casa = analise_casa
        self.fora = analise_fora

    @staticmethod
    def limitar_percentual(valor):
        return max(0.0, min(valor, 100.0))

    def calcular_diferenca(self):
        return (
            self.casa["intelligence_score"]
            - self.fora["intelligence_score"]
        )

    def calcular_probabilidades(self):

        diferenca = self.calcular_diferenca()

        casa = 45 + diferenca * 0.80
        fora = 45 - diferenca * 0.80

        empate = (
            100
            - casa
            - fora
        )

        casa = self.limitar_percentual(casa)
        empate = self.limitar_percentual(empate)
        fora = self.limitar_percentual(fora)

        soma = casa + empate + fora

        casa = casa / soma * 100
        empate = empate / soma * 100
        fora = fora / soma * 100

        return (
            round(casa, 2),
            round(empate, 2),
            round(fora, 2)
        )

    def favorito(self):

        casa, empate, fora = (
            self.calcular_probabilidades()
        )

        if casa > fora:
            return "Mandante"

        if fora > casa:
            return "Visitante"

        return "Equilibrado"

    def nivel_confianca(self):

        diferenca = abs(
            self.calcular_diferenca()
        )

        if diferenca >= 30:
            return "Muito Alta"

        if diferenca >= 20:
            return "Alta"

        if diferenca >= 10:
            return "Média"

        return "Baixa"

    def analisar(self):

        casa, empate, fora = (
            self.calcular_probabilidades()
        )

        return {

            "intelligence_casa":
                round(
                    self.casa["intelligence_score"],
                    2
                ),

            "intelligence_fora":
                round(
                    self.fora["intelligence_score"],
                    2
                ),

            "diferenca":
                round(
                    self.calcular_diferenca(),
                    2
                ),

            "probabilidade_casa":
                casa,

            "probabilidade_empate":
                empate,

            "probabilidade_fora":
                fora,

            "favorito":
                self.favorito(),

            "confianca":
                self.nivel_confianca()
        }