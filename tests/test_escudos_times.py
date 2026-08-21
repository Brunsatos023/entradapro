"""Testes do utilitário de escudos (cor + sigla) dos times."""

import sys
import unittest
import importlib.util
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"

_spec = importlib.util.spec_from_file_location(
    "escudos_times_teste", SRC / "ui" / "escudos_times.py"
)
escudos = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(escudos)


class TestObterEscudo(unittest.TestCase):

    def test_time_conhecido_retorna_cores_e_sigla_definidas(self):
        cor_fundo, cor_texto, sigla = escudos.obter_escudo("Flamengo")
        self.assertEqual(sigla, "FLA")
        self.assertTrue(cor_fundo.startswith("#"))
        self.assertTrue(cor_texto.startswith("#"))

    def test_time_desconhecido_nao_quebra(self):
        cor_fundo, cor_texto, sigla = escudos.obter_escudo(
            "Time Inventado XPTO"
        )
        self.assertEqual(sigla, "TIM")
        self.assertTrue(cor_fundo.startswith("#"))

    def test_nome_vazio_nao_quebra(self):
        cor_fundo, cor_texto, sigla = escudos.obter_escudo("")
        self.assertEqual(sigla, "?")

    def test_nome_none_nao_quebra(self):
        cor_fundo, cor_texto, sigla = escudos.obter_escudo(None)
        self.assertEqual(sigla, "?")

    def test_todos_os_20_times_do_dataset_tem_escudo_proprio(self):
        times_dataset = [
            "Atletico Goianiense", "Atletico Paranaense", "Atletico-MG",
            "Bahia", "Botafogo", "Corinthians", "Criciuma", "Cruzeiro",
            "Cuiaba", "Flamengo", "Fluminense", "Fortaleza EC", "Gremio",
            "Internacional", "Juventude", "Palmeiras", "RB Bragantino",
            "Sao Paulo", "Vasco DA Gama", "Vitoria",
        ]
        for time in times_dataset:
            self.assertIn(time, escudos.ESCUDOS)


class TestHtmlEscudo(unittest.TestCase):

    def test_gera_html_valido(self):
        html = escudos.html_escudo("Palmeiras")
        self.assertIn("escudo-time", html)
        self.assertIn("PAL", html)
        self.assertIn("background:", html)


if __name__ == "__main__":
    unittest.main(verbosity=2)
