"""
Testes do AutoTuningService (Etapa D do roteiro "EntradaPro
Autônomo") - ajuste automático de critérios com base no
desempenho real acumulado no histórico de previsões.
"""

import sys
import tempfile
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from _streamlit_stub import instalar_streamlit_falso  # noqa: E402

instalar_streamlit_falso()

import db  # noqa: E402
import auto_tuning_service as ats  # noqa: E402


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

    def _inserir_previsoes(self, quantidade_green, quantidade_red, odd=1.50):
        with db.conectar_banco() as conexao:
            for i in range(quantidade_green):
                conexao.execute(
                    """
                    INSERT INTO previsoes
                    (fixture_id, mandante, visitante, mercado,
                     odd, probabilidade, edge, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (f"g{i}", "A", "B", "Mais de 1,5 gols",
                     odd, 70.0, 5.0, "GREEN"),
                )
            for i in range(quantidade_red):
                conexao.execute(
                    """
                    INSERT INTO previsoes
                    (fixture_id, mandante, visitante, mercado,
                     odd, probabilidade, edge, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (f"r{i}", "A", "B", "Mais de 1,5 gols",
                     odd, 70.0, 5.0, "RED"),
                )
            conexao.commit()


class TestParametros(TestesComBancoTemporario):

    def test_parametro_nao_definido_retorna_padrao(self):
        valor = ats.obter_parametro("chave_que_nao_existe", 42.0)
        self.assertEqual(valor, 42.0)

    def test_definir_e_obter_parametro(self):
        ats.definir_parametro("teste_x", 55.0, "motivo de teste")
        self.assertEqual(ats.obter_parametro("teste_x", 0), 55.0)

    def test_atualizar_parametro_existente(self):
        ats.definir_parametro("teste_y", 10.0)
        ats.definir_parametro("teste_y", 20.0)
        self.assertEqual(ats.obter_parametro("teste_y", 0), 20.0)

    def test_limiar_over15_comeca_no_padrao(self):
        self.assertEqual(
            ats.obter_limiar_validacao_over15(), ats.LIMIAR_PADRAO
        )


class TestAvaliarEAjustarCriterios(TestesComBancoTemporario):

    def test_amostra_insuficiente_nao_ajusta(self):
        self._inserir_previsoes(quantidade_green=5, quantidade_red=5)

        resultado = ats.avaliar_e_ajustar_criterios(amostra_minima=20)

        self.assertFalse(resultado["ajustado"])
        self.assertEqual(
            ats.obter_limiar_validacao_over15(), ats.LIMIAR_PADRAO
        )

    def test_roi_muito_negativo_aumenta_o_limiar(self):
        # 4 green de 20 (odd 1.50) -> ROI bem negativo
        self._inserir_previsoes(quantidade_green=4, quantidade_red=16)

        resultado = ats.avaliar_e_ajustar_criterios(amostra_minima=20)

        self.assertTrue(resultado["ajustado"])
        self.assertGreater(
            resultado["limiar_novo"], resultado["limiar_anterior"]
        )

    def test_roi_muito_positivo_diminui_o_limiar(self):
        # 18 green de 20 (odd 1.50) -> ROI bem positivo
        self._inserir_previsoes(quantidade_green=18, quantidade_red=2)

        resultado = ats.avaliar_e_ajustar_criterios(amostra_minima=20)

        self.assertTrue(resultado["ajustado"])
        self.assertLess(
            resultado["limiar_novo"], resultado["limiar_anterior"]
        )

    def test_roi_neutro_nao_ajusta(self):
        # Com odd 1.50, o ponto de equilibrio e ~66,7% de acerto.
        # 13 green de 20 fica perto disso (ROI proximo de neutro).
        self._inserir_previsoes(quantidade_green=13, quantidade_red=7)

        resultado = ats.avaliar_e_ajustar_criterios(amostra_minima=20)

        self.assertFalse(resultado["ajustado"])

    def test_limiar_nao_ultrapassa_o_maximo_permitido(self):
        # forca varios ajustes seguidos para cima
        self._inserir_previsoes(quantidade_green=2, quantidade_red=18)

        for _ in range(20):
            ats.avaliar_e_ajustar_criterios(amostra_minima=20)

        self.assertLessEqual(
            ats.obter_limiar_validacao_over15(), ats.LIMIAR_MAXIMO
        )

    def test_limiar_nao_ultrapassa_o_minimo_permitido(self):
        self._inserir_previsoes(quantidade_green=19, quantidade_red=1)

        for _ in range(20):
            ats.avaliar_e_ajustar_criterios(amostra_minima=20)

        self.assertGreaterEqual(
            ats.obter_limiar_validacao_over15(), ats.LIMIAR_MINIMO
        )

    def test_ajuste_fica_registrado_no_banco_com_motivo(self):
        self._inserir_previsoes(quantidade_green=4, quantidade_red=16)
        ats.avaliar_e_ajustar_criterios(amostra_minima=20)

        with db.conectar_banco() as conexao:
            linha = conexao.execute(
                "SELECT * FROM config_dinamica WHERE chave = ?",
                (ats.CHAVE_LIMIAR_OVER15,),
            ).fetchone()

        self.assertIsNotNone(linha)
        self.assertIsNotNone(dict(linha)["motivo_ultima_atualizacao"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
