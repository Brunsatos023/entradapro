"""
Testes do MultiLeagueService: vitrine de múltiplos campeonatos
(sem análise completa, só exibição + placar ao vivo).
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import engines.multi_league_service as mls  # noqa: E402


class TestBuscarVitrineCampeonatos(unittest.TestCase):

    @patch("engines.multi_league_service.buscar_jogos_futuros_liga")
    @patch("engines.multi_league_service.buscar_liga_por_nome")
    def test_agrega_jogos_de_varias_ligas(
        self, mock_buscar_liga, mock_buscar_jogos
    ):
        mock_buscar_liga.return_value = {
            "sucesso": True, "liga_id": 39, "temporada": 2026,
            "nome": "Premier League",
        }
        mock_buscar_jogos.return_value = {
            "sucesso": True,
            "jogos": [
                {"fixture_id": 1, "mandante": "Arsenal", "visitante": "Chelsea"},
            ],
            "total": 1,
        }

        resultado = mls.buscar_vitrine_campeonatos()

        self.assertTrue(resultado["sucesso"])
        self.assertEqual(
            len(resultado["campeonatos"]), len(mls.LIGAS_VITRINE)
        )

    @patch("engines.multi_league_service.buscar_jogos_futuros_liga")
    @patch("engines.multi_league_service.buscar_liga_por_nome")
    def test_liga_com_erro_e_omitida_sem_quebrar(
        self, mock_buscar_liga, mock_buscar_jogos
    ):
        mock_buscar_liga.return_value = {
            "sucesso": False, "mensagem": "liga nao encontrada",
        }

        resultado = mls.buscar_vitrine_campeonatos()

        self.assertTrue(resultado["sucesso"])
        self.assertEqual(resultado["campeonatos"], [])

    @patch("engines.multi_league_service.buscar_jogos_futuros_liga")
    @patch("engines.multi_league_service.buscar_liga_por_nome")
    def test_liga_sem_jogos_e_omitida(
        self, mock_buscar_liga, mock_buscar_jogos
    ):
        mock_buscar_liga.return_value = {
            "sucesso": True, "liga_id": 39, "temporada": 2026,
            "nome": "Premier League",
        }
        mock_buscar_jogos.return_value = {
            "sucesso": True, "jogos": [], "total": 0,
        }

        resultado = mls.buscar_vitrine_campeonatos()
        self.assertEqual(resultado["campeonatos"], [])

    @patch("engines.multi_league_service.buscar_jogos_futuros_liga")
    @patch("engines.multi_league_service.buscar_liga_por_nome")
    def test_excecao_em_uma_liga_nao_afeta_as_demais(
        self, mock_buscar_liga, mock_buscar_jogos
    ):
        respostas_por_chamada = [
            Exception("erro de rede"),
        ] + [
            {
                "sucesso": True, "liga_id": 39, "temporada": 2026,
                "nome": "Liga Qualquer",
            }
        ] * (len(mls.LIGAS_VITRINE) - 1)

        mock_buscar_liga.side_effect = respostas_por_chamada
        mock_buscar_jogos.return_value = {
            "sucesso": True,
            "jogos": [
                {"fixture_id": 1, "mandante": "A", "visitante": "B"}
            ],
            "total": 1,
        }

        resultado = mls.buscar_vitrine_campeonatos()

        self.assertTrue(resultado["sucesso"])
        # a primeira falhou (excecao), as demais devem ter funcionado
        self.assertEqual(
            len(resultado["campeonatos"]), len(mls.LIGAS_VITRINE) - 1
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
