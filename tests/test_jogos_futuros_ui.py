"""Testes da lógica de agrupamento por dia e rótulos usada na
lista de jogos futuros (estilo R10 Score: Hoje/Amanhã/dia da
semana)."""

import sys
import unittest
import importlib.util
from pathlib import Path
from datetime import date

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from _streamlit_stub import instalar_streamlit_falso  # noqa: E402

instalar_streamlit_falso()

import engines.fixtures_engine  # noqa: E402,F401 - garante que o pacote existe

_spec = importlib.util.spec_from_file_location(
    "jogos_futuros_teste", SRC / "ui" / "jogos_futuros.py"
)
jf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(jf)


class TestAgruparPorDia(unittest.TestCase):

    def test_agrupa_jogos_do_mesmo_dia_juntos(self):
        jogos = [
            {"fixture_id": 1, "data_iso": "2026-08-20T20:00:00+00:00",
             "mandante": "A", "visitante": "B"},
            {"fixture_id": 2, "data_iso": "2026-08-20T18:00:00+00:00",
             "mandante": "C", "visitante": "D"},
        ]
        grupos = jf._agrupar_por_dia(jogos)

        self.assertEqual(len(grupos), 1)
        self.assertEqual(len(grupos[date(2026, 8, 20)]), 2)

    def test_dias_diferentes_ficam_em_grupos_separados(self):
        jogos = [
            {"fixture_id": 1, "data_iso": "2026-08-20T20:00:00+00:00",
             "mandante": "A", "visitante": "B"},
            {"fixture_id": 2, "data_iso": "2026-08-21T20:00:00+00:00",
             "mandante": "C", "visitante": "D"},
        ]
        grupos = jf._agrupar_por_dia(jogos)
        self.assertEqual(len(grupos), 2)

    def test_grupos_ficam_ordenados_por_data(self):
        jogos = [
            {"fixture_id": 1, "data_iso": "2026-08-25T20:00:00+00:00",
             "mandante": "A", "visitante": "B"},
            {"fixture_id": 2, "data_iso": "2026-08-20T20:00:00+00:00",
             "mandante": "C", "visitante": "D"},
        ]
        grupos = jf._agrupar_por_dia(jogos)
        datas = list(grupos.keys())
        self.assertEqual(datas, sorted(datas))

    def test_data_invalida_e_ignorada_sem_quebrar(self):
        jogos = [
            {"fixture_id": 1, "data_iso": "isso-nao-e-uma-data",
             "mandante": "A", "visitante": "B"},
        ]
        grupos = jf._agrupar_por_dia(jogos)
        self.assertEqual(grupos, {})


class TestRotuloDia(unittest.TestCase):

    def setUp(self):
        self.hoje = date(2026, 8, 20)  # quinta-feira

    def test_hoje(self):
        self.assertEqual(jf._rotulo_dia(self.hoje, self.hoje), "Hoje")

    def test_amanha(self):
        amanha = date(2026, 8, 21)
        self.assertEqual(jf._rotulo_dia(amanha, self.hoje), "Amanhã")

    def test_dia_da_semana_com_data(self):
        dia = date(2026, 8, 25)  # terca-feira
        self.assertEqual(jf._rotulo_dia(dia, self.hoje), "Terça 25/08")


if __name__ == "__main__":
    unittest.main(verbosity=2)
