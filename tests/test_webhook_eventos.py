"""
Testes do processamento de eventos do webhook do Mercado Pago:
ativação automática via preapproval, renovação recorrente,
cancelamento, e o vínculo entre nosso id interno e o id do
Mercado Pago (external_reference / assinatura_externa_id).

Estes testes chamam `processar_evento_mercado_pago()` diretamente
com dados simulando o que o Mercado Pago realmente envia (baseado
no formato usado por resumir_recurso() em webhook_api.py) — sem
precisar de rede, FastAPI, nem conta real no Mercado Pago.
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
import subscription_service as sub  # noqa: E402


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
            nome="Bruno Webhook",
            usuario="bruno.webhook",
            email="webhook@example.com",
            senha="senhaforte123",
            confirmar_senha="senhaforte123",
        )
        conta = auth.autenticar_usuario("bruno.webhook", "senhaforte123")
        self.usuario_id = conta["id"]

        resultado = sub.registrar_assinatura_pendente(
            usuario_id=self.usuario_id, codigo_plano="PRO_MENSAL"
        )
        self.assinatura_id = resultado["assinatura_id"]

    def tearDown(self):
        db.CAMINHO_BANCO_SQLITE = self._caminho_original
        Path(self._arquivo_temp.name).unlink(missing_ok=True)


class TestEventoPreapproval(TestesComBancoTemporario):
    """
    Simula os eventos do tipo "subscription_preapproval" que o
    Mercado Pago envia quando o usuário assina/cancela/pausa.
    """

    def test_preapproval_authorized_ativa_o_usuario(self):
        resumo = {
            "id": "MP-PREAPPROVAL-123",
            "status": "authorized",
            "external_reference": str(self.assinatura_id),
            "next_payment_date": "2026-09-19T10:00:00.000-03:00",
        }

        resultado = sub.processar_evento_mercado_pago(
            tipo="subscription_preapproval", resumo=resumo
        )

        self.assertEqual(resultado["acao"], "assinatura_ativada")

        conta = auth.autenticar_usuario("bruno.webhook", "senhaforte123")
        self.assertEqual(conta["plano"], "PRO")

    def test_preapproval_vincula_id_externo_automaticamente(self):
        resumo = {
            "id": "MP-PREAPPROVAL-999",
            "status": "authorized",
            "external_reference": str(self.assinatura_id),
        }

        sub.processar_evento_mercado_pago(
            tipo="subscription_preapproval", resumo=resumo
        )

        assinatura = sub.buscar_assinatura_por_id(self.assinatura_id)
        self.assertEqual(
            assinatura["assinatura_externa_id"], "MP-PREAPPROVAL-999"
        )

    def test_preapproval_cancelled_rebaixa_o_usuario(self):
        # primeiro ativa
        sub.processar_evento_mercado_pago(
            tipo="subscription_preapproval",
            resumo={
                "id": "MP-PREAPPROVAL-777",
                "status": "authorized",
                "external_reference": str(self.assinatura_id),
            },
        )
        conta = auth.autenticar_usuario("bruno.webhook", "senhaforte123")
        self.assertEqual(conta["plano"], "PRO")

        # depois cancela (evento seguinte, sem external_reference,
        # como às vezes acontece de verdade - precisa achar pelo
        # id externo que já foi vinculado no passo anterior)
        resultado = sub.processar_evento_mercado_pago(
            tipo="subscription_preapproval",
            resumo={
                "id": "MP-PREAPPROVAL-777",
                "status": "cancelled",
                "external_reference": None,
            },
        )

        self.assertEqual(resultado["acao"], "assinatura_cancelada")

        conta = auth.autenticar_usuario("bruno.webhook", "senhaforte123")
        self.assertEqual(conta["plano"], "FREE")

    def test_preapproval_pending_nao_faz_nada(self):
        resultado = sub.processar_evento_mercado_pago(
            tipo="subscription_preapproval",
            resumo={
                "id": "MP-X",
                "status": "pending",
                "external_reference": str(self.assinatura_id),
            },
        )
        self.assertEqual(resultado["acao"], "sem_efeito")

        conta = auth.autenticar_usuario("bruno.webhook", "senhaforte123")
        self.assertEqual(conta["plano"], "FREE")

    def test_external_reference_invalido_e_ignorado_sem_quebrar(self):
        resultado = sub.processar_evento_mercado_pago(
            tipo="subscription_preapproval",
            resumo={
                "id": "MP-Y",
                "status": "authorized",
                "external_reference": "isso-nao-e-um-numero",
            },
        )
        self.assertEqual(resultado["acao"], "ignorado")

    def test_assinatura_desconhecida_e_ignorada_sem_quebrar(self):
        resultado = sub.processar_evento_mercado_pago(
            tipo="subscription_preapproval",
            resumo={
                "id": "MP-Z",
                "status": "authorized",
                "external_reference": "999999",  # id que não existe
            },
        )
        self.assertEqual(resultado["acao"], "ignorado")


class TestEventoPagamentoRecorrente(TestesComBancoTemporario):
    """
    Simula "subscription_authorized_payment": a cobrança recorrente
    de uma assinatura já existente (ex: a renovação do mês seguinte).
    """

    def setUp(self):
        super().setUp()
        # a assinatura já precisa estar vinculada a um id do
        # Mercado Pago (isso acontece no primeiro evento de
        # preapproval, antes de qualquer cobrança recorrente)
        sub.vincular_assinatura_externa(
            assinatura_id=self.assinatura_id,
            assinatura_externa_id="MP-PREAPPROVAL-ABC",
        )

    def test_pagamento_aprovado_mantem_assinatura_ativa(self):
        resultado = sub.processar_evento_mercado_pago(
            tipo="subscription_authorized_payment",
            resumo={
                "preapproval_id": "MP-PREAPPROVAL-ABC",
                "payment_id": "MP-PAY-1",
                "payment_status": "approved",
                "transaction_amount": 29.90,
            },
        )
        self.assertEqual(resultado["acao"], "renovacao_aprovada")

        conta = auth.autenticar_usuario("bruno.webhook", "senhaforte123")
        self.assertEqual(conta["plano"], "PRO")

    def test_pagamento_recorrente_duplicado_nao_conta_duas_vezes(self):
        for _ in range(2):
            sub.processar_evento_mercado_pago(
                tipo="subscription_authorized_payment",
                resumo={
                    "preapproval_id": "MP-PREAPPROVAL-ABC",
                    "payment_id": "MP-PAY-DUPLICADO",
                    "payment_status": "approved",
                    "transaction_amount": 29.90,
                },
            )

        assinatura = sub.buscar_assinatura_por_id(self.assinatura_id)
        with db.conectar_banco() as conexao:
            total = conexao.execute(
                "SELECT COUNT(*) as n FROM pagamentos "
                "WHERE assinatura_id = ?",
                (assinatura["id"],),
            ).fetchone()["n"]
        self.assertEqual(total, 1)

    def test_pagamento_recorrente_recusado_nao_ativa(self):
        resultado = sub.processar_evento_mercado_pago(
            tipo="subscription_authorized_payment",
            resumo={
                "preapproval_id": "MP-PREAPPROVAL-ABC",
                "payment_id": "MP-PAY-2",
                "payment_status": "rejected",
                "transaction_amount": 29.90,
            },
        )
        self.assertEqual(resultado["acao"], "renovacao_recusada")

        conta = auth.autenticar_usuario("bruno.webhook", "senhaforte123")
        self.assertEqual(conta["plano"], "FREE")


class TestEventoPagamentoAvulso(TestesComBancoTemporario):
    """Simula "payment": um pagamento avulso vinculado por external_reference."""

    def test_pagamento_avulso_aprovado_ativa_usuario(self):
        resultado = sub.processar_evento_mercado_pago(
            tipo="payment",
            resumo={
                "id": "MP-PAY-AVULSO-1",
                "status": "approved",
                "external_reference": str(self.assinatura_id),
                "transaction_amount": 29.90,
            },
        )
        self.assertEqual(resultado["acao"], "assinatura_ativada")

        conta = auth.autenticar_usuario("bruno.webhook", "senhaforte123")
        self.assertEqual(conta["plano"], "PRO")

    def test_tipo_desconhecido_e_ignorado(self):
        resultado = sub.processar_evento_mercado_pago(
            tipo="algum_tipo_novo_do_mercado_pago",
            resumo={"id": "X"},
        )
        self.assertEqual(resultado["acao"], "ignorado")

    def test_resumo_vazio_e_ignorado_sem_quebrar(self):
        resultado = sub.processar_evento_mercado_pago(
            tipo="payment", resumo={}
        )
        self.assertEqual(resultado["acao"], "ignorado")


if __name__ == "__main__":
    unittest.main(verbosity=2)
