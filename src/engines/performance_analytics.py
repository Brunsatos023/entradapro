from copy import deepcopy
from math import isfinite


class PerformanceAnalytics:
    """
    Analisa os resultados gerados pelo BacktestEngine.

    O módulo não executa previsões e não modifica o backtest.
    Ele transforma o histórico de apostas em métricas de desempenho
    utilizáveis pelo Dashboard, relatórios e futuras rotinas de
    aprendizado do FootballAI.
    """

    FAIXAS_PROBABILIDADE = (
        (50.0, 60.0),
        (60.0, 70.0),
        (70.0, 80.0),
        (80.0, 90.0),
        (90.0, 100.01),
    )

    FAIXAS_ODDS = (
        (1.00, 1.30),
        (1.30, 1.40),
        (1.40, 1.50),
        (1.50, 1.60),
        (1.60, 1.70),
        (1.70, 1.80),
        (1.80, 2.00),
        (2.00, 2.50),
        (2.50, 3.00),
        (3.00, float("inf")),
    )

    MERCADOS_VALIDOS = {
        "over15",
        "btts",
    }

    NOMES_MERCADOS = {
        "over15": "Over 1.5",
        "btts": "BTTS",
    }

    def __init__(
        self,
        resultado_backtest,
        quantidade_ranking=10,
    ):
        self.resultado_backtest = self._validar_resultado_backtest(
            resultado_backtest
        )

        self.quantidade_ranking = self._validar_quantidade_ranking(
            quantidade_ranking
        )

        self.historico_partidas = deepcopy(
            self.resultado_backtest.get(
                "historico_partidas",
                [],
            )
        )

        self.curva_saldo = deepcopy(
            self.resultado_backtest.get(
                "curva_saldo",
                [],
            )
        )

        self.apostas = self._normalizar_apostas()

    def executar(self):
        """
        Executa toda a análise e retorna um dicionário consolidado.

        Cada grupo de métricas é calculado apenas uma vez.
        Os resultados prontos são reutilizados na geração do ranking.
        """

        geral = self._analisar_geral()

        mercados = self._analisar_mercados()

        faixas_probabilidade = (
            self._analisar_faixas_probabilidade()
        )

        faixas_odds = self._analisar_faixas_odds()

        ranking = self._gerar_ranking(
            mercados
        )

        diagnostico = self._gerar_diagnostico()

        return {
            "geral": geral,
            "mercados": mercados,
            "faixas_probabilidade": faixas_probabilidade,
            "faixas_odds": faixas_odds,
            "ranking": ranking,
            "diagnostico": diagnostico,
        }

    def _normalizar_apostas(self):
        """
        Converte o histórico de partidas em uma lista única de apostas.

        Cada entrada representa somente uma aposta realmente realizada
        pelo BacktestEngine.
        """

        apostas = []

        for registro in self.historico_partidas:
            if not isinstance(
                registro,
                dict,
            ):
                continue

            if registro.get(
                "aposta_over15_realizada"
            ):
                apostas.append(
                    self._criar_registro_aposta(
                        registro=registro,
                        mercado="over15",
                    )
                )

            if registro.get(
                "aposta_btts_realizada"
            ):
                apostas.append(
                    self._criar_registro_aposta(
                        registro=registro,
                        mercado="btts",
                    )
                )

        apostas.sort(
            key=lambda aposta: (
                self._valor_ordenacao_data(
                    aposta.get("data")
                ),
                aposta.get("fixture_id") or 0,
                aposta.get("mercado") or "",
            )
        )

        for numero, aposta in enumerate(
            apostas,
            start=1,
        ):
            aposta["numero_aposta"] = numero

        return apostas

    def _criar_registro_aposta(
        self,
        registro,
        mercado,
    ):
        """
        Cria uma entrada padronizada para uma aposta individual.
        """

        if mercado == "over15":
            probabilidade = registro.get(
                "probabilidade_over15"
            )

            odd = registro.get(
                "odd_over15"
            )

            venceu = bool(
                registro.get(
                    "over15_real"
                )
            )

            lucro = registro.get(
                "lucro_over15"
            )

        elif mercado == "btts":
            probabilidade = registro.get(
                "probabilidade_btts"
            )

            odd = registro.get(
                "odd_btts"
            )

            venceu = bool(
                registro.get(
                    "btts_real"
                )
            )

            lucro = registro.get(
                "lucro_btts"
            )

        else:
            raise ValueError(
                f"Mercado inválido: {mercado}"
            )

        probabilidade = self._converter_numero(
            probabilidade,
            valor_padrao=0.0,
        )

        odd = self._converter_numero(
            odd,
            valor_padrao=0.0,
        )

        lucro = self._converter_numero(
            lucro,
            valor_padrao=0.0,
        )

        stake = self._converter_numero(
            self.resultado_backtest.get(
                "stake_fixa"
            ),
            valor_padrao=0.0,
        )

        retorno_bruto = (
            stake + lucro
            if venceu
            else 0.0
        )

        return {
            "numero_aposta": None,
            "fixture_id": registro.get(
                "fixture_id"
            ),
            "data": registro.get(
                "data"
            ),
            "mandante_id": registro.get(
                "mandante_id"
            ),
            "visitante_id": registro.get(
                "visitante_id"
            ),
            "mandante": registro.get(
                "mandante"
            ),
            "visitante": registro.get(
                "visitante"
            ),
            "placar": (
                f"{registro.get('gols_mandante')} x "
                f"{registro.get('gols_visitante')}"
            ),
            "mercado": mercado,
            "mercado_nome": self.NOMES_MERCADOS[
                mercado
            ],
            "probabilidade": round(
                probabilidade,
                2,
            ),
            "odd": round(
                odd,
                2,
            ),
            "stake": round(
                stake,
                2,
            ),
            "venceu": venceu,
            "lucro": round(
                lucro,
                2,
            ),
            "retorno_bruto": round(
                retorno_bruto,
                2,
            ),
        }

    def _analisar_geral(self):
        """
        Calcula as métricas consolidadas de todas as apostas.
        """

        metricas = self._calcular_metricas(
            self.apostas
        )

        metricas.update(
            {
                "partidas_processadas": int(
                    self.resultado_backtest.get(
                        "partidas_processadas",
                        0,
                    )
                ),
                "partidas_ignoradas": int(
                    self.resultado_backtest.get(
                        "partidas_ignoradas",
                        0,
                    )
                ),
                "erros_processamento": int(
                    self.resultado_backtest.get(
                        "erros_processamento",
                        0,
                    )
                ),
                "stake_fixa": round(
                    self._converter_numero(
                        self.resultado_backtest.get(
                            "stake_fixa"
                        ),
                        valor_padrao=0.0,
                    ),
                    2,
                ),
                "taxa_acerto_previsoes": round(
                    self._converter_numero(
                        self.resultado_backtest.get(
                            "taxa_acerto_geral"
                        ),
                        valor_padrao=0.0,
                    ),
                    2,
                ),
                "maior_sequencia_vitorias": int(
                    self.resultado_backtest.get(
                        "maior_sequencia_vitorias",
                        0,
                    )
                ),
                "maior_sequencia_derrotas": int(
                    self.resultado_backtest.get(
                        "maior_sequencia_derrotas",
                        0,
                    )
                ),
            }
        )

        return metricas

    def _analisar_mercados(self):
        """
        Calcula métricas separadas para Over 1.5 e BTTS.
        """

        resultado = {}

        for mercado in (
            "over15",
            "btts",
        ):
            apostas_mercado = [
                aposta
                for aposta in self.apostas
                if aposta["mercado"] == mercado
            ]

            metricas = self._calcular_metricas(
                apostas_mercado
            )

            metricas["nome"] = self.NOMES_MERCADOS[
                mercado
            ]

            resultado[mercado] = metricas

        return resultado

    def _analisar_faixas_probabilidade(self):
        """
        Agrupa as apostas pelas faixas de probabilidade previstas.
        """

        resultado = {}

        for limite_inferior, limite_superior in (
            self.FAIXAS_PROBABILIDADE
        ):
            nome_faixa = self._nome_faixa_probabilidade(
                limite_inferior,
                limite_superior,
            )

            apostas_faixa = [
                aposta
                for aposta in self.apostas
                if (
                    aposta["probabilidade"]
                    >= limite_inferior
                    and aposta["probabilidade"]
                    < limite_superior
                )
            ]

            metricas = self._calcular_metricas(
                apostas_faixa
            )

            metricas.update(
                {
                    "limite_inferior": limite_inferior,
                    "limite_superior": (
                        100.0
                        if limite_superior > 100
                        else limite_superior
                    ),
                    "probabilidade_media": (
                        self._calcular_media(
                            [
                                aposta["probabilidade"]
                                for aposta in apostas_faixa
                            ]
                        )
                    ),
                }
            )

            resultado[nome_faixa] = metricas

        return resultado

    def _analisar_faixas_odds(self):
        """
        Agrupa as apostas pelas faixas de odds.
        """

        resultado = {}

        for limite_inferior, limite_superior in (
            self.FAIXAS_ODDS
        ):
            nome_faixa = self._nome_faixa_odd(
                limite_inferior,
                limite_superior,
            )

            apostas_faixa = [
                aposta
                for aposta in self.apostas
                if (
                    aposta["odd"] >= limite_inferior
                    and aposta["odd"] < limite_superior
                )
            ]

            metricas = self._calcular_metricas(
                apostas_faixa
            )

            metricas.update(
                {
                    "limite_inferior": limite_inferior,
                    "limite_superior": (
                        None
                        if limite_superior
                        == float("inf")
                        else limite_superior
                    ),
                    "odd_media": self._calcular_media(
                        [
                            aposta["odd"]
                            for aposta in apostas_faixa
                        ]
                    ),
                }
            )

            resultado[nome_faixa] = metricas

        return resultado

    def _gerar_ranking(
        self,
        mercados,
    ):
        """
        Gera rankings utilizando métricas já calculadas.

        O método não recalcula os mercados.
        """

        apostas_ordenadas_lucro = sorted(
            self.apostas,
            key=lambda aposta: (
                aposta["lucro"],
                aposta["probabilidade"],
            ),
            reverse=True,
        )

        apostas_ordenadas_prejuizo = sorted(
            self.apostas,
            key=lambda aposta: (
                aposta["lucro"],
                aposta["probabilidade"],
            ),
        )

        melhores = [
            deepcopy(aposta)
            for aposta in apostas_ordenadas_lucro[
                :self.quantidade_ranking
            ]
        ]

        piores = [
            deepcopy(aposta)
            for aposta in apostas_ordenadas_prejuizo[
                :self.quantidade_ranking
            ]
        ]

        ranking_mercados_roi = []

        for mercado, metricas in mercados.items():
            ranking_mercados_roi.append(
                {
                    "mercado": mercado,
                    "mercado_nome": (
                        self.NOMES_MERCADOS[
                            mercado
                        ]
                    ),
                    "total_apostas": metricas[
                        "total_apostas"
                    ],
                    "taxa_acerto": metricas[
                        "taxa_acerto"
                    ],
                    "lucro_liquido": metricas[
                        "lucro_liquido"
                    ],
                    "roi": metricas["roi"],
                }
            )

        ranking_mercados_roi.sort(
            key=lambda item: (
                item["roi"],
                item["lucro_liquido"],
            ),
            reverse=True,
        )

        return {
            "melhores_apostas": melhores,
            "piores_apostas": piores,
            "mercados_por_roi": ranking_mercados_roi,
        }

    def _gerar_diagnostico(self):
        """
        Compara os totais calculados pelo Analytics
        com os valores gerados pelo BacktestEngine.
        """

        total_apostas_backtest = int(
            self.resultado_backtest.get(
                "total_apostas",
                0,
            )
        )

        total_apostas_analytics = len(
            self.apostas
        )

        lucro_backtest = round(
            self._converter_numero(
                self.resultado_backtest.get(
                    "lucro_liquido"
                ),
                valor_padrao=0.0,
            ),
            2,
        )

        lucro_analytics = round(
            sum(
                aposta["lucro"]
                for aposta in self.apostas
            ),
            2,
        )

        valor_apostado_backtest = round(
            self._converter_numero(
                self.resultado_backtest.get(
                    "valor_apostado"
                ),
                valor_padrao=0.0,
            ),
            2,
        )

        valor_apostado_analytics = round(
            sum(
                aposta["stake"]
                for aposta in self.apostas
            ),
            2,
        )

        consistencia_total_apostas = (
            total_apostas_backtest
            == total_apostas_analytics
        )

        consistencia_lucro = (
            abs(
                lucro_backtest
                - lucro_analytics
            )
            <= 0.01
        )

        consistencia_valor_apostado = (
            abs(
                valor_apostado_backtest
                - valor_apostado_analytics
            )
            <= 0.01
        )

        alertas = []

        if not consistencia_total_apostas:
            alertas.append(
                "O total de apostas do Analytics não "
                "corresponde ao total do BacktestEngine."
            )

        if not consistencia_lucro:
            alertas.append(
                "O lucro calculado pelo Analytics não "
                "corresponde ao lucro do BacktestEngine."
            )

        if not consistencia_valor_apostado:
            alertas.append(
                "O valor apostado calculado pelo Analytics "
                "não corresponde ao BacktestEngine."
            )

        if not self.apostas:
            alertas.append(
                "Nenhuma aposta foi localizada no histórico."
            )

        return {
            "consistente": all(
                (
                    consistencia_total_apostas,
                    consistencia_lucro,
                    consistencia_valor_apostado,
                )
            ),
            "consistencia_total_apostas": (
                consistencia_total_apostas
            ),
            "consistencia_lucro": (
                consistencia_lucro
            ),
            "consistencia_valor_apostado": (
                consistencia_valor_apostado
            ),
            "total_apostas_backtest": (
                total_apostas_backtest
            ),
            "total_apostas_analytics": (
                total_apostas_analytics
            ),
            "lucro_backtest": lucro_backtest,
            "lucro_analytics": lucro_analytics,
            "valor_apostado_backtest": (
                valor_apostado_backtest
            ),
            "valor_apostado_analytics": (
                valor_apostado_analytics
            ),
            "alertas": alertas,
        }

    @staticmethod
    def _calcular_metricas(
        apostas,
    ):
        """
        Calcula as métricas financeiras e estatísticas
        de uma lista de apostas.
        """

        total_apostas = len(
            apostas
        )

        apostas_vencedoras = sum(
            1
            for aposta in apostas
            if aposta["venceu"]
        )

        apostas_perdedoras = (
            total_apostas
            - apostas_vencedoras
        )

        valor_apostado = round(
            sum(
                aposta["stake"]
                for aposta in apostas
            ),
            2,
        )

        retorno_bruto = round(
            sum(
                aposta["retorno_bruto"]
                for aposta in apostas
            ),
            2,
        )

        lucro_liquido = round(
            sum(
                aposta["lucro"]
                for aposta in apostas
            ),
            2,
        )

        if total_apostas > 0:
            taxa_acerto = round(
                apostas_vencedoras
                * 100
                / total_apostas,
                2,
            )
        else:
            taxa_acerto = 0.0

        if valor_apostado > 0:
            roi = round(
                lucro_liquido
                * 100
                / valor_apostado,
                2,
            )
        else:
            roi = 0.0

        odd_media = (
            PerformanceAnalytics._calcular_media(
                [
                    aposta["odd"]
                    for aposta in apostas
                ]
            )
        )

        probabilidade_media = (
            PerformanceAnalytics._calcular_media(
                [
                    aposta["probabilidade"]
                    for aposta in apostas
                ]
            )
        )

        lucro_medio_aposta = (
            round(
                lucro_liquido
                / total_apostas,
                2,
            )
            if total_apostas > 0
            else 0.0
        )

        return {
            "total_apostas": total_apostas,
            "apostas_vencedoras": apostas_vencedoras,
            "apostas_perdedoras": apostas_perdedoras,
            "taxa_acerto": taxa_acerto,
            "valor_apostado": valor_apostado,
            "retorno_bruto": retorno_bruto,
            "lucro_liquido": lucro_liquido,
            "roi": roi,
            "odd_media": odd_media,
            "probabilidade_media": probabilidade_media,
            "lucro_medio_aposta": lucro_medio_aposta,
        }

    @staticmethod
    def _calcular_media(
        valores,
    ):
        """
        Calcula a média apenas de valores numéricos finitos.
        """

        valores_validos = [
            float(valor)
            for valor in valores
            if isinstance(
                valor,
                (int, float),
            )
            and not isinstance(
                valor,
                bool,
            )
            and isfinite(
                float(valor)
            )
        ]

        if not valores_validos:
            return 0.0

        return round(
            sum(valores_validos)
            / len(valores_validos),
            2,
        )

    @staticmethod
    def _nome_faixa_probabilidade(
        limite_inferior,
        limite_superior,
    ):
        limite_superior_exibicao = (
            100
            if limite_superior > 100
            else int(limite_superior)
        )

        return (
            f"{int(limite_inferior)}-"
            f"{limite_superior_exibicao}%"
        )

    @staticmethod
    def _nome_faixa_odd(
        limite_inferior,
        limite_superior,
    ):
        if limite_superior == float("inf"):
            return (
                f"{limite_inferior:.2f}+"
            )

        return (
            f"{limite_inferior:.2f}-"
            f"{limite_superior:.2f}"
        )

    @staticmethod
    def _valor_ordenacao_data(
        data,
    ):
        if data is None:
            return ""

        return str(
            data
        )

    @staticmethod
    def _converter_numero(
        valor,
        valor_padrao=0.0,
    ):
        """
        Converte valores numéricos válidos para float.
        Valores inválidos retornam o valor padrão.
        """

        if isinstance(
            valor,
            bool,
        ):
            return float(
                valor
            )

        if not isinstance(
            valor,
            (int, float),
        ):
            return float(
                valor_padrao
            )

        valor = float(
            valor
        )

        if not isfinite(
            valor
        ):
            return float(
                valor_padrao
            )

        return valor

    @staticmethod
    def _validar_resultado_backtest(
        resultado_backtest,
    ):
        """
        Valida a estrutura mínima recebida do BacktestEngine.
        """

        if not isinstance(
            resultado_backtest,
            dict,
        ):
            raise TypeError(
                "resultado_backtest precisa ser "
                "um dicionário."
            )

        chaves_obrigatorias = {
            "total_apostas",
            "stake_fixa",
            "valor_apostado",
            "lucro_liquido",
            "historico_partidas",
        }

        chaves_faltantes = (
            chaves_obrigatorias
            - set(
                resultado_backtest.keys()
            )
        )

        if chaves_faltantes:
            raise ValueError(
                "O resultado do BacktestEngine não contém "
                "as chaves obrigatórias: "
                f"{sorted(chaves_faltantes)}"
            )

        historico_partidas = (
            resultado_backtest.get(
                "historico_partidas"
            )
        )

        if not isinstance(
            historico_partidas,
            list,
        ):
            raise TypeError(
                "'historico_partidas' precisa ser "
                "uma lista."
            )

        return deepcopy(
            resultado_backtest
        )

    @staticmethod
    def _validar_quantidade_ranking(
        quantidade,
    ):
        """
        Valida a quantidade de elementos dos rankings.
        """

        if not isinstance(
            quantidade,
            int,
        ):
            raise TypeError(
                "quantidade_ranking precisa ser inteira."
            )

        if quantidade <= 0:
            raise ValueError(
                "quantidade_ranking precisa ser "
                "maior que zero."
            )

        return quantidade