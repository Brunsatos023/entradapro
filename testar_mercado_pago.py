import streamlit as st


def main():
    st.set_page_config(
        page_title="Teste Mercado Pago",
        page_icon="💳"
    )

    st.title(
        "💳 Teste de credenciais Mercado Pago"
    )

    try:
        access_token = st.secrets[
            "MERCADO_PAGO_ACCESS_TOKEN"
        ]

        public_key = st.secrets[
            "MERCADO_PAGO_PUBLIC_KEY"
        ]

    except Exception as erro:
        st.error(
            "Não foi possível ler as credenciais."
        )

        st.exception(
            erro
        )

        return

    if (
        access_token
        and public_key
    ):
        st.success(
            "Credenciais de teste carregadas com sucesso."
        )

        st.info(
            "Nenhuma cobrança foi criada."
        )

    else:
        st.error(
            "As credenciais estão vazias."
        )


if __name__ == "__main__":
    main()