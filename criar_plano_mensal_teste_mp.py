import os

import requests
from dotenv import load_dotenv


load_dotenv()


URL_PLANOS = (
    "https://api.mercadopago.com/preapproval_plan"
)


def obter_access_token_teste():
    return os.getenv(
        "MERCADO_PAGO_TEST_ACCESS_TOKEN"
    )


def criar_plano_mensal_teste():
    access_token = (
        obter_access_token_teste()
    )

    if not access_token:
        print(
            "ERRO: Access Token de teste "
            "não encontrado no .env."
        )
        return

    headers = {
        "Authorization": (
            f"Bearer {access_token}"
        ),
        "Content-Type": (
            "application/json"
        )
    }

    dados = {
        "reason": (
            "EntradaPro PRO Mensal TESTE"
        ),
        "auto_recurring": {
            "frequency": 1,
            "frequency_type": (
                "months"
            ),
            "transaction_amount": (
                29.90
            ),
            "currency_id": "BRL"
        },
        "back_url": (
            "https://www.mercadopago.com.br"
        )
    }

    try:
        resposta = requests.post(
            URL_PLANOS,
            headers=headers,
            json=dados,
            timeout=20
        )

    except requests.RequestException as erro:
        print(
            "Erro de comunicação com "
            f"o Mercado Pago: {erro}"
        )
        return

    print()
    print(
        "Status HTTP:",
        resposta.status_code
    )

    try:
        resposta_json = resposta.json()

    except Exception:
        resposta_json = None

    if resposta.status_code not in {
        200,
        201
    }:
        print()
        print(
            "Não foi possível criar "
            "o plano mensal de teste."
        )

        if resposta_json:
            print(
                resposta_json
            )
        else:
            print(
                resposta.text
            )

        return

    plano_id = (
        resposta_json.get(
            "id"
        )
    )

    status = (
        resposta_json.get(
            "status"
        )
    )

    init_point = (
        resposta_json.get(
            "init_point"
        )
    )

    print()
    print(
        "Plano mensal de teste "
        "criado com sucesso."
    )

    print(
        "Status:",
        status
    )

    print()
    print(
        "ID DO PLANO DE TESTE:"
    )

    print(
        plano_id
    )

    if init_point:
        print()
        print(
            "Checkout de teste "
            "também foi gerado."
        )

    print()
    print(
        "IMPORTANTE:"
    )

    print(
        "Guarde o ID acima no .env como:"
    )

    print(
        "MERCADO_PAGO_TEST_PLANO_MENSAL_ID"
    )


if __name__ == "__main__":
    criar_plano_mensal_teste()