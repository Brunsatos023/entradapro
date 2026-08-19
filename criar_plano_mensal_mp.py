import requests
import streamlit as st


URL_PLANOS = (
    "https://api.mercadopago.com/preapproval_plan"
)


def criar_plano_mensal():
    access_token = st.secrets[
        "MERCADO_PAGO_ACCESS_TOKEN"
    ]

    headers = {
        "Authorization": (
            f"Bearer {access_token}"
        ),
        "Content-Type": "application/json"
    }

    dados = {
        "reason": "EntradaPro PRO Mensal",
        "auto_recurring": {
            "frequency": 1,
            "frequency_type": "months",
            "transaction_amount": 29.90,
            "currency_id": "BRL"
        },
        "back_url": (
            "https://www.mercadopago.com.br"
        )
    }

    resposta = requests.post(
        URL_PLANOS,
        headers=headers,
        json=dados,
        timeout=20
    )

    return resposta


def main():
    st.set_page_config(
        page_title=(
            "Criar plano Mercado Pago"
        ),
        page_icon="💳"
    )

    st.title(
        "💳 EntradaPro PRO Mensal"
    )

    st.caption(
        "Criação do plano de assinatura "
        "em ambiente de teste."
    )

    st.warning(
        "Clique apenas uma vez. "
        "Cada execução bem-sucedida pode criar "
        "um novo plano no Mercado Pago."
    )

    if st.button(
        "Criar plano PRO Mensal",
        use_container_width=True
    ):
        with st.spinner(
            "Criando plano..."
        ):
            try:
                resposta = (
                    criar_plano_mensal()
                )

            except requests.RequestException as erro:
                st.error(
                    "Erro de comunicação com "
                    f"o Mercado Pago: {erro}"
                )

                return

        if resposta.status_code in {
            200,
            201
        }:
            dados = resposta.json()

            st.success(
                "Plano PRO Mensal criado "
                "com sucesso."
            )

            st.markdown(
                "**Valor:** R$ 29,90"
            )

            st.markdown(
                "**Periodicidade:** Mensal"
            )

            plano_id = dados.get(
                "id"
            )

            if plano_id:
                st.code(
                    plano_id
                )

                st.info(
                    "Guarde este ID. "
                    "Ele será usado pelo EntradaPro "
                    "para criar assinaturas."
                )

            init_point = dados.get(
                "init_point"
            )

            if init_point:
                st.success(
                    "O Mercado Pago também retornou "
                    "o link de assinatura."
                )

        else:
            st.error(
                "Não foi possível criar o plano."
            )

            st.write(
                "Status:",
                resposta.status_code
            )

            try:
                st.json(
                    resposta.json()
                )

            except Exception:
                st.text(
                    resposta.text
                )


if __name__ == "__main__":
    main()