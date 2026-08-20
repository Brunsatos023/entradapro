"""
Testes da CornersEngine: análise do mercado de escanteios.

Usa respostas simuladas no formato da API-Football (sem precisar
de internet nem chave de API real).
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import engines.corners_engine as corners_engine  # noqa: E402


def _resposta_fixtures(fixture_ids):
    return {
        "response": [
            {"fixture": {"id": fid}} for fid in fixture_ids
        ]
    }


def _resposta_statistics(valor_corners):
    return {
        "response": [
            {
                "statistics": [
                    {"type": "Shots on Goal", "value": 5},
                    {"type": "Corner Kicks", "value": valor_corners},
                ]
            }
        ]
    }


class TestBuscarMediaCornersTime(unittest.TestCase):

    @patch("engines.corners_engine.requests.get")
    @patch.dict("os.environ", {"API_FOOTBALL_KEY": "chave-teste"})
    def test_calcula_media_corretamente(self, mock_get):
        resposta_fixtures = MagicMock()
        resposta_fixtures.status_code = 200
        resposta_fixtures.json.return_value = _resposta_fixtures(
            [1, 2, 3]
        )

        respostas_stats = []
        for valor in [4, 6, 5]:
            r = MagicMock()
            r.status_code = 200
            r.json.return_value = _resposta_statistics(valor)
            respostas_stats.append(r)

        mock_get.side_effect = [resposta_fixtures] + respostas_stats

        resultado = corners_engine.buscar_media_corners_time(
            127, ultimos_n=3
        )

        self.assertTrue(resultado["sucesso"])
        self.assertEqual(resultado["media_corners"], 5.0)
        self.assertEqual(resultado["jogos_analisados"], 3)

    @patch.dict("os.environ", {}, clear=True)
    def test_sem_chave_api_retorna_erro(self):
        resultado = corners_engine.buscar_media_corners_time(127)
        self.assertFalse(resultado["sucesso"])

    @patch("engines.corners_engine.requests.get")
    @patch.dict("os.environ", {"API_FOOTBALL_KEY": "chave-teste"})
    def test_sem_partidas_recentes_retorna_erro_claro(self, mock_get):
        resposta_fixtures = MagicMock()
        resposta_fixtures.status_code = 200
        resposta_fixtures.json.return_value = {"response": []}
        mock_get.return_value = resposta_fixtures

        resultado = corners_engine.buscar_media_corners_time(127)
        self.assertFalse(resultado["sucesso"])

    @patch("engines.corners_engine.requests.get")
    @patch.dict("os.environ", {"API_FOOTBALL_KEY": "chave-teste"})
    def test_estatistica_ausente_em_algumas_partidas_nao_quebra(
        self, mock_get
    ):
        resposta_fixtures = MagicMock()
        resposta_fixtures.status_code = 200
        resposta_fixtures.json.return_value = _resposta_fixtures(
            [1, 2]
        )

        resposta_com_dado = MagicMock()
        resposta_com_dado.status_code = 200
        resposta_com_dado.json.return_value = _resposta_statistics(7)

        resposta_sem_dado = MagicMock()
        resposta_sem_dado.status_code = 200
        resposta_sem_dado.json.return_value = {"response": []}

        mock_get.side_effect = [
            resposta_fixtures, resposta_com_dado, resposta_sem_dado,
        ]

        resultado = corners_engine.buscar_media_corners_time(
            127, ultimos_n=2
        )

        self.assertTrue(resultado["sucesso"])
        self.assertEqual(resultado["media_corners"], 7.0)
        self.assertEqual(resultado["jogos_analisados"], 1)


class TestCalcularProbabilidadeOverCorners(unittest.TestCase):

    def test_expectativa_igual_a_linha_fica_perto_de_50(self):
        prob = corners_engine._calcular_probabilidade_over_corners(
            5.0, 4.5, linha=9.5
        )
        self.assertEqual(prob, 50.0)

    def test_expectativa_bem_acima_da_linha_aumenta_probabilidade(self):
        prob = corners_engine._calcular_probabilidade_over_corners(
            7.0, 6.0, linha=9.5
        )
        self.assertGreater(prob, 50.0)

    def test_expectativa_bem_abaixo_da_linha_diminui_probabilidade(self):
        prob = corners_engine._calcular_probabilidade_over_corners(
            3.0, 3.0, linha=9.5
        )
        self.assertLess(prob, 50.0)

    def test_probabilidade_nunca_sai_do_intervalo_valido(self):
        prob_alta = corners_engine._calcular_probabilidade_over_corners(
            20.0, 20.0, linha=9.5
        )
        prob_baixa = corners_engine._calcular_probabilidade_over_corners(
            0.0, 0.0, linha=9.5
        )
        self.assertLessEqual(prob_alta, 95.0)
        self.assertGreaterEqual(prob_baixa, 5.0)


class TestAnalisarCorners(unittest.TestCase):

    @patch("engines.corners_engine.buscar_media_corners_time")
    def test_analise_completa_sem_odd(self, mock_busca):
        mock_busca.side_effect = [
            {"sucesso": True, "media_corners": 6.0, "jogos_analisados": 5},
            {"sucesso": True, "media_corners": 5.0, "jogos_analisados": 5},
        ]

        resultado = corners_engine.analisar_corners(127, 121)

        self.assertTrue(resultado["sucesso"])
        self.assertEqual(resultado["expectativa_total"], 11.0)
        self.assertIsNone(resultado["resultado_value"])

    @patch("engines.corners_engine.buscar_media_corners_time")
    def test_analise_completa_com_odd_calcula_value(self, mock_busca):
        mock_busca.side_effect = [
            {"sucesso": True, "media_corners": 6.5, "jogos_analisados": 5},
            {"sucesso": True, "media_corners": 5.5, "jogos_analisados": 5},
        ]

        resultado = corners_engine.analisar_corners(
            127, 121, odd_over_corners=1.90
        )

        self.assertTrue(resultado["sucesso"])
        self.assertIsNotNone(resultado["resultado_value"])
        self.assertIn("edge", resultado["resultado_value"])

    @patch("engines.corners_engine.buscar_media_corners_time")
    def test_erro_no_mandante_e_repassado_com_contexto(self, mock_busca):
        mock_busca.return_value = {
            "sucesso": False, "mensagem": "sem dados",
        }

        resultado = corners_engine.analisar_corners(127, 121)

        self.assertFalse(resultado["sucesso"])
        self.assertIn("Mandante", resultado["mensagem"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
