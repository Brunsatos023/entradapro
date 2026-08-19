import sys
import unittest
from copy import deepcopy
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from engines.performance_analytics import PerformanceAnalytics


def criar_resultado_backtest():
    """
    Cria um resultado controlado com quatro apostas:
    - Over 1.5 vencedora: lucro +40
    - BTTS perdedora: lucro -100
    - Over 1.5 perdedora: lucro -100
    - BTTS vencedora: lucro +80

    Totais esperados:
    - 4 apostas
    - 2 vencedoras e 2 perdedoras
    - R$ 400 apostados
    - R$ 320 de retorno bruto
    - R$ -80 de lucro líquido
    - ROI de -20%
    """

    return {
        "partidas_aptas": 3,
        "partidas_processadas": 3,
        "partidas_ignoradas": 0,
        "erros_processamento": 0,
        "stake_fixa": 100.0,
        "apostas_over15": 2,
        "apostas_btts": 2,
        "total_apostas": 4,
        "apostas_vencedoras": 2,
        "apostas_perdedoras": 2,
        "valor_apostado": 400.0,
        "retorno_bruto": 320.0,
        "lucro_liquido": -80.0,
        "lucro_over15": -60.0,
        "lucro_btts": -20.0,
        "roi": -20.0,
        "taxa_acerto_geral": 50.0,
        "maior_sequencia_vitorias": 1,
        "maior_sequencia_derrotas": 2,
        "curva_saldo": [
            {"numero_aposta": 1, "saldo": 40.0},
            {"numero_aposta": 2, "saldo": -60.0},
            {"numero_aposta": 3, "saldo": -160.0},
            {"numero_aposta": 4, "saldo": -80.0},
        ],
        "detalhes_erros": [],
        "historico_partidas": [
            {
                "fixture_id": 101,
                "data": "2024-01-10T20:00:00+00:00",
                "mandante_id": 1,
                "visitante_id": 2,
                "mandante": "Time A",
                "visitante": "Time B",
                "gols_mandante": 2,
                "gols_visitante": 1,
                "probabilidade_over15": 72.0,
                "probabilidade_btts": 68.0,
                "odd_over15": 1.40,
                "odd_btts": 1.70,
                "over15_real": True,
                "btts_real": True,
                "aposta_over15_realizada": True,
                "aposta_btts_realizada": False,
                "lucro_over15": 40.0,
                "lucro_btts": 0.0,
            },
            {
                "fixture_id": 102,
                "data": "2024-01-11T20:00:00+00:00",
                "mandante_id": 3,
                "visitante_id": 4,
                "mandante": "Time C",
                "visitante": "Time D",
                "gols_mandante": 1,
                "gols_visitante": 0,
                "probabilidade_over15": 58.0,
                "probabilidade_btts": 65.0,
                "odd_over15": 1.45,
                "odd_btts": 1.70,
                "over15_real": False,
                "btts_real": False,
                "aposta_over15_realizada": False,
                "aposta_btts_realizada": True,
                "lucro_over15": 0.0,
                "lucro_btts": -100.0,
            },
            {
                "fixture_id": 103,
                "data": "2024-01-12T20:00:00+00:00",
                "mandante_id": 5,
                "visitante_id": 6,
                "mandante": "Time E",
                "visitante": "Time F",
                "gols_mandante": 1,
                "gols_visitante": 1,
                "probabilidade_over15": 85.0,
                "probabilidade_btts": 92.0,
                "odd_over15": 1.50,
                "odd_btts": 1.80,
                "over15_real": False,
                "btts_real": True,
                "aposta_over15_realizada": True,
                "aposta_btts_realizada": True,
                "lucro_over15": -100.0,
                "lucro_btts": 80.0,
            },
        ],
    }


def criar_resultado_sem_apostas():
    return {
        "partidas_aptas": 0,
        "partidas_processadas": 0,
        "partidas_ignoradas": 0,
        "erros_processamento": 0,
        "stake_fixa": 100.0,
        "total_apostas": 0,
        "valor_apostado": 0.0,
        "lucro_liquido": 0.0,
        "historico_partidas": [],
        "curva_saldo": [],
    }


