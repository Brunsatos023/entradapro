from engines.form_engine import FormEngine
from engines.home_away_engine import HomeAwayEngine


class RatingEngine:
    def __init__(self, partidas, team_id, janela=5):
        self.partidas = partidas
        self.team_id = team_id
        self.janela = janela

    @staticmethod
    def limitar_nota(valor):
        return max(0.0, min(valor, 100.0))

    @staticmethod
    def classificar_rating(nota):
        if nota >= 90:
            return "Elite"

        if nota >= 80:
            return "Muito Forte"

        if nota >= 70:
            return "Forte"

        if nota >= 60:
            return "Competitivo"

        if nota >= 50:
            return "Regular"

        return "Em má fase"

    def analisar(self):
        form_engine = FormEngine(
            partidas=self.partidas,
            team_id=self.team_id,
            janela=self.janela
        )

        home_away_engine = HomeAwayEngine(
            partidas=self.partidas,
            team_id=self.team_id,
            janela=self.janela
        )

        forma = form_engine.analisar()
        casa_fora = home_away_engine.analisar()

        if forma.get("erro"):
            return {
                "erro": forma["erro"]
            }

        analise_casa = casa_fora["casa"]
        analise_fora = casa_fora["fora"]

        if (
            analise_casa.get("erro")
            or analise_fora.get("erro")
        ):
            return {
                "erro": (
                    "Não há partidas suficientes "
                    "para calcular casa e fora."
                )
            }

        nota_ataque = self.limitar_nota(
            forma["media_gols_marcados"]
            / 2.5
            * 100
        )

        nota_defesa = self.limitar_nota(
            100
            - (
                forma["media_gols_sofridos"]
                / 2.5
                * 100
            )
        )

        nota_forma = forma["nota_forma"]

        nota_casa = analise_casa["nota"]
        nota_fora = analise_fora["nota"]

        diferenca_mandos = abs(
            nota_casa - nota_fora
        )

        nota_consistencia = self.limitar_nota(
            100 - diferenca_mandos
        )

        rating_final = (
            nota_ataque * 0.30
            + nota_defesa * 0.25
            + nota_forma * 0.20
            + nota_casa * 0.10
            + nota_fora * 0.05
            + nota_consistencia * 0.10
        )

        rating_final = self.limitar_nota(
            rating_final
        )

        return {
            "ataque": nota_ataque,
            "defesa": nota_defesa,
            "forma": nota_forma,
            "casa": nota_casa,
            "fora": nota_fora,
            "consistencia": nota_consistencia,
            "rating": rating_final,
            "categoria": self.classificar_rating(
                rating_final
            )
        }