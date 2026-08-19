from copy import deepcopy
from datetime import datetime, timezone

from analysis_pipeline import AnalysisPipeline


class BacktestEngine:

    def __init__(
        self,
        dataset_engine,
        odd_over15=1.40,
        odd_btts=1.70,
        janela=5,
        minimo_jogos_anteriores=5,
        stake_fixa=100.00
    ):
        self.dataset = dataset_engine
        self.odd_over15 = self._validar_numero_positivo(
            odd_over15,
            "odd_over15"
        )
        self.odd_btts = self._validar_numero_positivo(
            odd_btts,
            "odd_btts"
        )
        self.janela = janela
        self.minimo_jogos_anteriores = (
            minimo_jogos_anteriores
        )
        self.stake_fixa = self._validar_numero_positivo(
            stake_fixa,
            "stake_fixa"
        )

    def executar(self):

        estatisticas = {
            "partidas_aptas": 0,
            "partidas_processadas": 0,
            "partidas_ignoradas": 0,
            "erros_processamento": 0,

            "acertos_over15": 0,
            "erros_over15": 0,

            "acertos_btts": 0,
            "erros_btts": 0,

            "stake_fixa": self.stake_fixa,

            "apostas_over15": 0,
            "apostas_btts": 0,
            "total_apostas": 0,

            "apostas_vencedoras": 0,
            "apostas_perdedoras": 0,

            "valor_apostado": 0.0,
            "retorno_bruto": 0.0,
            "lucro_liquido": 0.0,

            "lucro_over15": 0.0,
            "lucro_btts": 0.0,

            "roi": 0.0,

            "maior_sequencia_vitorias": 0,
            "maior_sequencia_derrotas": 0,

            "historico_partidas": [],
            "curva_saldo": [],
            "detalhes_erros": [],

            "_saldo_atual": 0.0,
            "_sequencia_vitorias_atual": 0,
            "_sequencia_derrotas_atual": 0
        }

        contextos = self.dataset.iterar_partidas_backtest(
            minimo_jogos_anteriores=(
                self.minimo_jogos_anteriores
            )
        )

        for contexto in contextos:

            estatisticas["partidas_aptas"] += 1

            try:
                resultado_partida = self._processar_contexto(
                    contexto
                )

                if resultado_partida.get("ignorada"):
                    estatisticas["partidas_ignoradas"] += 1
                    continue

                self._registrar_resultado(
                    estatisticas=estatisticas,
                    resultado_partida=resultado_partida
                )

            except Exception as erro:
                estatisticas["erros_processamento"] += 1

                fixture_id = self._obter_fixture_id(
                    contexto.get(
                        "partida",
                        {}
                    )
                )

                estatisticas["detalhes_erros"].append(
                    {
                        "fixture_id": fixture_id,
                        "erro": str(erro)
                    }
                )

        return self._calcular_metricas(
            estatisticas
        )

    def _processar_contexto(
        self,
        contexto
    ):
        partida = contexto.get(
            "partida"
        )

        mandante_id = contexto.get(
            "mandante_id"
        )

        visitante_id = contexto.get(
            "visitante_id"
        )

        if not isinstance(partida, dict):
            raise TypeError(
                "O contexto não possui uma partida válida."
            )

        if mandante_id is None:
            raise ValueError(
                "O contexto não possui o ID do mandante."
            )

        if visitante_id is None:
            raise ValueError(
                "O contexto não possui o ID do visitante."
            )

        fixture_id = self._obter_fixture_id(
            partida
        )

        if fixture_id is None:
            raise ValueError(
                "A partida não possui fixture.id válido."
            )

        historico_mandante = (
            self.dataset.obter_historico_anterior(
                team_id=mandante_id,
                fixture_id=fixture_id,
                janela=None,
                somente_encerradas=True
            )
        )

        historico_visitante = (
            self.dataset.obter_historico_anterior(
                team_id=visitante_id,
                fixture_id=fixture_id,
                janela=None,
                somente_encerradas=True
            )
        )

        historico_completo = self._unir_historicos(
            historico_mandante,
            historico_visitante
        )

        if not historico_completo:
            return {
                "ignorada": True,
                "motivo": (
                    "Nenhum histórico anterior foi localizado."
                )
            }

        resultado_pipeline = AnalysisPipeline(
            partidas=historico_completo,
            id_mandante=mandante_id,
            id_visitante=visitante_id,
            odd_over15=self.odd_over15,
            odd_btts=self.odd_btts,
            janela=self.janela
        ).executar()

        if not isinstance(
            resultado_pipeline,
            dict
        ):
            raise TypeError(
                "O AnalysisPipeline não retornou um dicionário."
            )

        if resultado_pipeline.get("erro"):
            return {
                "ignorada": True,
                "motivo": resultado_pipeline["erro"]
            }

        prediction = resultado_pipeline.get(
            "resultado_prediction"
        )

        if not isinstance(prediction, dict):
            raise TypeError(
                "O pipeline não retornou "
                "'resultado_prediction'."
            )

        gols_mandante, gols_visitante = (
            self._obter_placar(
                partida
            )
        )

        over15_real = (
            gols_mandante + gols_visitante
        ) >= 2

        btts_real = (
            gols_mandante > 0
            and gols_visitante > 0
        )

        probabilidade_over15 = prediction.get(
            "mais_15"
        )

        probabilidade_btts = prediction.get(
            "ambas_marcam"
        )

        if not isinstance(
            probabilidade_over15,
            (int, float)
        ):
            raise TypeError(
                "A probabilidade de Over 1.5 não é numérica."
            )

        if not isinstance(
            probabilidade_btts,
            (int, float)
        ):
            raise TypeError(
                "A probabilidade de BTTS não é numérica."
            )

        over15_previsto = (
            probabilidade_over15 >= 50
        )

        btts_previsto = (
            probabilidade_btts >= 50
        )

        mandante_nome, visitante_nome = (
            self._obter_nomes_times(
                partida
            )
        )

        return {
            "ignorada": False,

            "fixture_id": fixture_id,
            "data": self._obter_data_texto(
                partida
            ),

            "mandante_id": mandante_id,
            "visitante_id": visitante_id,

            "mandante": mandante_nome,
            "visitante": visitante_nome,

            "gols_mandante": gols_mandante,
            "gols_visitante": gols_visitante,

            "probabilidade_over15": (
                float(probabilidade_over15)
            ),
            "probabilidade_btts": (
                float(probabilidade_btts)
            ),

            "over15_real": over15_real,
            "btts_real": btts_real,

            "over15_previsto": over15_previsto,
            "btts_previsto": btts_previsto,

            "acertou_over15": (
                over15_previsto == over15_real
            ),
            "acertou_btts": (
                btts_previsto == btts_real
            )
        }

    def _registrar_resultado(
        self,
        estatisticas,
        resultado_partida
    ):
        estatisticas["partidas_processadas"] += 1

        if resultado_partida["acertou_over15"]:
            estatisticas["acertos_over15"] += 1
        else:
            estatisticas["erros_over15"] += 1

        if resultado_partida["acertou_btts"]:
            estatisticas["acertos_btts"] += 1
        else:
            estatisticas["erros_btts"] += 1

        lucro_over15 = 0.0
        lucro_btts = 0.0

        aposta_over15_realizada = (
            resultado_partida["over15_previsto"]
        )

        aposta_btts_realizada = (
            resultado_partida["btts_previsto"]
        )

        if aposta_over15_realizada:
            lucro_over15 = self._registrar_aposta(
                estatisticas=estatisticas,
                mercado="over15",
                odd=self.odd_over15,
                venceu=resultado_partida["over15_real"],
                fixture_id=resultado_partida["fixture_id"]
            )

        if aposta_btts_realizada:
            lucro_btts = self._registrar_aposta(
                estatisticas=estatisticas,
                mercado="btts",
                odd=self.odd_btts,
                venceu=resultado_partida["btts_real"],
                fixture_id=resultado_partida["fixture_id"]
            )

        registro_partida = deepcopy(
            resultado_partida
        )

        registro_partida.update(
            {
                "odd_over15": self.odd_over15,
                "odd_btts": self.odd_btts,

                "aposta_over15_realizada": (
                    aposta_over15_realizada
                ),
                "aposta_btts_realizada": (
                    aposta_btts_realizada
                ),

                "lucro_over15": round(
                    lucro_over15,
                    2
                ),
                "lucro_btts": round(
                    lucro_btts,
                    2
                ),

                "lucro_total_partida": round(
                    lucro_over15 + lucro_btts,
                    2
                ),

                "saldo_apos_partida": round(
                    estatisticas["_saldo_atual"],
                    2
                )
            }
        )

        estatisticas["historico_partidas"].append(
            registro_partida
        )

    def _registrar_aposta(
        self,
        estatisticas,
        mercado,
        odd,
        venceu,
        fixture_id
    ):
        estatisticas["total_apostas"] += 1
        estatisticas["valor_apostado"] += (
            self.stake_fixa
        )

        if mercado == "over15":
            estatisticas["apostas_over15"] += 1
        elif mercado == "btts":
            estatisticas["apostas_btts"] += 1
        else:
            raise ValueError(
                f"Mercado desconhecido: {mercado}"
            )

        if venceu:
            retorno = self.stake_fixa * odd
            lucro = retorno - self.stake_fixa

            estatisticas["retorno_bruto"] += retorno
            estatisticas["apostas_vencedoras"] += 1

            estatisticas[
                "_sequencia_vitorias_atual"
            ] += 1

            estatisticas[
                "_sequencia_derrotas_atual"
            ] = 0

            estatisticas[
                "maior_sequencia_vitorias"
            ] = max(
                estatisticas["maior_sequencia_vitorias"],
                estatisticas["_sequencia_vitorias_atual"]
            )

        else:
            retorno = 0.0
            lucro = -self.stake_fixa

            estatisticas["apostas_perdedoras"] += 1

            estatisticas[
                "_sequencia_derrotas_atual"
            ] += 1

            estatisticas[
                "_sequencia_vitorias_atual"
            ] = 0

            estatisticas[
                "maior_sequencia_derrotas"
            ] = max(
                estatisticas["maior_sequencia_derrotas"],
                estatisticas["_sequencia_derrotas_atual"]
            )

        estatisticas["lucro_liquido"] += lucro
        estatisticas["_saldo_atual"] += lucro

        if mercado == "over15":
            estatisticas["lucro_over15"] += lucro

        if mercado == "btts":
            estatisticas["lucro_btts"] += lucro

        estatisticas["curva_saldo"].append(
            {
                "numero_aposta": (
                    estatisticas["total_apostas"]
                ),
                "fixture_id": fixture_id,
                "mercado": mercado,
                "venceu": venceu,
                "odd": odd,
                "stake": round(
                    self.stake_fixa,
                    2
                ),
                "lucro": round(
                    lucro,
                    2
                ),
                "saldo": round(
                    estatisticas["_saldo_atual"],
                    2
                )
            }
        )

        return lucro

    @staticmethod
    def _unir_historicos(
        historico_mandante,
        historico_visitante
    ):
        partidas_por_fixture = {}

        for partida in (
            historico_mandante
            + historico_visitante
        ):
            fixture_id = (
                BacktestEngine._obter_fixture_id(
                    partida
                )
            )

            if fixture_id is None:
                continue

            partidas_por_fixture[
                fixture_id
            ] = deepcopy(partida)

        partidas_unificadas = list(
            partidas_por_fixture.values()
        )

        partidas_unificadas.sort(
            key=lambda partida: (
                BacktestEngine._obter_data(
                    partida
                ),
                BacktestEngine._obter_fixture_id(
                    partida
                )
            )
        )

        return partidas_unificadas

    @staticmethod
    def _obter_fixture_id(
        partida
    ):
        fixture_id = partida.get(
            "fixture",
            {}
        ).get(
            "id"
        )

        try:
            return int(
                fixture_id
            )
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _obter_data(
        partida
    ):
        fixture = partida.get(
            "fixture",
            {}
        )

        timestamp = fixture.get(
            "timestamp"
        )

        if timestamp is not None:
            try:
                return datetime.fromtimestamp(
                    int(timestamp),
                    tz=timezone.utc
                )
            except (
                TypeError,
                ValueError,
                OSError
            ):
                pass

        data_texto = fixture.get(
            "date"
        )

        if data_texto:
            try:
                data = datetime.fromisoformat(
                    str(data_texto).replace(
                        "Z",
                        "+00:00"
                    )
                )

                if data.tzinfo is None:
                    data = data.replace(
                        tzinfo=timezone.utc
                    )

                return data.astimezone(
                    timezone.utc
                )

            except (
                TypeError,
                ValueError
            ):
                pass

        return datetime.min.replace(
            tzinfo=timezone.utc
        )

    @staticmethod
    def _obter_data_texto(
        partida
    ):
        data = BacktestEngine._obter_data(
            partida
        )

        if data == datetime.min.replace(
            tzinfo=timezone.utc
        ):
            return None

        return data.isoformat()

    @staticmethod
    def _obter_placar(
        partida
    ):
        gols = partida.get(
            "goals",
            {}
        )

        gols_mandante = gols.get(
            "home"
        )

        gols_visitante = gols.get(
            "away"
        )

        try:
            gols_mandante = int(
                gols_mandante
            )

            gols_visitante = int(
                gols_visitante
            )

        except (TypeError, ValueError) as erro:
            raise ValueError(
                "A partida não possui um placar final válido."
            ) from erro

        if (
            gols_mandante < 0
            or gols_visitante < 0
        ):
            raise ValueError(
                "O placar não pode possuir gols negativos."
            )

        return (
            gols_mandante,
            gols_visitante
        )

    @staticmethod
    def _obter_nomes_times(
        partida
    ):
        teams = partida.get(
            "teams",
            {}
        )

        mandante = teams.get(
            "home",
            {}
        ).get(
            "name"
        )

        visitante = teams.get(
            "away",
            {}
        ).get(
            "name"
        )

        return (
            mandante or "Mandante desconhecido",
            visitante or "Visitante desconhecido"
        )

    @staticmethod
    def _validar_numero_positivo(
        valor,
        nome
    ):
        if not isinstance(
            valor,
            (int, float)
        ):
            raise TypeError(
                f"{nome} precisa ser numérico."
            )

        valor = float(
            valor
        )

        if valor <= 0:
            raise ValueError(
                f"{nome} precisa ser maior que zero."
            )

        return valor

    @staticmethod
    def _calcular_metricas(
        estatisticas
    ):
        total_processadas = estatisticas[
            "partidas_processadas"
        ]

        if total_processadas == 0:
            estatisticas["taxa_acerto_over15"] = 0.0
            estatisticas["taxa_acerto_btts"] = 0.0
            estatisticas["taxa_acerto_geral"] = 0.0

        else:
            estatisticas["taxa_acerto_over15"] = round(
                estatisticas["acertos_over15"]
                * 100
                / total_processadas,
                2
            )

            estatisticas["taxa_acerto_btts"] = round(
                estatisticas["acertos_btts"]
                * 100
                / total_processadas,
                2
            )

            total_previsoes = (
                total_processadas * 2
            )

            total_acertos = (
                estatisticas["acertos_over15"]
                + estatisticas["acertos_btts"]
            )

            estatisticas["taxa_acerto_geral"] = round(
                total_acertos
                * 100
                / total_previsoes,
                2
            )

        valor_apostado = estatisticas[
            "valor_apostado"
        ]

        if valor_apostado > 0:
            estatisticas["roi"] = round(
                estatisticas["lucro_liquido"]
                * 100
                / valor_apostado,
                2
            )
        else:
            estatisticas["roi"] = 0.0

        campos_financeiros = (
            "stake_fixa",
            "valor_apostado",
            "retorno_bruto",
            "lucro_liquido",
            "lucro_over15",
            "lucro_btts"
        )

        for campo in campos_financeiros:
            estatisticas[campo] = round(
                estatisticas[campo],
                2
            )

        estatisticas.pop(
            "_saldo_atual",
            None
        )

        estatisticas.pop(
            "_sequencia_vitorias_atual",
            None
        )

        estatisticas.pop(
            "_sequencia_derrotas_atual",
            None
        )

        return estatisticas