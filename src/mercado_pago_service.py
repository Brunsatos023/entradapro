import os

import requests
import streamlit as st
from dotenv import load_dotenv


load_dotenv()


URL_BASE_PLANOS = (
    "https://api.mercadopago.com/preapproval_plan"
)


# =========================================================
# AMBIENTE
# =========================================================


def obter_ambiente():
    ambiente = os.getenv(
        "MERCADO_PAGO_AMBIENTE",
        "TEST"
    )

    ambiente = str(
        ambiente
    ).strip().upper()

    if ambiente not in {
        "TEST",
        "PRODUCTION"
    }:
        return "TEST"

    return ambiente


def ambiente_eh_teste():
    return (
        obter_ambiente()
        == "TEST"
    )


# =========================================================
# CREDENCIAIS
# =========================================================


def obter_access_token():
    if ambiente_eh_teste():
        return os.getenv(
            "MERCADO_PAGO_TEST_ACCESS_TOKEN"
        )

    token_env = os.getenv(
        "MERCADO_PAGO_ACCESS_TOKEN"
    )

    if token_env:
        return token_env

    try:
        return st.secrets[
            "MERCADO_PAGO_ACCESS_TOKEN"
        ]

    except Exception:
        return None


def obter_public_key():
    if ambiente_eh_teste():
        return os.getenv(
            "MERCADO_PAGO_TEST_PUBLIC_KEY"
        )

    chave_env = os.getenv(
        "MERCADO_PAGO_PUBLIC_KEY"
    )

    if chave_env:
        return chave_env

    try:
        return st.secrets[
            "MERCADO_PAGO_PUBLIC_KEY"
        ]

    except Exception:
        return None


# =========================================================
# IDs DOS PLANOS
# =========================================================


SEGREDOS_PLANOS_PRODUCAO = {
    "PRO_MENSAL": (
        "MERCADO_PAGO_PLANO_MENSAL_ID"
    ),
    "PRO_TRIMESTRAL": (
        "MERCADO_PAGO_PLANO_TRIMESTRAL_ID"
    ),
    "PRO_ANUAL": (
        "MERCADO_PAGO_PLANO_ANUAL_ID"
    )
}


VARIAVEIS_PLANOS_TESTE = {
    "PRO_MENSAL": (
        "MERCADO_PAGO_TEST_PLANO_MENSAL_ID"
    ),
    "PRO_TRIMESTRAL": (
        "MERCADO_PAGO_TEST_PLANO_TRIMESTRAL_ID"
    ),
    "PRO_ANUAL": (
        "MERCADO_PAGO_TEST_PLANO_ANUAL_ID"
    )
}


def obter_id_plano(
    codigo_plano
):
    if ambiente_eh_teste():
        nome_variavel = (
            VARIAVEIS_PLANOS_TESTE.get(
                codigo_plano
            )
        )

        if not nome_variavel:
            return None

        return os.getenv(
            nome_variavel
        )

    nome_segredo = (
        SEGREDOS_PLANOS_PRODUCAO.get(
            codigo_plano
        )
    )

    if not nome_segredo:
        return None

    try:
        return st.secrets[
            nome_segredo
        ]

    except Exception:
        return os.getenv(
            nome_segredo
        )


# =========================================================
# HEADERS
# =========================================================


def obter_headers():
    access_token = obter_access_token()

    if not access_token:
        return None

    return {
        "Authorization": (
            f"Bearer {access_token}"
        ),
        "Content-Type": (
            "application/json"
        )
    }


# =========================================================
# CONSULTAR PLANO
# =========================================================


def consultar_plano(
    codigo_plano
):
    headers = obter_headers()

    if not headers:
        return {
            "sucesso": False,
            "mensagem": (
                "Access Token do Mercado Pago "
                "não configurado para o ambiente "
                f"{obter_ambiente()}."
            )
        }

    plano_id = obter_id_plano(
        codigo_plano
    )

    if not plano_id:
        return {
            "sucesso": False,
            "mensagem": (
                "ID do plano não configurado "
                "para o ambiente "
                f"{obter_ambiente()}."
            )
        }

    url = (
        f"{URL_BASE_PLANOS}/"
        f"{plano_id}"
    )

    try:
        resposta = requests.get(
            url,
            headers=headers,
            timeout=20
        )

    except requests.RequestException as erro:
        return {
            "sucesso": False,
            "mensagem": (
                "Erro de comunicação com "
                f"o Mercado Pago: {erro}"
            )
        }

    if resposta.status_code != 200:
        return {
            "sucesso": False,
            "mensagem": (
                "Mercado Pago respondeu com "
                f"status {resposta.status_code}."
            ),
            "status_http": (
                resposta.status_code
            )
        }

    try:
        dados = resposta.json()

    except Exception:
        return {
            "sucesso": False,
            "mensagem": (
                "O Mercado Pago retornou "
                "uma resposta inválida."
            )
        }

    return {
        "sucesso": True,
        "ambiente": obter_ambiente(),
        "id": dados.get(
            "id"
        ),
        "status": dados.get(
            "status"
        ),
        "reason": dados.get(
            "reason"
        ),
        "init_point": dados.get(
            "init_point"
        ),
        "dados": dados
    }


# =========================================================
# CHECKOUT
# =========================================================


def obter_link_checkout(
    codigo_plano
):
    resultado = consultar_plano(
        codigo_plano
    )

    if not resultado.get(
        "sucesso"
    ):
        return resultado

    status = str(
        resultado.get(
            "status"
        )
        or ""
    ).strip().lower()

    if status != "active":
        return {
            "sucesso": False,
            "mensagem": (
                "O plano não está ativo "
                "no Mercado Pago."
            )
        }

    init_point = resultado.get(
        "init_point"
    )

    if not init_point:
        return {
            "sucesso": False,
            "mensagem": (
                "O Mercado Pago não retornou "
                "o link de checkout."
            )
        }

    return {
        "sucesso": True,
        "ambiente": obter_ambiente(),
        "checkout_url": (
            init_point
        )
    }


# =========================================================
# DIAGNÓSTICO
# =========================================================


def diagnostico_configuracao():
    return {
        "ambiente": (
            obter_ambiente()
        ),
        "access_token_configurado": bool(
            obter_access_token()
        ),
        "public_key_configurada": bool(
            obter_public_key()
        ),
        "plano_mensal_configurado": bool(
            obter_id_plano(
                "PRO_MENSAL"
            )
        ),
        "plano_trimestral_configurado": bool(
            obter_id_plano(
                "PRO_TRIMESTRAL"
            )
        ),
        "plano_anual_configurado": bool(
            obter_id_plano(
                "PRO_ANUAL"
            )
        )
    }