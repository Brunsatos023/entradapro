class RecommendationEngine:
    """
    Interpreta as análises produzidas pelo FootballAIEngine
    para mandante e visitante.

    Cada mercado possui um contexto específico.
    """

    CHAVES_OBRIGATORIAS = {
        "form",
        "home_away",
        "rating",
        "opponent",
        "pulse",
        "intelligence_score"
    }

    LIMITE_OVER15_ALTA = 80.0
    LIMITE_OVER15_MODERADA = 65.0

    LIMITE_BTTS_ALTA = 70.0
    LIMITE_BTTS_MODERADA = 55.0

    AJUSTE_CONTEXTUAL_MAXIMO = 5.0

    PESOS_OVER15 = {
        "historico_over15": 0.30,
        "gols_marcados": 0.20,
        "gols_sofridos": 0.20,
        "forma": 0.10,
        "pulse": 0.10,
        "mando": 0.10
    }

    PESOS_BTTS = {
        "historico_btts": 0.35,
        "capacidade_marcar": 0.25,
        "vulnerabilidade_defensiva": 0.25,
        "forma": 0.05,
        "pulse": 0.05,
        "mando": 0.05
    }

    def __init__(
        self,
        analise_mandante,
        analise_visitante
    ):
        self.home = analise_mandante
        self.away = analise_visitante

    @staticmethod
    def _limitar(valor, minimo=0.0, maximo=100.0):
        return max(
            minimo,
            min(float(valor), maximo)
        )

    @staticmethod
    def _media(valor_mandante, valor_visitante):
        return (
            float(valor_mandante)
            + float(valor_visitante)
        ) / 2

    @staticmethod
    def _converter_media_gols_para_nota(media_gols):
        """
        Converte média de gols para escala de 0 a 100.

        Média de 2,5 gols ou mais recebe nota 100.
        """

        return min(
            float(media_gols) / 2.5 * 100.0,
            100.0
        )

    def _validar_analise(self, analise, identificacao):
        if not isinstance(analise, dict):
            return (
                f"A análise do {identificacao} "
                "não possui um formato válido."
            )

        if analise.get("erro"):
            return (
                f"A análise do {identificacao} retornou erro: "
                f"{analise['erro']}"
            )

        chaves_ausentes = (
            self.CHAVES_OBRIGATORIAS
            - set(analise.keys())
        )

        if chaves_ausentes:
            chaves_formatadas = ", ".join(
                sorted(chaves_ausentes)
            )

            return (
                f"A análise do {identificacao} está incompleta. "
                f"Chaves ausentes: {chaves_formatadas}."
            )

        return None

    @staticmethod
    def _validar_contexto_mando(
        analise,
        mando,
        identificacao
    ):
        home_away = analise.get("home_away", {})
        contexto = home_away.get(mando)

        if not isinstance(contexto, dict):
            return (
                None,
                f"Não foi encontrado o desempenho do "
                f"{identificacao} como {mando}."
            )

        if contexto.get("erro"):
            return (
                None,
                f"O desempenho do {identificacao} como "
                f"{mando} retornou erro: {contexto['erro']}"
            )

        return contexto, None

    def _montar_dados_base(
        self,
        contexto_mandante,
        contexto_visitante
    ):
        return {
            "mandante": {
                "intelligence_score": self._limitar(
                    self.home["intelligence_score"]
                ),
                "rating": self._limitar(
                    self.home["rating"]["rating"]
                ),
                "categoria_rating": self.home[
                    "rating"
                ]["categoria"],
                "nota_forma": self._limitar(
                    self.home["form"]["nota_forma"]
                ),
                "pulse_score": self._limitar(
                    self.home["pulse"]["pulse_score"]
                ),
                "tendencia": self.home[
                    "pulse"
                ]["tendencia"],
                "opponent_strength_score": self._limitar(
                    self.home[
                        "opponent"
                    ]["opponent_strength_score"]
                ),
                "contexto": "casa",
                "desempenho_mando": contexto_mandante
            },
            "visitante": {
                "intelligence_score": self._limitar(
                    self.away["intelligence_score"]
                ),
                "rating": self._limitar(
                    self.away["rating"]["rating"]
                ),
                "categoria_rating": self.away[
                    "rating"
                ]["categoria"],
                "nota_forma": self._limitar(
                    self.away["form"]["nota_forma"]
                ),
                "pulse_score": self._limitar(
                    self.away["pulse"]["pulse_score"]
                ),
                "tendencia": self.away[
                    "pulse"
                ]["tendencia"],
                "opponent_strength_score": self._limitar(
                    self.away[
                        "opponent"
                    ]["opponent_strength_score"]
                ),
                "contexto": "fora",
                "desempenho_mando": contexto_visitante
            }
        }

    @staticmethod
    def _classificar_amostra(jogos_analisados):
        if jogos_analisados >= 5:
            return "Adequada"

        if jogos_analisados >= 3:
            return "Limitada"

        return "Insuficiente"

    @staticmethod
    def _montar_alertas_amostra(
        amostra_mandante,
        amostra_visitante
    ):
        alertas = []

        if amostra_mandante != "Adequada":
            alertas.append(
                "A amostra do mandante é "
                f"{amostra_mandante.lower()}."
            )

        if amostra_visitante != "Adequada":
            alertas.append(
                "A amostra do visitante é "
                f"{amostra_visitante.lower()}."
            )

        return alertas

    def _converter_score_em_ajuste(self, score_contextual):
        ajuste = (
            (float(score_contextual) - 50.0)
            / 50.0
        ) * self.AJUSTE_CONTEXTUAL_MAXIMO

        return round(
            max(
                -self.AJUSTE_CONTEXTUAL_MAXIMO,
                min(
                    ajuste,
                    self.AJUSTE_CONTEXTUAL_MAXIMO
                )
            ),
            2
        )

    def _calcular_contexto_over15(self, dados_base):
        mandante = dados_base["mandante"]
        visitante = dados_base["visitante"]

        mando_mandante = mandante["desempenho_mando"]
        mando_visitante = visitante["desempenho_mando"]

        componentes = {
            "historico_over15": self._media(
                mando_mandante["percentual_over15"],
                mando_visitante["percentual_over15"]
            ),
            "gols_marcados": self._media(
                self._converter_media_gols_para_nota(
                    mando_mandante["media_gols_marcados"]
                ),
                self._converter_media_gols_para_nota(
                    mando_visitante["media_gols_marcados"]
                )
            ),
            "gols_sofridos": self._media(
                self._converter_media_gols_para_nota(
                    mando_mandante["media_gols_sofridos"]
                ),
                self._converter_media_gols_para_nota(
                    mando_visitante["media_gols_sofridos"]
                )
            ),
            "forma": self._media(
                mandante["nota_forma"],
                visitante["nota_forma"]
            ),
            "pulse": self._media(
                mandante["pulse_score"],
                visitante["pulse_score"]
            ),
            "mando": self._media(
                mando_mandante["nota"],
                mando_visitante["nota"]
            )
        }

        score_contextual = sum(
            componentes[chave]
            * self.PESOS_OVER15[chave]
            for chave in self.PESOS_OVER15
        )

        score_contextual = round(
            self._limitar(score_contextual),
            2
        )

        return {
            "score_contextual": score_contextual,
            "ajuste_contextual": (
                self._converter_score_em_ajuste(
                    score_contextual
                )
            ),
            "componentes": {
                chave: round(valor, 2)
                for chave, valor in componentes.items()
            },
            "pesos": self.PESOS_OVER15.copy()
        }

    def _calcular_contexto_btts(self, dados_base):
        mandante = dados_base["mandante"]
        visitante = dados_base["visitante"]

        mando_mandante = mandante["desempenho_mando"]
        mando_visitante = visitante["desempenho_mando"]

        capacidade_marcar = self._media(
            self._converter_media_gols_para_nota(
                mando_mandante["media_gols_marcados"]
            ),
            self._converter_media_gols_para_nota(
                mando_visitante["media_gols_marcados"]
            )
        )

        vulnerabilidade_defensiva = self._media(
            self._converter_media_gols_para_nota(
                mando_mandante["media_gols_sofridos"]
            ),
            self._converter_media_gols_para_nota(
                mando_visitante["media_gols_sofridos"]
            )
        )

        componentes = {
            "historico_btts": self._media(
                mando_mandante["percentual_btts"],
                mando_visitante["percentual_btts"]
            ),
            "capacidade_marcar": capacidade_marcar,
            "vulnerabilidade_defensiva": (
                vulnerabilidade_defensiva
            ),
            "forma": self._media(
                mandante["nota_forma"],
                visitante["nota_forma"]
            ),
            "pulse": self._media(
                mandante["pulse_score"],
                visitante["pulse_score"]
            ),
            "mando": self._media(
                mando_mandante["nota"],
                mando_visitante["nota"]
            )
        }

        score_contextual = sum(
            componentes[chave]
            * self.PESOS_BTTS[chave]
            for chave in self.PESOS_BTTS
        )

        score_contextual = round(
            self._limitar(score_contextual),
            2
        )

        return {
            "score_contextual": score_contextual,
            "ajuste_contextual": (
                self._converter_score_em_ajuste(
                    score_contextual
                )
            ),
            "componentes": {
                chave: round(valor, 2)
                for chave, valor in componentes.items()
            },
            "pesos": self.PESOS_BTTS.copy()
        }

    def _aplicar_ajuste_contextual(
        self,
        indice_estatistico,
        contexto
    ):
        indice_final = (
            float(indice_estatistico)
            + contexto["ajuste_contextual"]
        )

        return round(
            self._limitar(indice_final),
            2
        )

    @staticmethod
    def _classificar_confianca(
        indice_final,
        limite_alta,
        limite_moderada
    ):
        if indice_final >= limite_alta:
            return "Alta", True

        if indice_final >= limite_moderada:
            return "Moderada", True

        return "Baixa", False

    def _montar_recomendacao(
        self,
        mercado,
        percentual_mandante,
        percentual_visitante,
        jogos_mandante,
        jogos_visitante,
        contexto,
        limite_alta,
        limite_moderada,
        texto_mandante,
        texto_visitante,
        texto_indice,
        alerta_limite
    ):
        indice_estatistico = round(
            self._media(
                percentual_mandante,
                percentual_visitante
            ),
            2
        )

        indice_final = self._aplicar_ajuste_contextual(
            indice_estatistico,
            contexto
        )

        nivel_confianca, recomendado = (
            self._classificar_confianca(
                indice_final,
                limite_alta,
                limite_moderada
            )
        )

        amostra_mandante = self._classificar_amostra(
            jogos_mandante
        )

        amostra_visitante = self._classificar_amostra(
            jogos_visitante
        )

        motivos = [
            texto_mandante,
            texto_visitante,
            texto_indice.format(
                indice=indice_estatistico
            ),
            (
                "O contexto específico do mercado gerou "
                f"ajuste de "
                f"{contexto['ajuste_contextual']:+.2f} pontos."
            ),
            (
                "O índice final da recomendação "
                f"foi de {indice_final:.2f}%."
            )
        ]

        alertas = self._montar_alertas_amostra(
            amostra_mandante,
            amostra_visitante
        )

        if contexto["ajuste_contextual"] < 0:
            alertas.append(
                "O contexto específico do mercado reduziu "
                "a confiança da recomendação."
            )

        if not recomendado:
            alertas.append(alerta_limite)

        return {
            "mercado": mercado,
            "recomendado": recomendado,
            "indice_estatistico": indice_estatistico,
            "ajuste_contextual": contexto[
                "ajuste_contextual"
            ],
            "indice_confianca": indice_final,
            "nivel_confianca": nivel_confianca,
            "score_contextual": contexto[
                "score_contextual"
            ],
            "percentual_mandante_casa": round(
                percentual_mandante,
                2
            ),
            "percentual_visitante_fora": round(
                percentual_visitante,
                2
            ),
            "amostra": {
                "mandante": {
                    "jogos": jogos_mandante,
                    "classificacao": amostra_mandante
                },
                "visitante": {
                    "jogos": jogos_visitante,
                    "classificacao": amostra_visitante
                }
            },
            "motivos": motivos,
            "alertas": alertas,
            "aviso": (
                "O índice de confiança é um indicador "
                "interno e não representa garantia ou "
                "probabilidade matemática do resultado."
            )
        }

    def _analisar_over15(
        self,
        dados_base,
        contexto
    ):
        mandante = dados_base["mandante"][
            "desempenho_mando"
        ]

        visitante = dados_base["visitante"][
            "desempenho_mando"
        ]

        percentual_mandante = float(
            mandante["percentual_over15"]
        )

        percentual_visitante = float(
            visitante["percentual_over15"]
        )

        jogos_mandante = int(
            mandante["jogos_analisados"]
        )

        jogos_visitante = int(
            visitante["jogos_analisados"]
        )

        return self._montar_recomendacao(
            mercado="Over 1.5 gols",
            percentual_mandante=percentual_mandante,
            percentual_visitante=percentual_visitante,
            jogos_mandante=jogos_mandante,
            jogos_visitante=jogos_visitante,
            contexto=contexto,
            limite_alta=self.LIMITE_OVER15_ALTA,
            limite_moderada=(
                self.LIMITE_OVER15_MODERADA
            ),
            texto_mandante=(
                "O mandante teve Over 1.5 em "
                f"{percentual_mandante:.1f}% dos últimos "
                f"{jogos_mandante} jogos em casa."
            ),
            texto_visitante=(
                "O visitante teve Over 1.5 em "
                f"{percentual_visitante:.1f}% dos últimos "
                f"{jogos_visitante} jogos fora."
            ),
            texto_indice=(
                "O índice estatístico combinado "
                "foi de {indice:.1f}%."
            ),
            alerta_limite=(
                "O índice final ficou abaixo do limite "
                "mínimo definido para recomendação."
            )
        )

    def _analisar_btts(
        self,
        dados_base,
        contexto
    ):
        mandante = dados_base["mandante"][
            "desempenho_mando"
        ]

        visitante = dados_base["visitante"][
            "desempenho_mando"
        ]

        percentual_mandante = float(
            mandante["percentual_btts"]
        )

        percentual_visitante = float(
            visitante["percentual_btts"]
        )

        jogos_mandante = int(
            mandante["jogos_analisados"]
        )

        jogos_visitante = int(
            visitante["jogos_analisados"]
        )

        return self._montar_recomendacao(
            mercado="BTTS - Ambos marcam",
            percentual_mandante=percentual_mandante,
            percentual_visitante=percentual_visitante,
            jogos_mandante=jogos_mandante,
            jogos_visitante=jogos_visitante,
            contexto=contexto,
            limite_alta=self.LIMITE_BTTS_ALTA,
            limite_moderada=self.LIMITE_BTTS_MODERADA,
            texto_mandante=(
                "Ambos marcaram em "
                f"{percentual_mandante:.1f}% dos últimos "
                f"{jogos_mandante} jogos do mandante em casa."
            ),
            texto_visitante=(
                "Ambos marcaram em "
                f"{percentual_visitante:.1f}% dos últimos "
                f"{jogos_visitante} jogos do visitante fora."
            ),
            texto_indice=(
                "O índice estatístico combinado de BTTS "
                "foi de {indice:.1f}%."
            ),
            alerta_limite=(
                "O índice final ficou abaixo do limite "
                "mínimo definido para recomendação de BTTS."
            )
        )

    def analisar(self):
        erro_mandante = self._validar_analise(
            self.home,
            "mandante"
        )

        if erro_mandante:
            return {
                "erro": erro_mandante
            }

        erro_visitante = self._validar_analise(
            self.away,
            "visitante"
        )

        if erro_visitante:
            return {
                "erro": erro_visitante
            }

        contexto_mandante, erro_contexto_mandante = (
            self._validar_contexto_mando(
                analise=self.home,
                mando="casa",
                identificacao="mandante"
            )
        )

        if erro_contexto_mandante:
            return {
                "erro": erro_contexto_mandante
            }

        contexto_visitante, erro_contexto_visitante = (
            self._validar_contexto_mando(
                analise=self.away,
                mando="fora",
                identificacao="visitante"
            )
        )

        if erro_contexto_visitante:
            return {
                "erro": erro_contexto_visitante
            }

        dados_base = self._montar_dados_base(
            contexto_mandante=contexto_mandante,
            contexto_visitante=contexto_visitante
        )

        contexto_over15 = self._calcular_contexto_over15(
            dados_base
        )

        contexto_btts = self._calcular_contexto_btts(
            dados_base
        )

        recomendacao_over15 = self._analisar_over15(
            dados_base,
            contexto_over15
        )

        recomendacao_btts = self._analisar_btts(
            dados_base,
            contexto_btts
        )

        return {
            "status": "Dados validados com sucesso.",
            "dados_base": dados_base,
            "analise_contextual": {
                "over15": contexto_over15,
                "btts": contexto_btts
            },
            "recomendacoes": [
                recomendacao_over15,
                recomendacao_btts
            ]
        }