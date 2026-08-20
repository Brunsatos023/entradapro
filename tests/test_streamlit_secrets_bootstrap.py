"""Testes do bootstrap que gera .streamlit/secrets.toml a partir
de variáveis de ambiente, para o login nativo do Streamlit com
Google funcionar em produção (Render)."""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import streamlit_secrets_bootstrap as bootstrap  # noqa: E402


VARIAVEIS_COMPLETAS = {
    "GOOGLE_CLIENT_ID": "id-123",
    "GOOGLE_CLIENT_SECRET": "secret-456",
    "STREAMLIT_COOKIE_SECRET": "cookie-789",
    "STREAMLIT_REDIRECT_URI": "https://entradapro.com.br/oauth2callback",
}


class TestGoogleLoginConfigurado(unittest.TestCase):

    @patch.dict("os.environ", {}, clear=True)
    def test_sem_nenhuma_variavel_retorna_falso(self):
        self.assertFalse(bootstrap.google_login_configurado())

    @patch.dict("os.environ", VARIAVEIS_COMPLETAS, clear=True)
    def test_com_todas_as_variaveis_retorna_verdadeiro(self):
        self.assertTrue(bootstrap.google_login_configurado())

    @patch.dict(
        "os.environ",
        {"GOOGLE_CLIENT_ID": "id-123"},
        clear=True,
    )
    def test_variaveis_incompletas_retorna_falso(self):
        self.assertFalse(bootstrap.google_login_configurado())


class TestConfigurarSecretsGoogle(unittest.TestCase):

    def setUp(self):
        self._caminho_original = bootstrap.CAMINHO_SECRETS
        self._caminho_temp = Path(
            tempfile.mktemp(suffix=".toml")
        )
        bootstrap.CAMINHO_SECRETS = self._caminho_temp

    def tearDown(self):
        bootstrap.CAMINHO_SECRETS = self._caminho_original
        self._caminho_temp.unlink(missing_ok=True)

    @patch.dict("os.environ", {}, clear=True)
    def test_sem_variaveis_nao_gera_arquivo(self):
        resultado = bootstrap.configurar_secrets_google()
        self.assertFalse(resultado)
        self.assertFalse(self._caminho_temp.exists())

    @patch.dict("os.environ", VARIAVEIS_COMPLETAS, clear=True)
    def test_com_variaveis_gera_arquivo_valido(self):
        resultado = bootstrap.configurar_secrets_google()
        self.assertTrue(resultado)
        self.assertTrue(self._caminho_temp.exists())

        conteudo = self._caminho_temp.read_text()
        self.assertIn("id-123", conteudo)
        self.assertIn("secret-456", conteudo)
        self.assertIn("[auth]", conteudo)

    @patch.dict("os.environ", VARIAVEIS_COMPLETAS, clear=True)
    def test_nao_sobrescreve_arquivo_ja_existente(self):
        self._caminho_temp.parent.mkdir(parents=True, exist_ok=True)
        self._caminho_temp.write_text("conteudo original")

        bootstrap.configurar_secrets_google()

        self.assertEqual(
            self._caminho_temp.read_text(), "conteudo original"
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
