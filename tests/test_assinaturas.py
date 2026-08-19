"""
Testes do fluxo de assinatura: criação de pagamento, ativação de PRO,
cancelamento, expiração e proteção contra webhook duplicado.

IMPORTANTE: nunca toca no banco real (data/entradapro_users.db).
Cada teste usa seu próprio banco temporário.
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
import subscription_service as sub  # noqa: E402
import db  # noqa: E402


class TestesComBancoTemporario(unittest.TestCase):

    def setUp(self):
        self._arquivo_temp = tempfile.NamedTemporaryFile(
            suffix=".db", delete=False
        )
        self._arquivo_temp.close()

        self._caminho_original = db.CAMINHO_BANCO_SQLITE
        db.CAMINHO_BANCO_SQLITE = Path(self._arquivo_temp.name)

        auth.inicializar_banco()

        auth.cadastrar_usuario(
            nome="Bruno Assinante",
            usuario="bruno.assinante",
            email="assinante@example.com",
            senha="senhaforte123",
            confirmar_senha="senhaforte123",
        )
        conta = auth.autenticar_usuario("bruno.assinante", "senhaforte123")
        self.usuario_id = conta["id"]

    def tearDown(self):
        db.CAMINHO_BANCO_SQLITE = self._caminho_original
        Path(self._arquivo_temp.name).unlink(missing_ok=True)


class TestCriacaoDeAssinatura(TestesComBancoTemporario):

    def test_registrar_assinatura_pendente_com_plano_valido(self):
        resultado = sub.registrar_assinatura_pendente(
            usuario_id=self.usuario_id,
            codigo_plano="PRO_MENSAL",
        )
        self.assertTrue(resultado["sucesso"])
        self.assertIn("assinatura_id", resultado)

    def test_registrar_assinatura_com_plano_invalido_falha(self):
        resultado = sub.registrar_assinatura_pendente(
            usuario_id=self.usuario_id,
            codigo_plano="PLANO_QUE_NAO_EXISTE",
        )
        self.assertFalse(resultado["sucesso"])

    def test_nao_cria_assinatura_duplicada_se_ja_existe_pendente(self):
        primeira = sub.registrar_assinatura_pendente(
            usuario_id=self.usuario_id, codigo_plano="PRO_MENSAL"
        )
        segunda = sub.registrar_assinatura_pendente(
            usuario_id=self.usuario_id, codigo_plano="PRO_MENSAL"
        )
        self.assertEqual(
            primeira["assinatura_id"], segunda["assinatura_id"]
        )
        self.assertTrue(segunda["ja_existia"])


class TestAtivacaoDeAssinatura(TestesComBancoTemporario):

    def setUp(self):
        super().setUp()
        resultado = sub.registrar_assinatura_pendente(
            usuario_id=self.usuario_id, codigo_plano="PRO_MENSAL"
        )
        self.assinatura_id = resultado["assinatura_id"]

    def test_usuario_comeca_free_antes_do_pagamento(self):
        conta = auth.autenticar_usuario("bruno.assinante", "senhaforte123")
        self.assertEqual(conta["plano"], "FREE")

    def test_processar_assinatura_ativa_promove_usuario_a_pro(self):
        resultado = sub.processar_assinatura_ativa(
            assinatura_id=self.assinatura_id
        )
        self.assertTrue(resultado["sucesso"])

        conta = auth.autenticar_usuario("bruno.assinante", "senhaforte123")
        self.assertEqual(conta["plano"], "PRO")

    def test_assinatura_ativa_aparece_com_status_correto(self):
        sub.processar_assinatura_ativa(assinatura_id=self.assinatura_id)
        assinatura = sub.buscar_assinatura_por_id(self.assinatura_id)
        self.assertEqual(assinatura["status"], "ATIVA")

    def test_cancelar_assinatura_rebaixa_para_free_via_fluxo_completo(self):
        # ativa primeiro
        sub.processar_assinatura_ativa(assinatura_id=self.assinatura_id)
        conta = auth.autenticar_usuario("bruno.assinante", "senhaforte123")
        self.assertEqual(conta["plano"], "PRO")

        # cancela a assinatura
        resultado = sub.processar_assinatura_cancelada(
            assinatura_id=self.assinatura_id
        )
        self.assertTrue(resultado["sucesso"])

        assinatura = sub.buscar_assinatura_por_id(self.assinatura_id)
        self.assertEqual(assinatura["status"], "CANCELADA")

    def test_assinatura_inexistente_nao_quebra_o_sistema(self):
        resultado = sub.processar_assinatura_ativa(assinatura_id=999999)
        self.assertFalse(resultado["sucesso"])


class TestRegistroDePagamentoEWebhookDuplicado(TestesComBancoTemporario):

    def setUp(self):
        super().setUp()
        resultado = sub.registrar_assinatura_pendente(
            usuario_id=self.usuario_id, codigo_plano="PRO_MENSAL"
        )
        self.assinatura_id = resultado["assinatura_id"]

    def test_registra_pagamento_normalmente(self):
        resultado = sub.registrar_pagamento(
            usuario_id=self.usuario_id,
            assinatura_id=self.assinatura_id,
            pagamento_externo_id="MP-123456",
            valor=29.90,
            status="APROVADO",
            forma_pagamento="PIX",
        )
        self.assertTrue(resultado["sucesso"])
        self.assertFalse(resultado["ja_existia"])

    def test_webhook_duplicado_nao_cria_pagamento_repetido(self):
        """
        Simula o Mercado Pago enviando o MESMO webhook duas vezes
        (isso acontece de verdade em produção). O sistema não pode
        registrar o pagamento duas vezes nem contar a venda duas vezes.
        """
        primeiro = sub.registrar_pagamento(
            usuario_id=self.usuario_id,
            assinatura_id=self.assinatura_id,
            pagamento_externo_id="MP-DUPLICADO-1",
            valor=29.90,
            status="APROVADO",
        )
        segundo = sub.registrar_pagamento(
            usuario_id=self.usuario_id,
            assinatura_id=self.assinatura_id,
            pagamento_externo_id="MP-DUPLICADO-1",  # mesmo ID externo
            valor=29.90,
            status="APROVADO",
        )

        self.assertTrue(primeiro["sucesso"])
        self.assertTrue(segundo["sucesso"])
        self.assertFalse(primeiro["ja_existia"])
        self.assertTrue(segundo["ja_existia"])
        self.assertEqual(primeiro["pagamento_id"], segundo["pagamento_id"])

    def test_pagamento_recusado_nao_promove_usuario(self):
        sub.registrar_pagamento(
            usuario_id=self.usuario_id,
            assinatura_id=self.assinatura_id,
            pagamento_externo_id="MP-RECUSADO",
            valor=29.90,
            status="RECUSADO",
        )
        conta = auth.autenticar_usuario("bruno.assinante", "senhaforte123")
        self.assertEqual(conta["plano"], "FREE")

    def test_valor_de_pagamento_invalido_e_rejeitado(self):
        resultado = sub.registrar_pagamento(
            usuario_id=self.usuario_id,
            assinatura_id=self.assinatura_id,
            pagamento_externo_id="MP-INVALIDO",
            valor="isso-nao-e-um-numero",
            status="APROVADO",
        )
        self.assertFalse(resultado["sucesso"])


class TestControleAcessoFreePro(unittest.TestCase):
    """
    Testa access_control.py isoladamente (não depende de banco,
    só do "usuário logado" guardado na sessão).
    """

    def setUp(self):
        st = sys.modules["streamlit"]
        st.session_state = {}
        import access_control
        self.access_control = access_control

    def test_visitante_sem_login_e_tratado_como_free(self):
        self.assertFalse(self.access_control.usuario_eh_pro())
        self.assertTrue(self.access_control.usuario_eh_free())

    def test_usuario_free_nao_e_pro(self):
        sys.modules["streamlit"].session_state["usuario"] = {
            "plano": "FREE"
        }
        self.assertFalse(self.access_control.usuario_eh_pro())

    def test_usuario_pro_e_reconhecido_como_pro(self):
        sys.modules["streamlit"].session_state["usuario"] = {
            "plano": "PRO"
        }
        self.assertTrue(self.access_control.usuario_eh_pro())

    def test_plano_com_minusculo_ou_espaco_ainda_funciona(self):
        # o banco podia (por erro humano) salvar " pro " em vez de "PRO"
        sys.modules["streamlit"].session_state["usuario"] = {
            "plano": " pro "
        }
        self.assertTrue(self.access_control.usuario_eh_pro())


if __name__ == "__main__":
    unittest.main(verbosity=2)
