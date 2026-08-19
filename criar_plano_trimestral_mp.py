import requests
import streamlit as st


URL_PLANOS = (
    "https://api.mercadopago.com/preapproval_plan"
)


def criar_plano_trimestral():
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
        "reason": "EntradaPro PRO Trimestral",
        "auto_recurring": {
            "frequency": 3,
            "frequency_type": "months",
            "transaction_amount": 74.90,
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
            "Criar plano trimestral"
        ),
        page_icon="💳"
    )

    st.title(
        "💳 EntradaPro PRO Trimestral"
    )

    st.markdown(
        "**Valor:** R$ 74,90"
    )

    st.markdown(
        "**Periodicidade:** 3 meses"
    )

    st.warning(
        "Clique apenas uma vez. "
        "Uma execução bem-sucedida cria "
        "o plano no Mercado Pago."
    )

    if st.button(
        "Criar plano PRO Trimestral",
        use_container_width=True
    ):
        with st.spinner(
            "Criando plano..."
        ):
            try:
                resposta = (
                    criar_plano_trimestral()
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
                "Plano PRO Trimestral "
                "criado com sucesso."
            )

            plano_id = dados.get(
                "id"
            )

            if plano_id:
                st.markdown(
                    "**ID do plano:**"
                )

                st.code(
                    plano_id
                )

                st.info(
                    "Copie este ID. "
                    "Vamos salvá-lo nas "
                    "configurações do EntradaPro."
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