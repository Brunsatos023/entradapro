"""Testes do MatchListService: lista de jogos com Score/Odd/Value
para a nova tela principal estilo Forebet/R10."""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import engines.match_list_service as mls  # noqa: E402


JOGOS_SIMULADOS = [
    {"fixture_id": 5001, "data_iso": "2026-08-25T20:00:00+00:00",
     "mandante": "Flamengo", "visitante": "Palmeiras"},
    {"fixture_id": 5002, "data_iso": "2026-08-26T18:00:00+00:00",
     "mandante": "São Paulo", "visitante": "Corinthians"},
    {"fixture_id": 5003, "data_iso": "2026-08-27T20:00:00+00:00",
     "mandante": "Real Madrid", "visitante": "Barcelona"},
]


def _odds_simuladas(fixture_id):
    tabela = {
        5001: {
            "sucesso": True,
            "mercados": {"over_1_5": {"odd": 1.75, "casa": "Bet365"}},
        },
        5002: {"sucesso": False, "mensagem": "sem odds"},
    }
    return tabela.get(fixture_id, {"sucesso": False})


class TestConstruirListaJogos(unittest.TestCase):

    @patch("engines.match_list_service.buscar_melhores_odds")
    @patch("engines.match_list_service.buscar_jogos_futuros")
    def test_inclui_jogos_com_e_sem_odd(self, mock_jogos, mock_odds):
        mock_jogos.return_value = {
            "sucesso": True, "jogos": JOGOS_SIMULADOS
        }
        mock_odds.side_effect = _odds_simuladas

        resultado = mls.construir_lista_jogos()

        self.assertTrue(resultado["sucesso"])
        mandantes = {j["mandante"] for j in resultado["jogos"]}
        self.assertIn("Flamengo", mandantes)
        self.assertIn("Sao Paulo", mandantes)

    @patch("engines.match_list_service.buscar_melhores_odds")
    @patch("engines.match_list_service.buscar_jogos_futuros")
    def test_time_fora_do_dataset_e_omitido(self, mock_jogos, mock_odds):
        mock_jogos.return_value = {
            "sucesso": True, "jogos": JOGOS_SIMULADOS
        }
        mock_odds.side_effect = _odds_simuladas

        resultado = mls.construir_lista_jogos()

        mandantes = {j["mandante"] for j in resultado["jogos"]}
        self.assertNotIn("Real Madrid", mandantes)

    @patch("engines.match_list_service.buscar_melhores_odds")
    @patch("engines.match_list_service.buscar_jogos_futuros")
    def test_jogo_com_odd_real_tem_score_odd_e_edge(
        self, mock_jogos, mock_odds
    ):
        mock_jogos.return_value = {
            "sucesso": True, "jogos": [JOGOS_SIMULADOS[0]]
        }
        mock_odds.side_effect = _odds_simuladas

        resultado = mls.construir_lista_jogos()
        jogo = resultado["jogos"][0]

        self.assertIsInstance(jogo["entradapro_score"], int)
        self.assertEqual(jogo["odd"], 1.75)
        self.assertEqual(jogo["casa_da_odd"], "Bet365")
        self.assertIsNotNone(jogo["edge"])

    @patch("engines.match_list_service.buscar_melhores_odds")
    @patch("engines.match_list_service.buscar_jogos_futuros")
    def test_jogo_sem_odd_ainda_tem_score(self, mock_jogos, mock_odds):
        mock_jogos.return_value = {
            "sucesso": True, "jogos": [JOGOS_SIMULADOS[1]]
        }
        mock_odds.side_effect = _odds_simuladas

        resultado = mls.construir_lista_jogos()
        jogo = resultado["jogos"][0]

        self.assertIsInstance(jogo["entradapro_score"], int)
        self.assertIsNone(jogo["odd"])
        self.assertIsNone(jogo["edge"])

    @patch("engines.match_list_service.buscar_jogos_futuros")
    def test_sem_jogos_retorna_lista_vazia(self, mock_jogos):
        mock_jogos.return_value = {"sucesso": True, "jogos": []}
        resultado = mls.construir_lista_jogos()
        self.assertTrue(resultado["sucesso"])
        self.assertEqual(resultado["jogos"], [])

    @patch("engines.match_list_service.buscar_jogos_futuros")
    def test_erro_na_busca_e_repassado(self, mock_jogos):
        mock_jogos.return_value = {
            "sucesso": False, "mensagem": "erro qualquer"
        }
        resultado = mls.construir_lista_jogos()
        self.assertFalse(resultado["sucesso"])

    @patch("engines.match_list_service.buscar_melhores_odds")
    @patch("engines.match_list_service.buscar_jogos_futuros")
    def test_lista_ordenada_por_data(self, mock_jogos, mock_odds):
        mock_jogos.return_value = {
            "sucesso": True, "jogos": list(reversed(JOGOS_SIMULADOS[:2]))
        }
        mock_odds.side_effect = _odds_simuladas

        resultado = mls.construir_lista_jogos()
        datas = [j["data_iso"] for j in resultado["jogos"]]
        self.assertEqual(datas, sorted(datas))


if __name__ == "__main__":
    unittest.main(verbosity=2)
