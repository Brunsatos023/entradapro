"""
Testes da FixturesEngine: busca de jogos futuros reais do
Brasileirão Série A.

Usa respostas simuladas no formato real da API-Football (leagues e
fixtures) - sem precisar de internet nem de chave de API real.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import engines.fixtures_engine as fixtures_engine  # noqa: E402


RESPOSTA_LEAGUES_SIMULADA = {
    "response": [
        {
            "league": {"id": 71, "name": "Serie A", "type": "League"},
            "country": {"name": "Brazil"},
            "seasons": [
                {"year": 2025, "current": False},
                {"year": 2026, "current": True},
            ],
        },
        {
            # uma competição parecida, mas do tipo errado (Cup) -
            # a engine precisa ignorar essa e pegar só a "League"
            "league": {"id": 73, "name": "Serie A Women", "type": "Cup"},
            "country": {"name": "Brazil"},
            "seasons": [{"year": 2026, "current": True}],
        },
    ]
}

RESPOSTA_FIXTURES_SIMULADA = {
    "response": [
        {
            "fixture": {
                "id": 1111111,
                "date": "2026-08-25T20:00:00+00:00",
                "status": {"short": "NS"},
            },
            "league": {"name": "Serie A"},
            "teams": {
                "home": {"id": 127, "name": "Flamengo"},
                "away": {"id": 121, "name": "Palmeiras"},
            },
        },
        {
            "fixture": {
                "id": 1111112,
                "date": "2026-08-26T22:30:00+00:00",
                "status": {"short": "NS"},
            },
            "league": {"name": "Serie A"},
            "teams": {
                "home": {"id": 118, "name": "Corinthians"},
                "away": {"id": 120, "name": "Sao Paulo"},
            },
        },
    ]
}


class TestBuscarLigaBrasileirao(unittest.TestCase):

    def setUp(self):
        # Cada teste começa com o cache limpo, para não vazar
        # resultado de um teste para o outro.
        fixtures_engine._CACHE_LIGA.clear()

    def tearDown(self):
        fixtures_engine._CACHE_LIGA.clear()

    @patch("engines.fixtures_engine.requests.get")
    @patch.dict("os.environ", {"API_FOOTBALL_KEY": "chave-de-teste"})
    def test_encontra_a_liga_correta_e_ignora_tipo_errado(self, mock_get):
        mock_resposta = MagicMock()
        mock_resposta.status_code = 200
        mock_resposta.json.return_value = RESPOSTA_LEAGUES_SIMULADA
        mock_get.return_value = mock_resposta

        resultado = fixtures_engine.buscar_liga_brasileirao_serie_a()

        self.assertTrue(resultado["sucesso"])
        self.assertEqual(resultado["liga_id"], 71)
        self.assertEqual(resultado["temporada"], 2026)

    @patch("engines.fixtures_engine.requests.get")
    @patch.dict("os.environ", {"API_FOOTBALL_KEY": "chave-de-teste"})
    def test_usa_cache_na_segunda_chamada(self, mock_get):
        mock_resposta = MagicMock()
        mock_resposta.status_code = 200
        mock_resposta.json.return_value = RESPOSTA_LEAGUES_SIMULADA
        mock_get.return_value = mock_resposta

        fixtures_engine.buscar_liga_brasileirao_serie_a()
        fixtures_engine.buscar_liga_brasileirao_serie_a()

        self.assertEqual(mock_get.call_count, 1)

    @patch.dict("os.environ", {}, clear=True)
    def test_sem_chave_de_api_retorna_erro_claro(self):
        resultado = fixtures_engine.buscar_liga_brasileirao_serie_a()
        self.assertFalse(resultado["sucesso"])
        self.assertIn("API_FOOTBALL_KEY", resultado["mensagem"])

    @patch("engines.fixtures_engine.requests.get")
    @patch.dict("os.environ", {"API_FOOTBALL_KEY": "chave-de-teste"})
    def test_liga_nao_encontrada_retorna_erro_claro(self, mock_get):
        mock_resposta = MagicMock()
        mock_resposta.status_code = 200
        mock_resposta.json.return_value = {"response": []}
        mock_get.return_value = mock_resposta

        resultado = fixtures_engine.buscar_liga_brasileirao_serie_a()
        self.assertFalse(resultado["sucesso"])


class TestBuscarJogosFuturos(unittest.TestCase):

    def setUp(self):
        fixtures_engine._CACHE_LIGA.clear()

    def tearDown(self):
        fixtures_engine._CACHE_LIGA.clear()

    @patch("engines.fixtures_engine.requests.get")
    @patch.dict("os.environ", {"API_FOOTBALL_KEY": "chave-de-teste"})
    def test_busca_jogos_futuros_com_sucesso(self, mock_get):
        resposta_leagues = MagicMock()
        resposta_leagues.status_code = 200
        resposta_leagues.json.return_value = RESPOSTA_LEAGUES_SIMULADA

        resposta_fixtures = MagicMock()
        resposta_fixtures.status_code = 200
        resposta_fixtures.json.return_value = RESPOSTA_FIXTURES_SIMULADA

        mock_get.side_effect = [resposta_leagues, resposta_fixtures]

        resultado = fixtures_engine.buscar_jogos_futuros(dias_a_frente=7)

        self.assertTrue(resultado["sucesso"])
        self.assertEqual(resultado["total"], 2)

        primeiro_jogo = resultado["jogos"][0]
        self.assertEqual(primeiro_jogo["mandante"], "Flamengo")
        self.assertEqual(primeiro_jogo["visitante"], "Palmeiras")
        self.assertEqual(primeiro_jogo["fixture_id"], 1111111)
        self.assertEqual(primeiro_jogo["mandante_id"], 127)

    @patch("engines.fixtures_engine.requests.get")
    @patch.dict("os.environ", {"API_FOOTBALL_KEY": "chave-de-teste"})
    def test_erro_ao_buscar_liga_e_repassado(self, mock_get):
        resposta_leagues = MagicMock()
        resposta_leagues.status_code = 200
        resposta_leagues.json.return_value = {"response": []}
        mock_get.return_value = resposta_leagues

        resultado = fixtures_engine.buscar_jogos_futuros()
        self.assertFalse(resultado["sucesso"])

    @patch("engines.fixtures_engine.requests.get")
    @patch.dict("os.environ", {"API_FOOTBALL_KEY": "chave-de-teste"})
    def test_lista_vazia_de_jogos_nao_e_erro(self, mock_get):
        resposta_leagues = MagicMock()
        resposta_leagues.status_code = 200
        resposta_leagues.json.return_value = RESPOSTA_LEAGUES_SIMULADA

        resposta_fixtures = MagicMock()
        resposta_fixtures.status_code = 200
        resposta_fixtures.json.return_value = {"response": []}

        mock_get.side_effect = [resposta_leagues, resposta_fixtures]

        resultado = fixtures_engine.buscar_jogos_futuros()

        self.assertTrue(resultado["sucesso"])
        self.assertEqual(resultado["total"], 0)
        self.assertEqual(resultado["jogos"], [])

    @patch("engines.fixtures_engine.requests.get")
    @patch.dict("os.environ", {"API_FOOTBALL_KEY": "chave-de-teste"})
    def test_erro_de_rede_na_busca_de_fixtures_e_tratado(self, mock_get):
        resposta_leagues = MagicMock()
        resposta_leagues.status_code = 200
        resposta_leagues.json.return_value = RESPOSTA_LEAGUES_SIMULADA

        import requests as requests_mod

        mock_get.side_effect = [
            resposta_leagues,
            requests_mod.RequestException("timeout"),
        ]

        resultado = fixtures_engine.buscar_jogos_futuros()
        self.assertFalse(resultado["sucesso"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
