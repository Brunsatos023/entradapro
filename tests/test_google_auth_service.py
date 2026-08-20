"""
Testes do google_auth_service: criar/reconhecer contas do
EntradaPro a partir de um login feito com o Google.
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
import auth  # noqa: E402
import google_auth_service as gas  # noqa: E402


class TestGoogleAuthService(unittest.TestCase):

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

    def test_primeira_vez_cria_conta_free(self):
        conta = gas.obter_ou_criar_usuario_google(
            "novo@gmail.com", "Novo Usuário"
        )
        self.assertEqual(conta["plano"], "FREE")
        self.assertEqual(conta["email"], "novo@gmail.com")

    def test_segunda_vez_reconhece_a_mesma_conta(self):
        conta1 = gas.obter_ou_criar_usuario_google(
            "repetido@gmail.com", "Repetido"
        )
        conta2 = gas.obter_ou_criar_usuario_google(
            "repetido@gmail.com", "Repetido"
        )
        self.assertEqual(conta1["id"], conta2["id"])

    def test_nao_duplica_registro_no_banco(self):
        gas.obter_ou_criar_usuario_google("x@gmail.com", "X")
        gas.obter_ou_criar_usuario_google("x@gmail.com", "X")

        with db.conectar_banco() as conexao:
            total = conexao.execute(
                "SELECT COUNT(*) as n FROM usuarios WHERE email = ?",
                ("x@gmail.com",),
            ).fetchone()["n"]

        self.assertEqual(total, 1)

    def test_gera_usuario_unico_mesmo_com_prefixo_repetido(self):
        conta1 = gas.obter_ou_criar_usuario_google(
            "joao@gmail.com", "João 1"
        )
        conta2 = gas.obter_ou_criar_usuario_google(
            "joao@hotmail.com", "João 2"
        )
        self.assertNotEqual(conta1["usuario"], conta2["usuario"])

    def test_conta_criada_pelo_google_nao_aceita_login_com_senha(self):
        conta = gas.obter_ou_criar_usuario_google(
            "semssenha@gmail.com", "Sem Senha"
        )

        resultado = auth.autenticar_usuario(
            conta["usuario"], "qualquer-coisa-123"
        )
        self.assertIsNone(resultado)

    def test_conta_criada_e_marcada_como_login_google(self):
        gas.obter_ou_criar_usuario_google(
            "marcado@gmail.com", "Marcado"
        )

        with db.conectar_banco() as conexao:
            linha = conexao.execute(
                "SELECT login_google FROM usuarios WHERE email = ?",
                ("marcado@gmail.com",),
            ).fetchone()

        self.assertEqual(int(linha["login_google"]), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
