"""
Testes de autenticação: cadastro, login e recuperação de senha.

IMPORTANTE: estes testes NUNCA tocam no banco de dados real
(data/entradapro_users.db). Cada teste cria seu próprio banco
temporário e apaga no final.
"""

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from _streamlit_stub import instalar_streamlit_falso  # noqa: E402

instalar_streamlit_falso()

import auth  # noqa: E402
import db  # noqa: E402


class TestesComBancoTemporario(unittest.TestCase):
    """Classe base: cria um banco SQLite temporário para cada teste."""

    def setUp(self):
        self._arquivo_temp = tempfile.NamedTemporaryFile(
            suffix=".db", delete=False
        )
        self._arquivo_temp.close()

        self._caminho_original = db.CAMINHO_BANCO_SQLITE
        db.CAMINHO_BANCO_SQLITE = Path(self._arquivo_temp.name)

        auth.inicializar_banco()

    def tearDown(self):
        db.CAMINHO_BANCO_SQLITE = self._caminho_original
        Path(self._arquivo_temp.name).unlink(missing_ok=True)


class TestCadastro(TestesComBancoTemporario):

    def test_cadastro_com_dados_validos_funciona(self):
        ok, mensagem = auth.cadastrar_usuario(
            nome="Bruno Teste",
            usuario="bruno.teste",
            email="bruno.teste@example.com",
            senha="senhaforte123",
            confirmar_senha="senhaforte123",
        )
        self.assertTrue(ok, mensagem)

    def test_cadastro_recusa_senha_curta(self):
        ok, mensagem = auth.cadastrar_usuario(
            nome="Bruno",
            usuario="bruno.curto",
            email="curto@example.com",
            senha="123",
            confirmar_senha="123",
        )
        self.assertFalse(ok)
        self.assertIn("8 caracteres", mensagem)

    def test_cadastro_recusa_senhas_diferentes(self):
        ok, mensagem = auth.cadastrar_usuario(
            nome="Bruno",
            usuario="bruno.diff",
            email="diff@example.com",
            senha="senhaforte123",
            confirmar_senha="outrasenha456",
        )
        self.assertFalse(ok)
        self.assertIn("não coincidem", mensagem)

    def test_cadastro_recusa_email_invalido(self):
        ok, mensagem = auth.cadastrar_usuario(
            nome="Bruno",
            usuario="bruno.email",
            email="nao-e-um-email",
            senha="senhaforte123",
            confirmar_senha="senhaforte123",
        )
        self.assertFalse(ok)
        self.assertIn("e-mail válido", mensagem)

    def test_cadastro_recusa_usuario_duplicado(self):
        auth.cadastrar_usuario(
            nome="Bruno",
            usuario="bruno.dup",
            email="primeiro@example.com",
            senha="senhaforte123",
            confirmar_senha="senhaforte123",
        )
        ok, mensagem = auth.cadastrar_usuario(
            nome="Bruno Segundo",
            usuario="bruno.dup",
            email="segundo@example.com",
            senha="senhaforte123",
            confirmar_senha="senhaforte123",
        )
        self.assertFalse(ok)
        self.assertIn("em uso", mensagem)

    def test_cadastro_recusa_email_duplicado(self):
        auth.cadastrar_usuario(
            nome="Bruno",
            usuario="usuario.um",
            email="mesmo@example.com",
            senha="senhaforte123",
            confirmar_senha="senhaforte123",
        )
        ok, mensagem = auth.cadastrar_usuario(
            nome="Bruno Outro",
            usuario="usuario.dois",
            email="mesmo@example.com",
            senha="senhaforte123",
            confirmar_senha="senhaforte123",
        )
        self.assertFalse(ok)
        self.assertIn("já existe", mensagem.lower())

    def test_novo_usuario_comeca_como_free(self):
        auth.cadastrar_usuario(
            nome="Bruno",
            usuario="bruno.free",
            email="free@example.com",
            senha="senhaforte123",
            confirmar_senha="senhaforte123",
        )
        conta = auth.autenticar_usuario("bruno.free", "senhaforte123")
        self.assertIsNotNone(conta)
        self.assertEqual(conta["plano"], "FREE")