class TestPerformanceAnalyticsEstrutura(unittest.TestCase):

    def setUp(self):
        self.resultado_backtest = criar_resultado_backtest()
        self.analytics = PerformanceAnalytics(
            self.resultado_backtest,
            quantidade_ranking=2,
        )
        self.resultado = self.analytics.executar()

    def test_executar_retorna_todos_os_grupos(self):
        self.assertEqual(
            set(self.resultado.keys()),
            {
                "geral",
                "mercados",
                "faixas_probabilidade",
                "faixas_odds",
                "ranking",
                "diagnostico",
            },
        )

    def test_entrada_original_nao_e_modificada(self):
        original = criar_resultado_backtest()
        entrada = deepcopy(original)

        PerformanceAnalytics(entrada).executar()

        self.assertEqual(entrada, original)

    def test_normaliza_apenas_apostas_realizadas(self):
        self.assertEqual(len(self.analytics.apostas), 4)

        mercados = [
            aposta["mercado"]
            for aposta in self.analytics.apostas
        ]

        self.assertEqual(
            mercados,
            ["over15", "btts", "btts", "over15"],
        )

    def test_numera_apostas_em_ordem_cronologica(self):
        numeros = [
            aposta["numero_aposta"]
            for aposta in self.analytics.apostas
        ]

        fixture_ids = [
            aposta["fixture_id"]
            for aposta in self.analytics.apostas
        ]

        self.assertEqual(numeros, [1, 2, 3, 4])
        self.assertEqual(fixture_ids, [101, 102, 103, 103])


class TestPerformanceAnalyticsMetricasGerais(unittest.TestCase):

    def setUp(self):
        self.resultado = PerformanceAnalytics(
            criar_resultado_backtest()
        ).executar()

    def test_metricas_gerais(self):
        geral = self.resultado["geral"]

        self.assertEqual(geral["total_apostas"], 4)
        self.assertEqual(geral["apostas_vencedoras"], 2)
        self.assertEqual(geral["apostas_perdedoras"], 2)
        self.assertEqual(geral["taxa_acerto"], 50.0)
        self.assertEqual(geral["valor_apostado"], 400.0)
        self.assertEqual(geral["retorno_bruto"], 320.0)
        self.assertEqual(geral["lucro_liquido"], -80.0)
        self.assertEqual(geral["roi"], -20.0)
        self.assertEqual(geral["odd_media"], 1.60)
        self.assertEqual(geral["probabilidade_media"], 78.5)
        self.assertEqual(geral["lucro_medio_aposta"], -20.0)

    def test_dados_operacionais_do_backtest(self):
        geral = self.resultado["geral"]

        self.assertEqual(geral["partidas_processadas"], 3)
        self.assertEqual(geral["partidas_ignoradas"], 0)
        self.assertEqual(geral["erros_processamento"], 0)
        self.assertEqual(geral["stake_fixa"], 100.0)
        self.assertEqual(geral["taxa_acerto_previsoes"], 50.0)
        self.assertEqual(geral["maior_sequencia_vitorias"], 1)
        self.assertEqual(geral["maior_sequencia_derrotas"], 2)


class TestPerformanceAnalyticsMercados(unittest.TestCase):

    def setUp(self):
        self.mercados = PerformanceAnalytics(
            criar_resultado_backtest()
        ).executar()["mercados"]

    def test_mercados_disponiveis(self):
        self.assertEqual(
            set(self.mercados.keys()),
            {"over15", "btts"},
        )

    def test_metricas_over15(self):
        over15 = self.mercados["over15"]

        self.assertEqual(over15["nome"], "Over 1.5")
        self.assertEqual(over15["total_apostas"], 2)
        self.assertEqual(over15["apostas_vencedoras"], 1)
        self.assertEqual(over15["apostas_perdedoras"], 1)
        self.assertEqual(over15["taxa_acerto"], 50.0)
        self.assertEqual(over15["valor_apostado"], 200.0)
        self.assertEqual(over15["retorno_bruto"], 140.0)
        self.assertEqual(over15["lucro_liquido"], -60.0)
        self.assertEqual(over15["roi"], -30.0)

    def test_metricas_btts(self):
        btts = self.mercados["btts"]

        self.assertEqual(btts["nome"], "BTTS")
        self.assertEqual(btts["total_apostas"], 2)
        self.assertEqual(btts["apostas_vencedoras"], 1)
        self.assertEqual(btts["apostas_perdedoras"], 1)
        self.assertEqual(btts["taxa_acerto"], 50.0)
        self.assertEqual(btts["valor_apostado"], 200.0)
        self.assertEqual(btts["retorno_bruto"], 180.0)
        self.assertEqual(btts["lucro_liquido"], -20.0)
        self.assertEqual(btts["roi"], -10.0)


