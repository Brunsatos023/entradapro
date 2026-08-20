"""
Testes do RiskManagementService (Etapa E do roteiro "EntradaPro
Autônomo") - detecção de sequências ruins recentes por mercado.

Lembrete importante: este serviço NUNCA bloqueia nada sozinho,
apenas gera um alerta informativo. Os testes aqui validam a
detecção, não nenhuma ação automática (porque ela não existe).
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
import risk_management_service as rms  # noqa: E402


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

    def _inserir_resultado(
        self, mercado, status, dias_atras, fixture_id
    ):
        with db.conectar_banco() as conexao:
            conexao.execute(
                """
                INSERT INTO previsoes
                (fixture_id, mandante, visitante, mercado, odd,
                 probabilidade, edge, status, verificado_em)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?,
                        datetime('now', ?))
                """,
                (
                    fixture_id, "A", "B", mercado, 1.50, 70.0, 5.0,
                    status, f"-{dias_atras} days",
                ),
            )
            conexao.commit()


class TestAvaliarSequenciaRecente(TestesComBancoTemporario):

    def test_sem_dados_nenhum_nao_gera_alerta(self):
        resultado = rms.avaliar_sequencia_recente("Mais de 1,5 gols")
        self.assertFalse(resultado["alerta_ativo"])

    def test_cinco_reds_seguidos_ativa_alerta(self):
        for i in range(5):
            self._inserir_resultado(
                "Mais de 1,5 gols", "RED", 4 - i, f"fix{i}"
            )

        resultado = rms.avaliar_sequencia_recente("Mais de 1,5 gols")

        self.assertTrue(resultado["alerta_ativo"])
        self.assertEqual(resultado["sequencia_ruim_atual"], 5)

    def test_green_recente_interrompe_a_sequencia(self):
        # 4 REDs antigos, depois um GREEN mais recente
        for i in range(4):
            self._inserir_resultado(
                "Mais de 1,5 gols", "RED", 10 - i, f"red{i}"
            )
        self._inserir_resultado(
            "Mais de 1,5 gols", "GREEN", 1, "green_recente"
        )

        resultado = rms.avaliar_sequencia_recente("Mais de 1,5 gols")

        self.assertFalse(resultado["alerta_ativo"])
        self.assertEqual(resultado["sequencia_ruim_atual"], 0)

    def test_ignora_resultados_antigos_positivos(self):
        # GREENs antigos nao "escondem" uma sequencia ruim recente
        for i in range(3):
            self._inserir_resultado(
                "Mais de 1,5 gols", "GREEN", 20 - i, f"old{i}"
            )
        for i in range(5):
            self._inserir_resultado(
                "Mais de 1,5 gols", "RED", 4 - i, f"new{i}"
            )

        resultado = rms.avaliar_sequencia_recente("Mais de 1,5 gols")
        self.assertTrue(resultado["alerta_ativo"])

    def test_mercados_diferentes_sao_avaliados_separadamente(self):
        for i in range(5):
            self._inserir_resultado(
                "Mais de 1,5 gols", "RED", 4 - i, f"m1_{i}"
            )
        for i in range(5):
            self._inserir_resultado(
                "Ambas marcam — Sim", "GREEN", 4 - i, f"m2_{i}"
            )

        r1 = rms.avaliar_sequencia_recente("Mais de 1,5 gols")
        r2 = rms.avaliar_sequencia_recente("Ambas marcam — Sim")

        self.assertTrue(r1["alerta_ativo"])
        self.assertFalse(r2["alerta_ativo"])

    def test_limite_customizado_e_respeitado(self):
        for i in range(3):
            self._inserir_resultado(
                "Mais de 1,5 gols", "RED", 2 - i, f"fix{i}"
            )

        resultado_padrao = rms.avaliar_sequencia_recente(
            "Mais de 1,5 gols", limite_sequencia_ruim=5
        )
        resultado_customizado = rms.avaliar_sequencia_recente(
            "Mais de 1,5 gols", limite_sequencia_ruim=3
        )

        self.assertFalse(resultado_padrao["alerta_ativo"])
        self.assertTrue(resultado_customizado["alerta_ativo"])


class TestStatusRiscoGeral(TestesComBancoTemporario):

    def test_sem_nenhum_alerta_tem_alerta_e_falso(self):
        status = rms.obter_status_risco_geral()
        self.assertFalse(status["tem_alerta"])
        self.assertEqual(len(status["avaliacoes"]), 3)

    def test_um_mercado_com_alerta_reflete_no_status_geral(self):
        for i in range(5):
            self._inserir_resultado(
                "Ambas marcam — Sim", "RED", 4 - i, f"fix{i}"
            )

        status = rms.obter_status_risco_geral()

        self.assertTrue(status["tem_alerta"])
        self.assertEqual(len(status["alertas_ativos"]), 1)
        self.assertEqual(
            status["alertas_ativos"][0]["mercado"], "Ambas marcam — Sim"
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
