"""Testes do serviço de times favoritos."""

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
import favoritos_service as fs  # noqa: E402


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


class TestFavoritos(TestesComBancoTemporario):

    def test_time_novo_nao_e_favorito(self):
        self.assertFalse(fs.eh_favorito(1, "Flamengo"))

    def test_alternar_adiciona_favorito(self):
        resultado = fs.alternar_favorito(1, "Flamengo")
        self.assertTrue(resultado)
        self.assertTrue(fs.eh_favorito(1, "Flamengo"))

    def test_alternar_duas_vezes_remove(self):
        fs.alternar_favorito(1, "Flamengo")
        resultado = fs.alternar_favorito(1, "Flamengo")
        self.assertFalse(resultado)
        self.assertFalse(fs.eh_favorito(1, "Flamengo"))

    def test_listar_favoritos_de_um_usuario(self):
        fs.alternar_favorito(1, "Flamengo")
        fs.alternar_favorito(1, "Palmeiras")

        favoritos = fs.listar_favoritos(1)
        self.assertEqual(set(favoritos), {"Flamengo", "Palmeiras"})

    def test_favoritos_sao_isolados_por_usuario(self):
        fs.alternar_favorito(1, "Flamengo")
        fs.alternar_favorito(2, "Palmeiras")

        self.assertEqual(fs.listar_favoritos(1), ["Flamengo"])
        self.assertEqual(fs.listar_favoritos(2), ["Palmeiras"])

    def test_marcar_o_mesmo_time_duas_vezes_nao_duplica(self):
        fs.alternar_favorito(1, "Flamengo")
        fs.alternar_favorito(1, "Flamengo")  # remove
        fs.alternar_favorito(1, "Flamengo")  # adiciona de novo

        with db.conectar_banco() as conexao:
            total = conexao.execute(
                "SELECT COUNT(*) as n FROM times_favoritos "
                "WHERE usuario_id = ? AND nome_time = ?",
                (1, "Flamengo"),
            ).fetchone()["n"]

        self.assertEqual(total, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
