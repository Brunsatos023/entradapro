"""
Testes do PredictionHistoryService (Etapa C do roteiro "EntradaPro
Autônomo") - registro de previsões e conferência com resultado real.

Nunca toca no banco real (data/entradapro_users.db) - cada teste
usa seu próprio banco temporário.
"""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from _streamlit_stub import instalar_streamlit_falso  # noqa: E402

instalar_streamlit_falso()

import db  # noqa: E402
import prediction_history_service as phs  # noqa: E402


class TestesComBancoTemporario(unittest.TestCase):

    def setUp(self):
        self._arquivo_temp = tempfile.NamedTemporaryFile(
            suffix=".db", delete=False
        )
        self._arquivo_temp.close()

        self._caminho_original = db.CAMINHO_BANCO_SQLITE
        db.CAMINHO_BANCO_SQLITE = Path(self._arquivo_temp.name)

        db.inicializar_banco()

    def tearDown(self):
        db.CAMINHO_BANCO_SQLITE = self._caminho_original
        Path(self._arquivo_temp.name).unlink(missing_ok=True)


class TestRegistrarPrevisao(TestesComBancoTemporario):

    def test_registra_previsao_nova(self):
        resultado = phs.registrar_previsao(
            fixture_id=1001, mandante="Flamengo", visitante="Palmeiras",
            mercado="Mais de 1,5 gols", odd=1.75, probabilidade=82.5,
            edge=15.3, data_jogo="2026-08-20T20:00:00",
        )
        self.assertTrue(resultado["sucesso"])
        self.assertFalse(resultado["ja_existia"])

    def test_nao_duplica_mesmo_fixture_e_mercado(self):
        phs.registrar_previsao(
            fixture_id=1001, mandante="Flamengo", visitante="Palmeiras",
            mercado="Mais de 1,5 gols", odd=1.75, probabilidade=82.5,
            edge=15.3,
        )
        resultado = phs.registrar_previsao(
            fixture_id=1001, mandante="Flamengo", visitante="Palmeiras",
            mercado="Mais de 1,5 gols", odd=1.80, probabilidade=85.0,
            edge=18.0,
        )
        self.assertTrue(resultado["ja_existia"])

    def test_mesmo_fixture_mercados_diferentes_nao_e_duplicidade(self):
        r1 = phs.registrar_previsao(
            fixture_id=1002, mandante="Corinthians", visitante="Santos",
            mercado="Mais de 1,5 gols", odd=1.60, probabilidade=75.0,
            edge=10.0,
        )
        r2 = phs.registrar_previsao(
            fixture_id=1002, mandante="Corinthians", visitante="Santos",
            mercado="Ambas marcam — Sim", odd=1.90, probabilidade=60.0,
            edge=8.0,
        )
        self.assertFalse(r1["ja_existia"])
        self.assertFalse(r2["ja_existia"])
        self.assertNotEqual(r1["previsao_id"], r2["previsao_id"])


class TestVerificarPrevisoesPendentes(TestesComBancoTemporario):

    def setUp(self):
        super().setUp()
        phs.registrar_previsao(
            fixture_id=2001, mandante="Flamengo", visitante="Palmeiras",
            mercado="Mais de 1,5 gols", odd=1.75, probabilidade=82.5,
            edge=15.3,
        )

    @patch("prediction_history_service.buscar_resultado_fixture")
    def test_jogo_encerrado_com_mercado_batendo_vira_green(self, mock_busca):
        mock_busca.return_value = {
            "sucesso": True, "encerrado": True,
            "gols_casa": 2, "gols_visitante": 1,
        }
        resultado = phs.verificar_previsoes_pendentes()
        self.assertEqual(resultado["green"], 1)

    @patch("prediction_history_service.buscar_resultado_fixture")
    def test_jogo_encerrado_com_mercado_nao_batendo_vira_red(self, mock_busca):
        mock_busca.return_value = {
            "sucesso": True, "encerrado": True,
            "gols_casa": 1, "gols_visitante": 0,  # so 1 gol - nao bate +1,5
        }
        resultado = phs.verificar_previsoes_pendentes()
        self.assertEqual(resultado["red"], 1)

    @patch("prediction_history_service.buscar_resultado_fixture")
    def test_jogo_ainda_nao_aconteceu_continua_pendente(self, mock_busca):
        mock_busca.return_value = {
            "sucesso": True, "encerrado": False,
        }
        resultado = phs.verificar_previsoes_pendentes()
        self.assertEqual(resultado["verificadas"], 0)

        with db.conectar_banco() as conexao:
            linha = conexao.execute(
                "SELECT status FROM previsoes WHERE fixture_id = ?",
                ("2001",),
            ).fetchone()
        self.assertEqual(linha["status"], "PENDENTE")

    @patch("prediction_history_service.buscar_resultado_fixture")
    def test_erro_na_api_nao_quebra_a_verificacao(self, mock_busca):
        mock_busca.return_value = {
            "sucesso": False, "mensagem": "erro qualquer",
        }
        resultado = phs.verificar_previsoes_pendentes()
        self.assertTrue(resultado["sucesso"])
        self.assertEqual(resultado["verificadas"], 0)

    @patch("prediction_history_service.buscar_resultado_fixture")
    def test_rodar_duas_vezes_nao_reprocessa_o_que_ja_foi_verificado(
        self, mock_busca
    ):
        mock_busca.return_value = {
            "sucesso": True, "encerrado": True,
            "gols_casa": 2, "gols_visitante": 1,
        }
        primeira = phs.verificar_previsoes_pendentes()
        segunda = phs.verificar_previsoes_pendentes()

        self.assertEqual(primeira["verificadas"], 1)
        self.assertEqual(segunda["verificadas"], 0)


class TestEstatisticasHistorico(TestesComBancoTemporario):

    def test_sem_previsoes_conferidas_retorna_none(self):
        stats = phs.obter_estatisticas_historico()
        self.assertEqual(stats["total"], 0)
        self.assertIsNone(stats["taxa_acerto"])

    @patch("prediction_history_service.buscar_resultado_fixture")
    def test_calcula_taxa_de_acerto_correta(self, mock_busca):
        phs.registrar_previsao(
            fixture_id=3001, mandante="A", visitante="B",
            mercado="Mais de 1,5 gols", odd=1.80, probabilidade=80,
            edge=10,
        )
        phs.registrar_previsao(
            fixture_id=3002, mandante="C", visitante="D",
            mercado="Mais de 1,5 gols", odd=1.70, probabilidade=75,
            edge=8,
        )

        respostas = {
            "3001": {"sucesso": True, "encerrado": True, "gols_casa": 2, "gols_visitante": 1},
            "3002": {"sucesso": True, "encerrado": True, "gols_casa": 0, "gols_visitante": 0},
        }
        mock_busca.side_effect = lambda fid: respostas[str(fid)]

        phs.verificar_previsoes_pendentes()

        stats = phs.obter_estatisticas_historico()
        self.assertEqual(stats["total"], 2)
        self.assertEqual(stats["green"], 1)
        self.assertEqual(stats["red"], 1)
        self.assertEqual(stats["taxa_acerto"], 50.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