class TestPerformanceAnalyticsFaixas(unittest.TestCase):

    def setUp(self):
        self.resultado = PerformanceAnalytics(
            criar_resultado_backtest()
        ).executar()

    def test_faixas_probabilidade(self):
        faixas = self.resultado["faixas_probabilidade"]

        self.assertEqual(faixas["50-60%"]["total_apostas"], 0)
        self.assertEqual(faixas["60-70%"]["total_apostas"], 1)
        self.assertEqual(faixas["70-80%"]["total_apostas"], 1)
        self.assertEqual(faixas["80-90%"]["total_apostas"], 1)
        self.assertEqual(faixas["90-100%"]["total_apostas"], 1)

        self.assertEqual(
            faixas["60-70%"]["probabilidade_media"],
            65.0,
        )
        self.assertEqual(
            faixas["90-100%"]["probabilidade_media"],
            92.0,
        )

    def test_faixas_odds(self):
        faixas = self.resultado["faixas_odds"]

        self.assertEqual(faixas["1.40-1.50"]["total_apostas"], 1)
        self.assertEqual(faixas["1.50-1.60"]["total_apostas"], 1)
        self.assertEqual(faixas["1.70-1.80"]["total_apostas"], 1)
        self.assertEqual(faixas["1.80-2.00"]["total_apostas"], 1)

        self.assertEqual(faixas["1.40-1.50"]["odd_media"], 1.40)
        self.assertEqual(faixas["1.80-2.00"]["odd_media"], 1.80)


class TestPerformanceAnalyticsRanking(unittest.TestCase):

    def setUp(self):
        self.ranking = PerformanceAnalytics(
            criar_resultado_backtest(),
            quantidade_ranking=2,
        ).executar()["ranking"]

    def test_limita_quantidade_do_ranking(self):
        self.assertEqual(
            len(self.ranking["melhores_apostas"]),
            2,
        )
        self.assertEqual(
            len(self.ranking["piores_apostas"]),
            2,
        )

    def test_ordena_melhores_apostas(self):
        lucros = [
            aposta["lucro"]
            for aposta in self.ranking["melhores_apostas"]
        ]

        self.assertEqual(lucros, [80.0, 40.0])

    def test_ordena_piores_apostas(self):
        lucros = [
            aposta["lucro"]
            for aposta in self.ranking["piores_apostas"]
        ]

        self.assertEqual(lucros, [-100.0, -100.0])

    def test_ranking_de_mercados_por_roi(self):
        ranking_mercados = self.ranking["mercados_por_roi"]

        self.assertEqual(ranking_mercados[0]["mercado"], "btts")
        self.assertEqual(ranking_mercados[0]["roi"], -10.0)
        self.assertEqual(ranking_mercados[1]["mercado"], "over15")
        self.assertEqual(ranking_mercados[1]["roi"], -30.0)


