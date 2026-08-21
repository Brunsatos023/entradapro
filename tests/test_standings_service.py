"""Testes do StandingsService: tabela de classificação real
calculada a partir do dataset histórico."""

import sys
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from engines.standings_service import (  # noqa: E402
    calcular_tabela_classificacao,
)


class TestCalcularTabelaClassificacao(unittest.TestCase):

    def setUp(self):
        self.resultado = calcular_tabela_classificacao()

    def test_sucesso(self):
        self.assertTrue(self.resultado["sucesso"])

    def test_tem_20_times(self):
        self.assertEqual(len(self.resultado["tabela"]), 20)

    def test_tabela_ordenada_por_pontos_decrescente(self):
        pontos = [t["pontos"] for t in self.resultado["tabela"]]
        self.assertEqual(pontos, sorted(pontos, reverse=True))

    def test_posicoes_sequenciais_de_1_a_20(self):
        posicoes = [t["posicao"] for t in self.resultado["tabela"]]
        self.assertEqual(posicoes, list(range(1, 21)))

    def test_cada_time_tem_todos_os_campos(self):
        linha = self.resultado["tabela"][0]
        for campo in (
            "posicao", "time", "pontos", "jogos", "vitorias",
            "empates", "derrotas", "gols_marcados",
            "gols_sofridos", "saldo_gols",
        ):
            self.assertIn(campo, linha)

    def test_pontos_batem_com_vitorias_e_empates(self):
        for linha in self.resultado["tabela"]:
            pontos_esperados = (
                linha["vitorias"] * 3 + linha["empates"]
            )
            self.assertEqual(linha["pontos"], pontos_esperados)

    def test_jogos_bate_com_vitorias_empates_derrotas(self):
        for linha in self.resultado["tabela"]:
            total = (
                linha["vitorias"]
                + linha["empates"]
                + linha["derrotas"]
            )
            self.assertEqual(linha["jogos"], total)

    def test_saldo_de_gols_calculado_corretamente(self):
        for linha in self.resultado["tabela"]:
            saldo_esperado = (
                linha["gols_marcados"] - linha["gols_sofridos"]
            )
            self.assertEqual(linha["saldo_gols"], saldo_esperado)

    def test_todos_os_times_jogaram_a_mesma_quantidade(self):
        # pontos-corridos: todo mundo deve ter jogado o mesmo
        # numero de jogos no dataset completo
        jogos = {t["jogos"] for t in self.resultado["tabela"]}
        self.assertEqual(len(jogos), 1)

    def test_dataset_inexistente_lanca_erro_claro(self):
        with self.assertRaises(FileNotFoundError):
            calcular_tabela_classificacao(
                nome_arquivo_dataset="isso_nao_existe.json"
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