class TestLogin(TestesComBancoTemporario):

    def setUp(self):
        super().setUp()
        auth.cadastrar_usuario(
            nome="Bruno Login",
            usuario="bruno.login",
            email="login@example.com",
            senha="senhaforte123",
            confirmar_senha="senhaforte123",
        )

    def test_login_com_senha_correta_funciona(self):
        conta = auth.autenticar_usuario("bruno.login", "senhaforte123")
        self.assertIsNotNone(conta)
        self.assertEqual(conta["usuario"], "bruno.login")

    def test_login_com_senha_errada_falha(self):
        conta = auth.autenticar_usuario("bruno.login", "senhaerrada")
        self.assertIsNone(conta)

    def test_login_com_usuario_inexistente_falha(self):
        conta = auth.autenticar_usuario("nao.existe", "qualquercoisa")
        self.assertIsNone(conta)

    def test_senha_nunca_fica_em_texto_puro_no_banco(self):
        with auth._conectar_banco() as conexao:
            linha = conexao.execute(
                "SELECT senha_hash FROM usuarios WHERE usuario = ?",
                ("bruno.login",),
            ).fetchone()
        self.assertNotEqual(linha["senha_hash"], "senhaforte123")
        self.assertGreater(len(linha["senha_hash"]), 20)


class TestRecuperacaoSenha(TestesComBancoTemporario):

    def setUp(self):
        super().setUp()
        auth.cadastrar_usuario(
            nome="Bruno Recup",
            usuario="bruno.recup",
            email="recup@example.com",
            senha="senhaantiga123",
            confirmar_senha="senhaantiga123",
        )

    def test_solicitar_recuperacao_gera_codigo_de_6_digitos(self):
        ok, mensagem, codigo = auth.solicitar_recuperacao_senha(
            "recup@example.com"
        )
        self.assertTrue(ok)
        self.assertIsNotNone(codigo)
        self.assertEqual(len(codigo), 6)
        self.assertTrue(codigo.isdigit())

    def test_email_nao_cadastrado_nao_revela_isso(self):
        # Por segurança, a mensagem deve ser igual quer o e-mail
        # exista ou não (evita que alguém descubra quais e-mails
        # estão cadastrados só tentando recuperar senha).
        ok, mensagem, codigo = auth.solicitar_recuperacao_senha(
            "nao.cadastrado@example.com"
        )
        self.assertTrue(ok)
        self.assertIsNone(codigo)

    def test_codigo_correto_valida(self):
        _, _, codigo = auth.solicitar_recuperacao_senha("recup@example.com")
        valido, _ = auth.validar_codigo_recuperacao("recup@example.com", codigo)
        self.assertTrue(valido)

    def test_codigo_errado_nao_valida(self):
        auth.solicitar_recuperacao_senha("recup@example.com")
        valido, mensagem = auth.validar_codigo_recuperacao(
            "recup@example.com", "000000"
        )
        self.assertFalse(valido)

    def test_redefinir_senha_com_codigo_correto_funciona(self):
        _, _, codigo = auth.solicitar_recuperacao_senha("recup@example.com")

        ok, mensagem = auth.redefinir_senha_com_codigo(
            email="recup@example.com",
            codigo=codigo,
            nova_senha="senhanova456",
            confirmar_nova_senha="senhanova456",
        )
        self.assertTrue(ok, mensagem)

        # a senha antiga não deve mais funcionar
        self.assertIsNone(
            auth.autenticar_usuario("bruno.recup", "senhaantiga123")
        )
        # a senha nova deve funcionar
        self.assertIsNotNone(
            auth.autenticar_usuario("bruno.recup", "senhanova456")
        )

    def test_codigo_usado_nao_pode_ser_reutilizado(self):
        _, _, codigo = auth.solicitar_recuperacao_senha("recup@example.com")

        auth.redefinir_senha_com_codigo(
            email="recup@example.com",
            codigo=codigo,
            nova_senha="primeiratroca1",
            confirmar_nova_senha="primeiratroca1",
        )

        # tentando usar o MESMO código de novo
        ok, mensagem = auth.redefinir_senha_com_codigo(
            email="recup@example.com",
            codigo=codigo,
            nova_senha="segundatroca2",
            confirmar_nova_senha="segundatroca2",
        )
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main(verbosity=2)
