"""
Testes da OddsEngine: comparação de odds entre casas de apostas.

Usa respostas simuladas no MESMO FORMATO que a API-Football
realmente devolve (validado antes no script exploratório
scripts/testes_manuais/testar_odds_partida.py) - sem precisar de
internet nem de chave de API real.
"""

import sys
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from engines.odds_engine import (  # noqa: E402
    _extrair_casas_relevantes,
    melhor_odd_do_mercado,
    buscar_melhores_odds,
    CASAS_ENTRADAPRO,
)


def _bookmaker(bookmaker_id, nome, odd_over_1_5=None, odd_btts_sim=None):
    bets = []

    if odd_over_1_5 is not None:
        bets.append({
            "id": 5,
            "name": "Goals Over/Under",
            "values": [
                {"value": "Over 1.5", "odd": str(odd_over_1_5)},
                {"value": "Under 1.5", "odd": "2.10"},
            ],
        })

    if odd_btts_sim is not None:
        bets.append({
            "id": 8,
            "name": "Both Teams Score",
            "values": [
                {"value": "Yes", "odd": str(odd_btts_sim)},
                {"value": "No", "odd": "1.90"},
            ],
        })

    return {"id": bookmaker_id, "name": nome, "bets": bets}


class TestExtrairCasasRelevantes(unittest.TestCase):

    def test_mantem_so_as_casas_do_entradapro(self):
        item_odds = {
            "bookmakers": [
                _bookmaker(8, "Bet365", odd_over_1_5="1.80"),
                _bookmaker(999, "CasaDesconhecida", odd_over_1_5="5.00"),
            ]
        }
        casas = _extrair_casas_relevantes(item_odds)
        self.assertIn(8, casas)
        self.assertNotIn(999, casas)

    def test_sem_bookmakers_retorna_vazio(self):
        casas = _extrair_casas_relevantes({"bookmakers": []})
        self.assertEqual(casas, {})


class TestMelhorOddDoMercado(unittest.TestCase):

    def test_encontra_a_maior_odd_entre_varias_casas(self):
        casas = {
            8: _bookmaker(8, "Bet365", odd_over_1_5="1.75"),
            32: _bookmaker(32, "Betano", odd_over_1_5="1.90"),
            23: _bookmaker(23, "Sportingbet", odd_over_1_5="1.82"),
        }

        melhor = melhor_odd_do_mercado(
            casas, "Goals Over/Under", "Over 1.5"
        )

        self.assertEqual(melhor["casa"], "Betano")
        self.assertEqual(melhor["odd"], 1.90)

    def test_mercado_ausente_em_todas_as_casas_retorna_none(self):
        casas = {
            8: _bookmaker(8, "Bet365"),  # sem nenhum mercado
        }
        melhor = melhor_odd_do_mercado(
            casas, "Goals Over/Under", "Over 1.5"
        )
        self.assertIsNone(melhor)

    def test_ignora_casa_sem_o_mercado_especifico(self):
        casas = {
            8: _bookmaker(8, "Bet365", odd_btts_sim="1.70"),  # só tem BTTS
            32: _bookmaker(32, "Betano", odd_over_1_5="1.95"),
        }
        melhor = melhor_odd_do_mercado(
            casas, "Goals Over/Under", "Over 1.5"
        )
        self.assertEqual(melhor["casa"], "Betano")

    def test_odd_invalida_e_ignorada_sem_quebrar(self):
        bookmaker_com_erro = {
            "id": 8,
            "name": "Bet365",
            "bets": [{
                "id": 5,
                "name": "Goals Over/Under",
                "values": [{"value": "Over 1.5", "odd": "não é um número"}],
            }],
        }
        casas = {8: bookmaker_com_erro}
        melhor = melhor_odd_do_mercado(
            casas, "Goals Over/Under", "Over 1.5"
        )
        self.assertIsNone(melhor)


class TestBuscarMelhoresOdds(unittest.TestCase):
    """
    Testa a função principal, simulando a resposta da API inteira
    (sem chamar a internet de verdade).
    """

    def test_fluxo_completo_com_varias_casas(self):
        import engines.odds_engine as odds_engine

        resposta_simulada = {
            "sucesso": True,
            "dados": {
                "bookmakers": [
                    _bookmaker(
                        8, "Bet365",
                        odd_over_1_5="1.75", odd_btts_sim="1.65",
                    ),
                    _bookmaker(
                        32, "Betano",
                        odd_over_1_5="1.92", odd_btts_sim="1.80",
                    ),
                ]
            },
        }

        original = odds_engine.buscar_odds_brutas
        odds_engine.buscar_odds_brutas = lambda fixture_id: resposta_simulada
        try:
            resultado = buscar_melhores_odds(fixture_id=12345)
        finally:
            odds_engine.buscar_odds_brutas = original

        self.assertTrue(resultado["sucesso"])
        self.assertEqual(resultado["mercados"]["over_1_5"]["casa"], "Betano")
        self.assertEqual(resultado["mercados"]["over_1_5"]["odd"], 1.92)
        self.assertEqual(resultado["mercados"]["btts"]["casa"], "Betano")
        self.assertEqual(resultado["casas_encontradas"], 2)

    def test_erro_na_busca_e_repassado(self):
        import engines.odds_engine as odds_engine

        original = odds_engine.buscar_odds_brutas
        odds_engine.buscar_odds_brutas = lambda fixture_id: {
            "sucesso": False,
            "mensagem": "sem chave de API",
        }
        try:
            resultado = buscar_melhores_odds(fixture_id=1)
        finally:
            odds_engine.buscar_odds_brutas = original

        self.assertFalse(resultado["sucesso"])

    def test_lista_oficial_tem_seis_casas(self):
        self.assertEqual(len(CASAS_ENTRADAPRO), 6)


if __name__ == "__main__":
    unittest.main(verbosity=2)
