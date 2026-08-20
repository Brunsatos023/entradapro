def limitar_percentual(valor):
    return max(0.0, min(float(valor), 100.0))


class MatchPredictor:

    def __init__(self, analise_casa, analise_fora):
        self.casa = analise_casa
        self.fora = analise_fora

    def validar_dados(self):
        campos_obrigatorios = [
            "media_gols_marcados",
            "media_gols_sofridos",
            "percentual_over15",
            "percentual_btts"
        ]

        for campo in campos_obrigatorios:
            if campo not in self.casa:
                return {
                    "erro": (
                        f"O campo '{campo}' não foi encontrado "
                        "na análise do mandante."
                    )
                }

            if campo not in self.fora:
                return {
                    "erro": (
                        f"O campo '{campo}' não foi encontrado "
                        "na análise do visitante."
                    )
                }

        return None

    def calcular_expectativa_gols(self):
        ataque_casa = self.casa[
            "media_gols_marcados"
        ]

        defesa_visitante = self.fora[
            "media_gols_sofridos"
        ]

        ataque_fora = self.fora[
            "media_gols_marcados"
        ]

        defesa_mandante = self.casa[
            "media_gols_sofridos"
        ]

        gols_esperados_casa = (
            ataque_casa + defesa_visitante
        ) / 2

        gols_esperados_fora = (
            ataque_fora + defesa_mandante
        ) / 2

        return {
            "gols_esperados_casa": gols_esperados_casa,
            "gols_esperados_fora": gols_esperados_fora,
            "gols_esperados_total": (
                gols_esperados_casa
                + gols_esperados_fora
            )
        }

    def calcular_mais_15(self):
        historico_mais_15 = (
            self.casa["percentual_over15"]
            + self.fora["percentual_over15"]
        ) / 2

        expectativa = self.calcular_expectativa_gols()

        fator_gols = limitar_percentual(
            expectativa["gols_esperados_total"]
            / 3
            * 100
        )

        forca_ofensiva = (
            self.casa["media_gols_marcados"]
            + self.fora["media_gols_marcados"]
        ) / 2

        fator_ofensivo = limitar_percentual(
            forca_ofensiva
            / 2.5
            * 100
        )

        vulnerabilidade_defensiva = (
            self.casa["media_gols_sofridos"]
            + self.fora["media_gols_sofridos"]
        ) / 2

        fator_defensivo = limitar_percentual(
            vulnerabilidade_defensiva
            / 2
            * 100
        )

        score = (
            historico_mais_15 * 0.45
            + fator_gols * 0.25
            + fator_ofensivo * 0.15
            + fator_defensivo * 0.15
        )

        return round(
            limitar_percentual(score),
            2
        )

    def calcular_mais_25(self):
        historico_mais_25 = (
            self.casa["percentual_over25"]
            + self.fora["percentual_over25"]
        ) / 2

        expectativa = self.calcular_expectativa_gols()

        fator_gols = limitar_percentual(
            expectativa["gols_esperados_total"]
            / 3.5
            * 100
        )

        forca_ofensiva = (
            self.casa["media_gols_marcados"]
            + self.fora["media_gols_marcados"]
        ) / 2

        fator_ofensivo = limitar_percentual(
            forca_ofensiva
            / 3
            * 100
        )

        vulnerabilidade_defensiva = (
            self.casa["media_gols_sofridos"]
            + self.fora["media_gols_sofridos"]
        ) / 2

        fator_defensivo = limitar_percentual(
            vulnerabilidade_defensiva
            / 2.5
            * 100
        )

        score = (
            historico_mais_25 * 0.45
            + fator_gols * 0.25
            + fator_ofensivo * 0.15
            + fator_defensivo * 0.15
        )

        return round(
            limitar_percentual(score),
            2
        )

    def calcular_ambas_marcam(self):
        historico_btts = (
            self.casa["percentual_btts"]
            + self.fora["percentual_btts"]
        ) / 2

        ataque_casa = self.casa[
            "media_gols_marcados"
        ]

        ataque_fora = self.fora[
            "media_gols_marcados"
        ]

        equilibrio_ofensivo = min(
            ataque_casa,
            ataque_fora
        )

        fator_ofensivo = limitar_percentual(
            equilibrio_ofensivo
            / 2
            * 100
        )

        vulnerabilidade_defensiva = (
            self.casa["media_gols_sofridos"]
            + self.fora["media_gols_sofridos"]
        ) / 2

        fator_defensivo = limitar_percentual(
            vulnerabilidade_defensiva
            / 2
            * 100
        )

        score = (
            historico_btts * 0.50
            + fator_ofensivo * 0.30
            + fator_defensivo * 0.20
        )

        return round(
            limitar_percentual(score),
            2
        )

    def gerar_motivos_mais_15(self):
        motivos = []

        media_historica = (
            self.casa["percentual_over15"]
            + self.fora["percentual_over15"]
        ) / 2

        expectativa = self.calcular_expectativa_gols()

        media_ataques = (
            self.casa["media_gols_marcados"]
            + self.fora["media_gols_marcados"]
        ) / 2

        if media_historica >= 70:
            motivos.append(
                "Alta frequência recente de jogos "
                "com pelo menos dois gols."
            )

        if expectativa["gols_esperados_total"] >= 2:
            motivos.append(
                "A expectativa combinada de gols "
                "é igual ou superior a dois."
            )

        if media_ataques >= 1.5:
            motivos.append(
                "As equipes apresentam boa "
                "produção ofensiva recente."
            )

        if not motivos:
            motivos.append(
                "Os dados recentes não apresentam "
                "sinais fortes para este mercado."
            )

        return motivos

    def gerar_motivos_mais_25(self):
        motivos = []

        media_historica = (
            self.casa["percentual_over25"]
            + self.fora["percentual_over25"]
        ) / 2

        expectativa = self.calcular_expectativa_gols()

        media_ataques = (
            self.casa["media_gols_marcados"]
            + self.fora["media_gols_marcados"]
        ) / 2

        if media_historica >= 60:
            motivos.append(
                "Alta frequência recente de jogos "
                "com três gols ou mais."
            )

        if expectativa["gols_esperados_total"] >= 2.7:
            motivos.append(
                "A expectativa combinada de gols "
                "é igual ou superior a 2,7."
            )

        if media_ataques >= 1.7:
            motivos.append(
                "As equipes apresentam produção "
                "ofensiva recente elevada."
            )

        if not motivos:
            motivos.append(
                "Os dados recentes não apresentam "
                "sinais fortes para este mercado."
            )

        return motivos

    def gerar_motivos_btts(self):
        motivos = []

        media_btts = (
            self.casa["percentual_btts"]
            + self.fora["percentual_btts"]
        ) / 2

        ataque_casa = self.casa[
            "media_gols_marcados"
        ]

        ataque_fora = self.fora[
            "media_gols_marcados"
        ]

        media_sofridos = (
            self.casa["media_gols_sofridos"]
            + self.fora["media_gols_sofridos"]
        ) / 2

        if media_btts >= 60:
            motivos.append(
                "Ambas as equipes marcaram com "
                "frequência nos jogos recentes."
            )

        if ataque_casa >= 1.2 and ataque_fora >= 1.2:
            motivos.append(
                "Os dois ataques apresentam média "
                "recente superior a um gol."
            )

        if media_sofridos >= 1:
            motivos.append(
                "As duas defesas apresentam "
                "vulnerabilidade recente."
            )

        if not motivos:
            motivos.append(
                "Os dados não indicam tendência "
                "forte para ambas marcarem."
            )

        return motivos

    def classificar_over15(self, score):
        if score >= 85:
            return "SINAL MUITO FORTE"

        if score >= 80:
            return "SINAL FORTE"

        if score >= 70:
            return "SINAL"

        return "NÃO QUALIFICADA"

    def classificar_status_estrategico_over15(self, score):
        if score >= 85:
            return "APTO EXPERIMENTAL"

        if score >= 80:
            return "APTO FORTE"

        if score >= 70:
            return "APTO"

        return "NÃO APTO"

    def classificar_over25(self, score):
        if score >= 80:
            return "SINAL MUITO FORTE"

        if score >= 72:
            return "SINAL FORTE"

        if score >= 60:
            return "SINAL"

        return "NÃO QUALIFICADA"

    def classificar_status_estrategico_over25(self, score):
        if score >= 80:
            return "APTO EXPERIMENTAL"

        if score >= 72:
            return "APTO FORTE"

        if score >= 60:
            return "APTO"

        return "NÃO APTO"

    def classificar_btts(self, score):
        if score >= 80:
            return "SINAL ALTO"

        if score >= 70:
            return "SINAL"

        if score >= 60:
            return "SINAL MODERADO"

        return "SINAL BAIXO"

    def classificar_status_estrategico_btts(self):
        return "NÃO VALIDADO"

    def gerar_previsao(self):
        erro = self.validar_dados()

        if erro:
            return erro

        expectativa = self.calcular_expectativa_gols()

        score_mais_15 = self.calcular_mais_15()
        score_mais_25 = self.calcular_mais_25()
        score_btts = self.calcular_ambas_marcam()

        if score_mais_15 >= score_btts:
            melhor_mercado = "Mais de 1,5 gols"
            melhor_score = score_mais_15
        else:
            melhor_mercado = "Ambas marcam — Sim"
            melhor_score = score_btts

        return {
            "gols_esperados_casa": round(
                expectativa["gols_esperados_casa"],
                2
            ),
            "gols_esperados_fora": round(
                expectativa["gols_esperados_fora"],
                2
            ),
            "gols_esperados_total": round(
                expectativa["gols_esperados_total"],
                2
            ),

            "mais_15": score_mais_15,
            "classificacao_over15": (
                self.classificar_over15(
                    score_mais_15
                )
            ),
            "status_estrategico_over15": (
                self.classificar_status_estrategico_over15(
                    score_mais_15
                )
            ),

            "mais_25": score_mais_25,
            "classificacao_over25": (
                self.classificar_over25(
                    score_mais_25
                )
            ),
            "status_estrategico_over25": (
                self.classificar_status_estrategico_over25(
                    score_mais_25
                )
            ),

            "ambas_marcam": score_btts,
            "classificacao_btts": (
                self.classificar_btts(
                    score_btts
                )
            ),
            "status_estrategico_btts": (
                self.classificar_status_estrategico_btts()
            ),

            "melhor_mercado": melhor_mercado,
            "melhor_score": melhor_score,

            "motivos_mais_15": (
                self.gerar_motivos_mais_15()
            ),
            "motivos_mais_25": (
                self.gerar_motivos_mais_25()
            ),
            "motivos_btts": (
                self.gerar_motivos_btts()
            )
        }