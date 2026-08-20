"""
Testes do mercado "+2,5 gols" - adicionado como informação
complementar ao +1,5 gols já existente e validado.
"""

import sys
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from data_storage import carregar_json  # noqa: E402
from engines.match_analysis_engine import MatchAnalysisEngine  # noqa: E402
from predictor import MatchPredictor  # noqa: E402


class TestPredictorMais25(unittest.TestCase):
    """Testa o cálculo isolado, sem depender do dataset completo."""

    def _dados_base(self, **overrides):
        base_casa = {
            "media_gols_marcados": 1.8,
            "media_gols_sofridos": 1.0,
            "percentual_over15": 80.0,
            "percentual_over25": 60.0,
            "percentual_btts": 55.0,
        }
        base_fora = {
            "media_gols_marcados": 1.2,
            "media_gols_sofridos": 1.3,
            "percentual_over15": 65.0,
            "percentual_over25": 45.0,
            "percentual_btts": 50.0,
        }
        base_casa.update(overrides.get("casa", {}))
        base_fora.update(overrides.get("fora", {}))
        return base_casa, base_fora

    def test_calcular_mais_25_retorna_percentual_valido(self):
        casa, fora = self._dados_base()
        score = MatchPredictor(casa, fora).calcular_mais_25()
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_ataques_fortes_geram_score_mais_alto(self):
        casa_fraco, fora_fraco = self._dados_base(
            casa={"percentual_over25": 20.0, "media_gols_marcados": 0.8},
            fora={"percentual_over25": 15.0, "media_gols_marcados": 0.7},
        )
        casa_forte, fora_forte = self._dados_base(
            casa={"percentual_over25": 80.0, "media_gols_marcados": 2.2},
            fora={"percentual_over25": 75.0, "media_gols_marcados": 2.0},
        )

        score_fraco = MatchPredictor(casa_fraco, fora_fraco).calcular_mais_25()
        score_forte = MatchPredictor(casa_forte, fora_forte).calcular_mais_25()

        self.assertGreater(score_forte, score_fraco)

    def test_gerar_previsao_inclui_mais_25(self):
        casa, fora = self._dados_base()
        resultado = MatchPredictor(casa, fora).gerar_previsao()

        self.assertIn("mais_25", resultado)
        self.assertIn("classificacao_over25", resultado)
        self.assertIn("status_estrategico_over25", resultado)
        self.assertIn("motivos_mais_25", resultado)
        self.assertIsInstance(resultado["motivos_mais_25"], list)
        self.assertGreater(len(resultado["motivos_mais_25"]), 0)

    def test_mais_15_continua_funcionando_sem_alteracao(self):
        """
        Garante que adicionar o +2,5 não bagunçou o +1,5 que já
        era usado (e validado) antes.
        """
        casa, fora = self._dados_base()
        resultado = MatchPredictor(casa, fora).gerar_previsao()

        self.assertIn("mais_15", resultado)
        self.assertIn("classificacao_over15", resultado)
        self.assertIn("status_estrategico_over15", resultado)


class TestMatchAnalysisEngineMais25(unittest.TestCase):
    """Testa a engine completa, com o dataset real do Brasileirão."""

    @classmethod
    def setUpClass(cls):
        dados = carregar_json("brasileirao_serie_a_2024.json")
        cls.partidas = dados["response"]

        times_ids = set()
        for p in cls.partidas[:60]:
            times_ids.add(p["teams"]["home"]["id"])
            times_ids.add(p["teams"]["away"]["id"])
        cls.times_ids = list(times_ids)

    def test_com_odd_over25_calcula_resultado(self):
        engine = MatchAnalysisEngine(
            partidas=self.partidas,
            id_mandante=self.times_ids[0],
            id_visitante=self.times_ids[1],
            odd_over15=1.40,
            odd_btts=1.70,
            odd_over25=2.10,
        )
        resultado = engine.analisar()

        self.assertIsNone(resultado.get("erro"))
        self.assertIsNotNone(resultado["resultado_over25"])
        self.assertIn("valor_esperado", resultado["resultado_over25"])
        self.assertIn("value_bet", resultado["resultado_over25"])
        self.assertIsNotNone(resultado["status_over25"])

    def test_sem_odd_over25_nao_calcula_e_nao_quebra(self):
        """
        Compatibilidade: quem não informar a odd de 2,5 continua
        funcionando normalmente, só sem esse dado extra.
        """
        engine = MatchAnalysisEngine(
            partidas=self.partidas,
            id_mandante=self.times_ids[0],
            id_visitante=self.times_ids[1],
            odd_over15=1.40,
            odd_btts=1.70,
        )
        resultado = engine.analisar()

        self.assertIsNone(resultado.get("erro"))
        self.assertIsNone(resultado["resultado_over25"])

    def test_over25_nao_interfere_na_recomendacao_principal(self):
        """
        Regra estratégica V1: só o +1,5 (validado por backtest)
        pode virar a recomendação principal. O +2,5 é informativo.
        """
        engine = MatchAnalysisEngine(
            partidas=self.partidas,
            id_mandante=self.times_ids[0],
            id_visitante=self.times_ids[1],
            odd_over15=1.40,
            odd_btts=1.70,
            odd_over25=2.10,
        )
        resultado = engine.analisar()

        self.assertIn(
            resultado["melhor_mercado"],
            ("Mais de 1,5 gols", "Nenhuma oportunidade validada"),
        )

    def test_comparacao_mercados_inclui_mais_25(self):
        engine = MatchAnalysisEngine(
            partidas=self.partidas,
            id_mandante=self.times_ids[0],
            id_visitante=self.times_ids[1],
            odd_over15=1.40,
            odd_btts=1.70,
            odd_over25=2.10,
        )
        resultado = engine.analisar()

        self.assertIn("mais_25", resultado["comparacao_mercados"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
