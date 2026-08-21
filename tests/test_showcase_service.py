"""Testes do ShowcaseService: vitrine de análises reais do
histórico, para a primeira tela (visível mesmo sem login)."""

import sys
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from engines.showcase_service import construir_vitrine_analises  # noqa: E402


class TestConstruirVitrineAnalises(unittest.TestCase):

    def test_retorna_a_quantidade_pedida(self):
        resultado = construir_vitrine_analises(quantidade=3)
        self.assertTrue(resultado["sucesso"])
        self.assertLessEqual(len(resultado["analises"]), 3)
        self.assertGreater(len(resultado["analises"]), 0)

    def test_cada_analise_tem_os_campos_esperados(self):
        resultado = construir_vitrine_analises(quantidade=3)
        analise = resultado["analises"][0]

        for campo in (
            "data", "hora", "mandante", "visitante", "entradapro_score",
            "probabilidade_over15", "placar_real",
        ):
            self.assertIn(campo, analise)

    def test_score_esta_no_intervalo_valido(self):
        resultado = construir_vitrine_analises(quantidade=5)
        for analise in resultado["analises"]:
            self.assertGreaterEqual(analise["entradapro_score"], 0)
            self.assertLessEqual(analise["entradapro_score"], 100)

    def test_nao_expoe_veredito_de_acerto_ou_erro(self):
        # decisao de produto: nao rotular como "bateu/nao bateu" na
        # vitrine da primeira tela - evita parecer promessa de
        # precisao. So a pagina de Resultados mostra isso.
        resultado = construir_vitrine_analises(quantidade=5)
        for analise in resultado["analises"]:
            self.assertNotIn("previsao_bateu", analise)

    def test_placar_real_vem_do_dataset_verdadeiro(self):
        resultado = construir_vitrine_analises(quantidade=5)
        for analise in resultado["analises"]:
            self.assertRegex(analise["placar_real"], r"^\d+ x \d+$")

    def test_dataset_inexistente_lanca_erro_claro(self):
        with self.assertRaises(FileNotFoundError):
            construir_vitrine_analises(
                nome_arquivo_dataset="isso_nao_existe.json"
            )

    def test_hora_esta_no_formato_hh_mm(self):
        resultado = construir_vitrine_analises(quantidade=5)
        for analise in resultado["analises"]:
            self.assertRegex(analise["hora"], r"^\d{2}:\d{2}$")


if __name__ == "__main__":
    unittest.main(verbosity=2)
