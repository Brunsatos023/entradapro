"""Testes do utilitário de casamento de nomes de times entre
fontes diferentes (API externa vs dataset histórico local)."""

import sys
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from utils.nomes_times import (  # noqa: E402
    normalizar_nome_time,
    encontrar_time_local,
)


TIMES_LOCAIS = [
    "Atletico Goianiense", "Atletico Paranaense", "Atletico-MG", "Bahia",
    "Botafogo", "Corinthians", "Criciuma", "Cruzeiro", "Cuiaba", "Flamengo",
    "Fluminense", "Fortaleza EC", "Gremio", "Internacional", "Juventude",
    "Palmeiras", "RB Bragantino", "Sao Paulo", "Vasco DA Gama", "Vitoria",
]


class TestNormalizarNomeTime(unittest.TestCase):

    def test_remove_acentos(self):
        self.assertEqual(normalizar_nome_time("São Paulo"), "sao paulo")
        self.assertEqual(normalizar_nome_time("Grêmio"), "gremio")

    def test_nome_vazio_nao_quebra(self):
        self.assertEqual(normalizar_nome_time(None), "")
        self.assertEqual(normalizar_nome_time(""), "")


class TestEncontrarTimeLocal(unittest.TestCase):

    def test_casamento_exato_sem_acento(self):
        self.assertEqual(
            encontrar_time_local("Flamengo", TIMES_LOCAIS), "Flamengo"
        )

    def test_casamento_com_acento_da_api(self):
        self.assertEqual(
            encontrar_time_local("São Paulo", TIMES_LOCAIS), "Sao Paulo"
        )
        self.assertEqual(
            encontrar_time_local("Grêmio", TIMES_LOCAIS), "Gremio"
        )
        self.assertEqual(
            encontrar_time_local("Cuiabá", TIMES_LOCAIS), "Cuiaba"
        )
        self.assertEqual(
            encontrar_time_local("Criciúma", TIMES_LOCAIS), "Criciuma"
        )

    def test_casamento_parcial_com_sufixo(self):
        self.assertEqual(
            encontrar_time_local("Fortaleza", TIMES_LOCAIS), "Fortaleza EC"
        )
        self.assertEqual(
            encontrar_time_local("Vasco da Gama", TIMES_LOCAIS),
            "Vasco DA Gama",
        )

    def test_time_inexistente_retorna_none(self):
        self.assertIsNone(
            encontrar_time_local("Real Madrid", TIMES_LOCAIS)
        )
        self.assertIsNone(
            encontrar_time_local("Manchester City", TIMES_LOCAIS)
        )

    def test_lista_local_vazia_retorna_none(self):
        self.assertIsNone(encontrar_time_local("Flamengo", []))


if __name__ == "__main__":
    unittest.main(verbosity=2)
