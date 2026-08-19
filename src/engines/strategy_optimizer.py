from __future__ import annotations

from copy import deepcopy
from math import isfinite
from typing import Any, Dict, List, Optional, Tuple


class StrategyOptimizer:
    """
    Analisa o histórico produzido pelo BacktestEngine para localizar
    faixas de probabilidade potencialmente mais eficientes.

    A engine não altera o BacktestEngine e não executa novas previsões.
    Ela apenas segmenta apostas já realizadas e calcula métricas
    estatísticas e financeiras.
    """

    MERCADOS_VALIDOS = {
        "over15",
        "btts",
    }

    NOMES_MERCADOS = {
        "over15": "Over 1.5",
        "btts": "BTTS",
    }

    FAIXAS_PROBABILIDADE_PADRAO = (
        (0.0, 50.0),
        (50.0, 55.0),
        (55.0, 60.0),
        (60.0, 65.0),
        (65.0, 70.0),
        (70.0, 75.0),
        (75.0, 80.0),
        (80.0, 85.0),
        (85.0, 90.0),
        (90.0, 100.01),
    )

    PONTOS_CORTE_PADRAO = (
        50.0,
        55.0,
        60.0,
        65.0,
        70.0,
        75.0,
        80.0,
        85.0,
        90.0,
    )

    def __init__(
        self,
        resultado_backtest: Dict[str, Any],
        minimo_apostas_recomendacao: int = 10,
        faixas_probabilidade: Optional[
            Tuple[Tuple[float, float], ...]
        ] = None,
        pontos_corte: Optional[Tuple[float, ...]] = None,
    ):
        self.resultado_backtest = (
            self._validar_resultado_backtest(
                resultado_backtest
            )
        )

        self.minimo_apostas_recomendacao = (
            self._validar_minimo_apostas(
                minimo_apostas_recomendacao
            )
        )

        self.faixas_probabilidade = (
            self._validar_faixas_probabilidade(
                faixas_probabilidade
                or self.FAIXAS_PROBABILIDADE_PADRAO
            )
        )

        self.pontos_corte = self._validar_pontos_corte(
            pontos_corte
            or self.PONTOS_CORTE_PADRAO
        )

        self.historico_partidas = deepcopy(
            self.resultado_backtest.get(
                "historico_partidas",
                [],
            )
        )

        self.apostas = self._normalizar_apostas()

    def executar(self) -> Dict[str, Any]:
        """
        Executa toda a análise de otimização.
        """

        geral = self._analisar_geral()

        mercados = {
            mercado: self._analisar_mercado(
                mercado
            )
            for mercado in sorted(
                self.MERCADOS_VALIDOS
            )
        }

        comparacao_cortes = {
            mercado: self._analisar_pontos_corte(
                mercado
            )
            for mercado in sorted(
                self.MERCADOS_VALIDOS
            )
        }

        melhores_faixas = {
            mercado: self._localizar_melhores_faixas(
                mercados[mercado][
                    "faixas_probabilidade"
                ]
            )
            for mercado in sorted(
                self.MERCADOS_VALIDOS
            )
        }

        recomendacoes = self._gerar_recomendacoes(
            mercados=mercados,
            comparacao_cortes=comparacao_cortes,
        )

        diagnostico = self._gerar_diagnostico(
            geral=geral,
            mercados=mercados,
        )

        return {
            "geral": geral,
            "mercados": mercados,
            "comparacao_pontos_corte": (
                comparacao_cortes
            ),
            "melhores_faixas": melhores_faixas,
            "recomendacoes": recomendacoes,
            "diagnostico": diagnostico,
        }

    def _normalizar_apostas(self) -> List[Dict[str, Any]]:
        """
        Converte o histórico de partidas em uma lista única de apostas.

        Apenas apostas efetivamente realizadas são consideradas.
        """

        apostas = []

        for registro in self.historico_partidas:
            if not isinstance(
                registro,
                dict,
            ):
                continue

            aposta_over15 = self._criar_aposta(
                registro=registro,
                mercado="over15",
            )

            if aposta_over15 is not None:
                apostas.append(
                    aposta_over15
                )

            aposta_btts = self._criar_aposta(
                registro=registro,
                mercado="btts",
            )

            if aposta_btts is not None:
                apostas.append(
                    aposta_btts
                )

        return apostas

    def _criar_aposta(
        self,
        registro: Dict[str, Any],
        mercado: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Normaliza uma aposta de um mercado específico.
        """

        campo_realizada = (
            f"aposta_{mercado}_realizada"
        )

        if not registro.get(
            campo_realizada,
            False,
        ):
            return None

        probabilidade = self._converter_numero(
            registro.get(
                f"probabilidade_{mercado}"
            )
        )

        odd = self._converter_numero(
            registro.get(
                f"odd_{mercado}"
            )
        )

        lucro = self._converter_numero(
            registro.get(
                f"lucro_{mercado}"
            )
        )

        stake = self._converter_numero(
            self.resultado_backtest.get(
                "stake_fixa",
                0.0,
            )
        )

        if (
            probabilidade is None
            or odd is None
            or lucro is None
            or stake is None
        ):
            return None

        if stake <= 0 or odd <= 0:
            return None

        campo_resultado_real = (
            "over15_real"
            if mercado == "over15"
            else "btts_real"
        )

        venceu = bool(
            registro.get(
                campo_resultado_real,
                False,
            )
        )

        retorno_bruto = (
            stake + lucro
            if lucro > 0
            else 0.0
        )

        return {
            "fixture_id": registro.get(
                "fixture_id"
            ),
            "data": registro.get(
                "data"
            ),
            "mandante": registro.get(
                "mandante"
            ),
            "visitante": registro.get(
                "visitante"
            ),
            "mercado": mercado,
            "mercado_nome": (
                self.NOMES_MERCADOS[
                    mercado
                ]
            ),
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

    def _analisar_geral(self) -> Dict[str, Any]:
        """
        Calcula métricas considerando todos os mercados.
        """

        metricas = self._calcular_metricas(
            self.apostas
        )

        metricas["total_partidas_historico"] = len(
            self.historico_partidas
        )

        metricas["mercados_analisados"] = sorted(
            self.MERCADOS_VALIDOS
        )

        return metricas

    def _analisar_mercado(
        self,
        mercado: str,
    ) -> Dict[str, Any]:
        """
        Analisa um mercado separadamente.
        """

        apostas_mercado = [
            aposta
            for aposta in self.apostas
            if aposta["mercado"] == mercado
        ]

        metricas = self._calcular_metricas(
            apostas_mercado
        )

        faixas = self._analisar_faixas(
            apostas_mercado
        )

        return {
            "mercado": mercado,
            "nome": self.NOMES_MERCADOS[
                mercado
            ],
            **metricas,
            "faixas_probabilidade": faixas,
        }

    def _analisar_faixas(
        self,
        apostas: List[Dict[str, Any]],
    ) -> Dict[str, Dict[str, Any]]:
        """
        Divide as apostas pelas faixas de probabilidade.
        """

        resultado = {}

        for inicio, fim in self.faixas_probabilidade:
            apostas_faixa = [
                aposta
                for aposta in apostas
                if (
                    aposta["probabilidade"] >= inicio
                    and aposta["probabilidade"] < fim
                )
            ]

            nome_faixa = self._formatar_faixa(
                inicio=inicio,
                fim=fim,
            )

            metricas = self._calcular_metricas(
                apostas_faixa
            )

            resultado[nome_faixa] = {
                "probabilidade_minima": inicio,
                "probabilidade_maxima": (
                    None
                    if fim > 100
                    else fim
                ),
                **metricas,
                "amostra_suficiente": (
                    metricas["total_apostas"]
                    >= self.minimo_apostas_recomendacao
                ),
            }

        return resultado

    def _analisar_pontos_corte(
        self,
        mercado: str,
    ) -> List[Dict[str, Any]]:
        """
        Simula o desempenho utilizando probabilidades mínimas diferentes.

        Exemplo:
        - probabilidade mínima de 60%;
        - probabilidade mínima de 65%;
        - probabilidade mínima de 70%.
        """

        apostas_mercado = [
            aposta
            for aposta in self.apostas
            if aposta["mercado"] == mercado
        ]

        resultados = []

        for ponto_corte in self.pontos_corte:
            apostas_filtradas = [
                aposta
                for aposta in apostas_mercado
                if (
                    aposta["probabilidade"]
                    >= ponto_corte
                )
            ]

            metricas = self._calcular_metricas(
                apostas_filtradas
            )

            resultados.append(
                {
                    "probabilidade_minima": (
                        ponto_corte
                    ),
                    **metricas,
                    "amostra_suficiente": (
                        metricas["total_apostas"]
                        >= self.minimo_apostas_recomendacao
                    ),
                }
            )

        resultados.sort(
            key=lambda item: (
                item["roi"],
                item["lucro_liquido"],
                item["total_apostas"],
            ),
            reverse=True,
        )

        return resultados

    def _localizar_melhores_faixas(
        self,
        faixas: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Localiza as melhores e piores faixas por ROI.
        """

        faixas_com_apostas = [
            {
                "faixa": nome,
                **metricas,
            }
            for nome, metricas in faixas.items()
            if metricas["total_apostas"] > 0
        ]

        faixas_validas = [
            faixa
            for faixa in faixas_com_apostas
            if faixa["amostra_suficiente"]
        ]

        base_ranking = (
            faixas_validas
            if faixas_validas
            else faixas_com_apostas
        )

        ordenadas = sorted(
            base_ranking,
            key=lambda item: (
                item["roi"],
                item["lucro_liquido"],
                item["total_apostas"],
            ),
            reverse=True,
        )

        melhor = (
            deepcopy(ordenadas[0])
            if ordenadas
            else None
        )

        pior = (
            deepcopy(ordenadas[-1])
            if ordenadas
            else None
        )

        lucrativas = [
            deepcopy(faixa)
            for faixa in ordenadas
            if faixa["roi"] > 0
        ]

        return {
            "melhor_faixa": melhor,
            "pior_faixa": pior,
            "faixas_lucrativas": lucrativas,
            "ranking_baseado_em_amostra_suficiente": (
                bool(faixas_validas)
            ),
        }

    def _gerar_recomendacoes(
        self,
        mercados: Dict[str, Dict[str, Any]],
        comparacao_cortes: Dict[
            str,
            List[Dict[str, Any]],
        ],
    ) -> Dict[str, Any]:
        """
        Gera recomendações objetivas com base nos resultados.

        As recomendações não alteram automaticamente os motores.
        """

        resultado = {}

        for mercado in sorted(
            self.MERCADOS_VALIDOS
        ):
            metricas_mercado = mercados[
                mercado
            ]

            cortes = comparacao_cortes[
                mercado
            ]

            cortes_validos = [
                corte
                for corte in cortes
                if corte["amostra_suficiente"]
            ]

            cortes_lucrativos = [
                corte
                for corte in cortes_validos
                if corte["roi"] > 0
            ]

            melhor_corte = (
                max(
                    cortes_lucrativos,
                    key=lambda item: (
                        item["roi"],
                        item["lucro_liquido"],
                        item["total_apostas"],
                    ),
                )
                if cortes_lucrativos
                else None
            )

            alertas = []

            if (
                metricas_mercado[
                    "total_apostas"
                ]
                < self.minimo_apostas_recomendacao
            ):
                alertas.append(
                    "A quantidade total de apostas "
                    "é insuficiente para uma "
                    "recomendação confiável."
                )

            if metricas_mercado["roi"] < 0:
                alertas.append(
                    "O mercado apresentou ROI "
                    "negativo na configuração atual."
                )

            if melhor_corte is None:
                alertas.append(
                    "Nenhum ponto de corte com "
                    "amostra suficiente apresentou "
                    "ROI positivo."
                )

            resultado[mercado] = {
                "mercado": mercado,
                "nome": self.NOMES_MERCADOS[
                    mercado
                ],
                "roi_configuracao_atual": (
                    metricas_mercado["roi"]
                ),
                "lucro_configuracao_atual": (
                    metricas_mercado[
                        "lucro_liquido"
                    ]
                ),
                "melhor_ponto_corte": (
                    deepcopy(melhor_corte)
                ),
                "alteracao_recomendada": (
                    melhor_corte is not None
                ),
                "alertas": alertas,
            }

        return resultado

    def _gerar_diagnostico(
        self,
        geral: Dict[str, Any],
        mercados: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Verifica a consistência dos dados normalizados.
        """

        total_apostas_backtest = int(
            self.resultado_backtest.get(
                "total_apostas",
                0,
            )
        )

        total_apostas_optimizer = len(
            self.apostas
        )

        lucro_backtest = round(
            self._converter_numero(
                self.resultado_backtest.get(
                    "lucro_liquido"
                ),
                valor_padrao=0.0,
            )
            or 0.0,
            2,
        )

        lucro_optimizer = round(
            geral["lucro_liquido"],
            2,
        )

        apostas_over15_backtest = int(
            self.resultado_backtest.get(
                "apostas_over15",
                0,
            )
        )

        apostas_btts_backtest = int(
            self.resultado_backtest.get(
                "apostas_btts",
                0,
            )
        )

        consistencia_total = (
            total_apostas_backtest
            == total_apostas_optimizer
        )

        consistencia_lucro = (
            abs(
                lucro_backtest
                - lucro_optimizer
            )
            <= 0.01
        )

        consistencia_over15 = (
            apostas_over15_backtest
            == mercados["over15"][
                "total_apostas"
            ]
        )

        consistencia_btts = (
            apostas_btts_backtest
            == mercados["btts"][
                "total_apostas"
            ]
        )

        alertas = []

        if not consistencia_total:
            alertas.append(
                "O total de apostas normalizadas "
                "não corresponde ao BacktestEngine."
            )

        if not consistencia_lucro:
            alertas.append(
                "O lucro calculado pelo optimizer "
                "não corresponde ao BacktestEngine."
            )

        if not consistencia_over15:
            alertas.append(
                "A quantidade de apostas Over 1.5 "
                "não corresponde ao BacktestEngine."
            )

        if not consistencia_btts:
            alertas.append(
                "A quantidade de apostas BTTS "
                "não corresponde ao BacktestEngine."
            )

        if not self.apostas:
            alertas.append(
                "Nenhuma aposta foi localizada "
                "no histórico do backtest."
            )

        consistente = all(
            (
                consistencia_total,
                consistencia_lucro,
                consistencia_over15,
                consistencia_btts,
            )
        )

        return {
            "consistente": consistente,
            "consistencia_total_apostas": (
                consistencia_total
            ),
            "consistencia_lucro": (
                consistencia_lucro
            ),
            "consistencia_apostas_over15": (
                consistencia_over15
            ),
            "consistencia_apostas_btts": (
                consistencia_btts
            ),
            "total_apostas_backtest": (
                total_apostas_backtest
            ),
            "total_apostas_optimizer": (
                total_apostas_optimizer
            ),
            "lucro_backtest": lucro_backtest,
            "lucro_optimizer": lucro_optimizer,
            "alertas": alertas,
        }

    @staticmethod
    def _calcular_metricas(
        apostas: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Calcula métricas financeiras e estatísticas.
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

        taxa_acerto = (
            round(
                apostas_vencedoras
                * 100
                / total_apostas,
                2,
            )
            if total_apostas > 0
            else 0.0
        )

        roi = (
            round(
                lucro_liquido
                * 100
                / valor_apostado,
                2,
            )
            if valor_apostado > 0
            else 0.0
        )

        odd_media = StrategyOptimizer._calcular_media(
            [
                aposta["odd"]
                for aposta in apostas
            ]
        )

        probabilidade_media = (
            StrategyOptimizer._calcular_media(
                [
                    aposta["probabilidade"]
                    for aposta in apostas
                ]
            )
        )

        lucro_medio = (
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
            "apostas_vencedoras": (
                apostas_vencedoras
            ),
            "apostas_perdedoras": (
                apostas_perdedoras
            ),
            "taxa_acerto": taxa_acerto,
            "valor_apostado": valor_apostado,
            "retorno_bruto": retorno_bruto,
            "lucro_liquido": lucro_liquido,
            "roi": roi,
            "odd_media": odd_media,
            "probabilidade_media": (
                probabilidade_media
            ),
            "lucro_medio_aposta": lucro_medio,
        }

    @staticmethod
    def _calcular_media(
        valores: List[Any],
    ) -> float:
        """
        Calcula a média ignorando valores inválidos.
        """

        numeros = []

        for valor in valores:
            numero = StrategyOptimizer._converter_numero(
                valor
            )

            if numero is not None:
                numeros.append(
                    numero
                )

        if not numeros:
            return 0.0

        return round(
            sum(numeros) / len(numeros),
            2,
        )

    @staticmethod
    def _formatar_faixa(
        inicio: float,
        fim: float,
    ) -> str:
        """
        Formata o nome visual de uma faixa.
        """

        if fim > 100:
            return f"{inicio:.0f}%+"

        return (
            f"{inicio:.0f}-"
            f"{fim:.0f}%"
        )

    @staticmethod
    def _converter_numero(
        valor: Any,
        valor_padrao: Optional[float] = None,
    ) -> Optional[float]:
        """
        Converte inteiros e floats válidos.
        """

        if isinstance(
            valor,
            bool,
        ):
            return valor_padrao

        if not isinstance(
            valor,
            (int, float),
        ):
            return valor_padrao

        numero = float(
            valor
        )

        if not isfinite(
            numero
        ):
            return valor_padrao

        return numero

    @staticmethod
    def _validar_resultado_backtest(
        resultado_backtest: Any,
    ) -> Dict[str, Any]:
        """
        Valida a entrada do BacktestEngine.
        """

        if not isinstance(
            resultado_backtest,
            dict,
        ):
            raise TypeError(
                "resultado_backtest precisa "
                "ser um dicionário."
            )

        chaves_obrigatorias = {
            "total_apostas",
            "apostas_over15",
            "apostas_btts",
            "stake_fixa",
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
                "O resultado do BacktestEngine não "
                "contém as chaves obrigatórias: "
                f"{sorted(chaves_faltantes)}"
            )

        historico = resultado_backtest.get(
            "historico_partidas"
        )

        if not isinstance(
            historico,
            list,
        ):
            raise TypeError(
                "'historico_partidas' precisa "
                "ser uma lista."
            )

        return deepcopy(
            resultado_backtest
        )

    @staticmethod
    def _validar_minimo_apostas(
        quantidade: Any,
    ) -> int:
        """
        Valida o tamanho mínimo da amostra.
        """

        if not isinstance(
            quantidade,
            int,
        ):
            raise TypeError(
                "minimo_apostas_recomendacao "
                "precisa ser inteiro."
            )

        if quantidade <= 0:
            raise ValueError(
                "minimo_apostas_recomendacao "
                "precisa ser maior que zero."
            )

        return quantidade

    @staticmethod
    def _validar_faixas_probabilidade(
        faixas: Any,
    ) -> Tuple[Tuple[float, float], ...]:
        """
        Valida as faixas de probabilidade.
        """

        if not isinstance(
            faixas,
            (tuple, list),
        ):
            raise TypeError(
                "faixas_probabilidade precisa "
                "ser uma lista ou tupla."
            )

        resultado = []

        for faixa in faixas:
            if (
                not isinstance(
                    faixa,
                    (tuple, list),
                )
                or len(faixa) != 2
            ):
                raise ValueError(
                    "Cada faixa precisa conter "
                    "um início e um fim."
                )

            inicio = StrategyOptimizer._converter_numero(
                faixa[0]
            )

            fim = StrategyOptimizer._converter_numero(
                faixa[1]
            )

            if inicio is None or fim is None:
                raise ValueError(
                    "Os limites das faixas precisam "
                    "ser números válidos."
                )

            if inicio < 0 or fim <= inicio:
                raise ValueError(
                    "As faixas de probabilidade "
                    "possuem limites inválidos."
                )

            resultado.append(
                (
                    inicio,
                    fim,
                )
            )

        return tuple(
            resultado
        )

    @staticmethod
    def _validar_pontos_corte(
        pontos: Any,
    ) -> Tuple[float, ...]:
        """
        Valida os pontos de corte utilizados nas simulações.
        """

        if not isinstance(
            pontos,
            (tuple, list),
        ):
            raise TypeError(
                "pontos_corte precisa ser "
                "uma lista ou tupla."
            )

        resultado = []

        for ponto in pontos:
            numero = StrategyOptimizer._converter_numero(
                ponto
            )

            if numero is None:
                raise ValueError(
                    "Todos os pontos de corte "
                    "precisam ser números válidos."
                )

            if numero < 0 or numero > 100:
                raise ValueError(
                    "Os pontos de corte precisam "
                    "estar entre 0 e 100."
                )

            resultado.append(
                numero
            )

        if not resultado:
            raise ValueError(
                "É necessário informar ao menos "
                "um ponto de corte."
            )

        return tuple(
            sorted(
                set(resultado)
            )
        )