class TestPerformanceAnalyticsDiagnostico(unittest.TestCase):

    def test_diagnostico_consistente(self):
        diagnostico = PerformanceAnalytics(
            criar_resultado_backtest()
        ).executar()["diagnostico"]

        self.assertTrue(diagnostico["consistente"])
        self.assertTrue(
            diagnostico["consistencia_total_apostas"]
        )
        self.assertTrue(diagnostico["consistencia_lucro"])
        self.assertTrue(
            diagnostico["consistencia_valor_apostado"]
        )
        self.assertEqual(diagnostico["alertas"], [])

    def test_diagnostico_detecta_total_incorreto(self):
        entrada = criar_resultado_backtest()
        entrada["total_apostas"] = 99

        diagnostico = PerformanceAnalytics(
            entrada
        ).executar()["diagnostico"]

        self.assertFalse(diagnostico["consistente"])
        self.assertFalse(
            diagnostico["consistencia_total_apostas"]
        )
        self.assertTrue(
            any(
                "total de apostas" in alerta
                for alerta in diagnostico["alertas"]
            )
        )

    def test_diagnostico_detecta_lucro_incorreto(self):
        entrada = criar_resultado_backtest()
        entrada["lucro_liquido"] = 999.0

        diagnostico = PerformanceAnalytics(
            entrada
        ).executar()["diagnostico"]

        self.assertFalse(diagnostico["consistente"])
        self.assertFalse(diagnostico["consistencia_lucro"])

    def test_diagnostico_detecta_valor_apostado_incorreto(self):
        entrada = criar_resultado_backtest()
        entrada["valor_apostado"] = 999.0

        diagnostico = PerformanceAnalytics(
            entrada
        ).executar()["diagnostico"]

        self.assertFalse(diagnostico["consistente"])
        self.assertFalse(
            diagnostico["consistencia_valor_apostado"]
        )

    def test_sem_apostas_gera_alerta(self):
        diagnostico = PerformanceAnalytics(
            criar_resultado_sem_apostas()
        ).executar()["diagnostico"]

        self.assertTrue(diagnostico["consistente"])
        self.assertTrue(
            any(
                "Nenhuma aposta" in alerta
                for alerta in diagnostico["alertas"]
            )
        )


class TestPerformanceAnalyticsValidacoes(unittest.TestCase):

    def test_resultado_backtest_precisa_ser_dicionario(self):
        with self.assertRaises(TypeError):
            PerformanceAnalytics([])

    def test_chaves_obrigatorias(self):
        with self.assertRaises(ValueError):
            PerformanceAnalytics({})

    def test_historico_precisa_ser_lista(self):
        entrada = criar_resultado_sem_apostas()
        entrada["historico_partidas"] = {}

        with self.assertRaises(TypeError):
            PerformanceAnalytics(entrada)

    def test_quantidade_ranking_precisa_ser_inteira(self):
        with self.assertRaises(TypeError):
            PerformanceAnalytics(
                criar_resultado_backtest(),
                quantidade_ranking=2.5,
            )

    def test_quantidade_ranking_precisa_ser_positiva(self):
        with self.assertRaises(ValueError):
            PerformanceAnalytics(
                criar_resultado_backtest(),
                quantidade_ranking=0,
            )

    def test_registro_invalido_no_historico_e_ignorado(self):
        entrada = criar_resultado_sem_apostas()
        entrada["historico_partidas"] = [
            None,
            "registro inválido",
            123,
        ]

        resultado = PerformanceAnalytics(
            entrada
        ).executar()

        self.assertEqual(resultado["geral"]["total_apostas"], 0)


class TestPerformanceAnalyticsUtilitarios(unittest.TestCase):

    def test_calcular_metricas_lista_vazia(self):
        metricas = PerformanceAnalytics._calcular_metricas([])

        self.assertEqual(metricas["total_apostas"], 0)
        self.assertEqual(metricas["taxa_acerto"], 0.0)
        self.assertEqual(metricas["valor_apostado"], 0.0)
        self.assertEqual(metricas["lucro_liquido"], 0.0)
        self.assertEqual(metricas["roi"], 0.0)
        self.assertEqual(metricas["odd_media"], 0.0)
        self.assertEqual(metricas["probabilidade_media"], 0.0)
        self.assertEqual(metricas["lucro_medio_aposta"], 0.0)

    def test_calcular_media_ignora_valores_invalidos(self):
        media = PerformanceAnalytics._calcular_media(
            [1, 2.0, None, "3", True, float("inf")]
        )

        self.assertEqual(media, 1.5)

    def test_converter_numero(self):
        self.assertEqual(
            PerformanceAnalytics._converter_numero(
                1.75,
                valor_padrao=0.0,
            ),
            1.75,
        )
        self.assertEqual(
            PerformanceAnalytics._converter_numero(
                "1,75",
                valor_padrao=0.0,
            ),
            0.0,
        )
        self.assertEqual(
            PerformanceAnalytics._converter_numero(
                None,
                valor_padrao=10.0,
            ),
            10.0,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)