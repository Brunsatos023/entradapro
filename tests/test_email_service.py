"""
Testes do email_service - especialmente a garantia de que, sem
SMTP configurado, o sistema NUNCA volta a expor o código na tela
como alternativa (isso foi uma vulnerabilidade real, corrigida).
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import email_service  # noqa: E402


class TestEnviarEmailRecuperacao(unittest.TestCase):

    @patch.dict("os.environ", {}, clear=True)
    def test_sem_credenciais_falha_com_seguranca(self):
        sucesso, mensagem = email_service.enviar_email_recuperacao(
            "teste@example.com", "123456"
        )
        self.assertFalse(sucesso)
        self.assertIn("configurado", mensagem.lower())

    @patch.dict(
        "os.environ",
        {"SMTP_EMAIL": "bot@example.com", "SMTP_APP_PASSWORD": "senha123"},
    )
    @patch("email_service.smtplib.SMTP")
    def test_com_credenciais_envia_com_sucesso(self, mock_smtp_classe):
        mock_servidor = MagicMock()
        mock_smtp_classe.return_value.__enter__.return_value = (
            mock_servidor
        )

        sucesso, mensagem = email_service.enviar_email_recuperacao(
            "destino@example.com", "654321"
        )

        self.assertTrue(sucesso)
        mock_servidor.login.assert_called_once()
        mock_servidor.sendmail.assert_called_once()

    @patch.dict(
        "os.environ",
        {"SMTP_EMAIL": "bot@example.com", "SMTP_APP_PASSWORD": "senha123"},
    )
    @patch("email_service.smtplib.SMTP")
    def test_erro_de_envio_e_tratado_sem_quebrar(self, mock_smtp_classe):
        mock_smtp_classe.side_effect = Exception("conexão recusada")

        sucesso, mensagem = email_service.enviar_email_recuperacao(
            "destino@example.com", "654321"
        )

        self.assertFalse(sucesso)
        self.assertIn("não foi possível", mensagem.lower())

    @patch.dict("os.environ", {"SMTP_EMAIL": "bot@example.com"}, clear=True)
    def test_apenas_uma_credencial_configurada_ainda_falha(self):
        # so SMTP_EMAIL sem SMTP_APP_PASSWORD nao deve ser suficiente
        sucesso, _ = email_service.enviar_email_recuperacao(
            "teste@example.com", "111111"
        )
        self.assertFalse(sucesso)


if __name__ == "__main__":
    unittest.main(verbosity=2)
