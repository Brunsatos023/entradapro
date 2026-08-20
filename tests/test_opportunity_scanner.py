"""
Testes do OpportunityScanner (Etapa B do roteiro "EntradaPro
Autônomo") - varredura automática combinando jogos futuros, odds
reais e análise, sem escolha manual.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import engines.opportunity_scanner as scanner  # noqa: E402


JOGOS_SIMULADOS = [
    {
        "fixture_id": 5001,
        "data_iso": "2026-08-25T20:00:00+00:00",
        "mandante": "Flamengo",
        "visitante": "Palmeiras",
    },
    {
        "fixture_id": 5002,
        "data_iso": "2026-08-26T18:00:00+00:00",
        "mandante": "São Paulo",
        "visitante": "Corinthians",
    },
    {
        "fixture_id": 5003,
        "data_iso": "2026-08-27T21:00:00+00:00",
        "mandante": "Real Madrid",
        "visitante": "Barcelona",
    },
]


def _odds_simuladas(fixture_id):
    tabela = {
        5001: {
            "sucesso": True,
            "mercados": {
                "over_1_5": {"odd": 1.75, "casa": "Bet365"},
                "btts": {"odd": 1.65, "casa": "Betano"},
            },
            "casas_encontradas": 2,
        },
        5002: {
            "sucesso": True,
            "mercados": {
                "over_1_5": {"odd": 1.30, "casa": "Betfair"},
                "btts": {"odd": 1.40, "casa": "Superbet"},
            },
            "casas_encontradas": 2,
        },
    }
    return tabela.get(fixture_id, {"sucesso": False, "mensagem": "sem odds"})


class TestOpportunityScanner(unittest.TestCase):

    @patch("engines.opportunity_scanner.buscar_melhores_odds")
    @patch("engines.opportunity_scanner.buscar_jogos_futuros")
    def test_escaneia_e_encontra_oportunidades_reais(
        self, mock_jogos, mock_odds
    ):
        mock_jogos.return_value = {
            "sucesso": True, "jogos": JOGOS_SIMULADOS
        }
        mock_odds.side_effect = _odds_simuladas

        resultado = scanner.escanear_melhores_oportunidades(
            dias_a_frente=3, limite=5
        )

        self.assertTrue(resultado["sucesso"])
        self.assertGreaterEqual(len(resultado["oportunidades"]), 1)

    @patch("engines.opportunity_scanner.buscar_melhores_odds")
    @patch("engines.opportunity_scanner.buscar_jogos_futuros")
    def test_ignora_jogo_com_time_fora_do_dataset_local(
        self, mock_jogos, mock_odds
    ):
        mock_jogos.return_value = {
            "sucesso": True, "jogos": JOGOS_SIMULADOS
        }
        mock_odds.side_effect = _odds_simuladas

        resultado = scanner.escanear_melhores_oportunidades()

        nomes_encontrados = {
            (o["mandante"], o["visitante"])
            for o in resultado["oportunidades"]
        }
        self.assertNotIn(
            ("Real Madrid", "Barcelona"), nomes_encontrados
        )

    @patch("engines.opportunity_scanner.buscar_melhores_odds")
    @patch("engines.opportunity_scanner.buscar_jogos_futuros")
    def test_casa_nomes_com_acento_da_api(self, mock_jogos, mock_odds):
        mock_jogos.return_value = {
            "sucesso": True, "jogos": JOGOS_SIMULADOS
        }
        mock_odds.side_effect = _odds_simuladas

        resultado = scanner.escanear_melhores_oportunidades()

        nomes_encontrados = {
            o["mandante"] for o in resultado["oportunidades"]
        }
        # "São Paulo" (API) deve ter virado "Sao Paulo" (dataset local)
        possui_sao_paulo = any(
            "paulo" in n.lower() for n in nomes_encontrados
        )
        if possui_sao_paulo:
            self.assertIn("Sao Paulo", nomes_encontrados)

    @patch("engines.opportunity_scanner.buscar_melhores_odds")
    @patch("engines.opportunity_scanner.buscar_jogos_futuros")
    def test_ordenado_do_maior_edge_para_o_menor(
        self, mock_jogos, mock_odds
    ):
        mock_jogos.return_value = {
            "sucesso": True, "jogos": JOGOS_SIMULADOS
        }
        mock_odds.side_effect = _odds_simuladas

        resultado = scanner.escanear_melhores_oportunidades()
        edges = [o["edge"] for o in resultado["oportunidades"]]

        self.assertEqual(edges, sorted(edges, reverse=True))

    @patch("engines.opportunity_scanner.buscar_jogos_futuros")
    def test_sem_jogos_futuros_retorna_lista_vazia_sem_erro(
        self, mock_jogos
    ):
        mock_jogos.return_value = {"sucesso": True, "jogos": []}

        resultado = scanner.escanear_melhores_oportunidades()

        self.assertTrue(resultado["sucesso"])
        self.assertEqual(resultado["oportunidades"], [])

    @patch("engines.opportunity_scanner.buscar_jogos_futuros")
    def test_erro_na_busca_de_jogos_e_repassado(self, mock_jogos):
        mock_jogos.return_value = {
            "sucesso": False, "mensagem": "sem chave de API"
        }

        resultado = scanner.escanear_melhores_oportunidades()

        self.assertFalse(resultado["sucesso"])

    @patch("engines.opportunity_scanner.buscar_melhores_odds")
    @patch("engines.opportunity_scanner.buscar_jogos_futuros")
    def test_jogo_sem_odds_disponiveis_e_ignorado_sem_quebrar(
        self, mock_jogos, mock_odds
    ):
        mock_jogos.return_value = {
            "sucesso": True,
            "jogos": [
                {
                    "fixture_id": 9999,
                    "data_iso": "2026-08-28T20:00:00+00:00",
                    "mandante": "Flamengo",
                    "visitante": "Palmeiras",
                }
            ],
        }
        mock_odds.return_value = {
            "sucesso": False, "mensagem": "nenhuma odd disponível"
        }

        resultado = scanner.escanear_melhores_oportunidades()

        self.assertTrue(resultado["sucesso"])
        self.assertEqual(resultado["oportunidades"], [])

    @patch("engines.opportunity_scanner.buscar_melhores_odds")
    @patch("engines.opportunity_scanner.buscar_jogos_futuros")
    def test_respeita_o_limite_maximo_solicitado(
        self, mock_jogos, mock_odds
    ):
        mock_jogos.return_value = {
            "sucesso": True, "jogos": JOGOS_SIMULADOS
        }
        mock_odds.side_effect = _odds_simuladas

        resultado = scanner.escanear_melhores_oportunidades(limite=1)

        self.assertLessEqual(len(resultado["oportunidades"]), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
