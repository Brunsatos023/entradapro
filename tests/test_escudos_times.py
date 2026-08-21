"""Testes do utilitário de escudos (imagem real + reserva)."""

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


class TestObterUrlEscudo(unittest.TestCase):

    def test_time_conhecido_retorna_url_real(self):
        url = escudos.obter_url_escudo("Flamengo")
        self.assertTrue(url.startswith("https://media.api-sports.io/"))

    def test_time_desconhecido_retorna_none(self):
        self.assertIsNone(escudos.obter_url_escudo("Time Inventado XPTO"))

    def test_todos_os_20_times_tem_url_valida(self):
        for nome, (url, *_resto) in escudos.ESCUDOS.items():
            self.assertTrue(
                url.startswith("https://"), f"{nome} sem URL valida"
            )


class TestObterEscudo(unittest.TestCase):

    def test_time_conhecido_retorna_cores_e_sigla_de_reserva(self):
        cor_fundo, cor_texto, sigla = escudos.obter_escudo("Flamengo")
        self.assertEqual(sigla, "FLA")
        self.assertTrue(cor_fundo.startswith("#"))

    def test_time_desconhecido_nao_quebra(self):
        cor_fundo, cor_texto, sigla = escudos.obter_escudo(
            "Time Inventado XPTO"
        )
        self.assertEqual(sigla, "TIM")

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

    def test_time_conhecido_usa_imagem_real(self):
        html = escudos.html_escudo("Palmeiras")
        self.assertIn("<img", html)
        self.assertIn("media.api-sports.io", html)

    def test_time_conhecido_tambem_tem_reserva_no_html(self):
        html = escudos.html_escudo("Palmeiras")
        self.assertIn("escudo-time", html)
        self.assertIn("PAL", html)

    def test_time_desconhecido_usa_so_a_reserva(self):
        html = escudos.html_escudo("Time Inventado XPTO")
        self.assertNotIn("<img", html)
        self.assertIn("escudo-time", html)

    def test_tamanho_customizado_e_aplicado(self):
        html = escudos.html_escudo("Flamengo", tamanho=46)
        self.assertIn("46px", html)


if __name__ == "__main__":
    unittest.main(verbosity=2)
