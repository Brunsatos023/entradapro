import requests
import streamlit as st


URL_TESTE = (
    "https://api.mercadolibre.com/users/me"
)


def testar_conexao():
    try:
        access_token = st.secrets[
            "MERCADO_PAGO_ACCESS_TOKEN"
        ]

    except Exception:
        return {
            "sucesso": False,
            "mensagem": (
                "Não foi possível carregar "
                "o Access Token."
            )
        }

    headers = {
        "Authorization": (
            f"Bearer {access_token}"
        )
    }

    try:
        resposta = requests.get(
            URL_TESTE,
            headers=headers,
            timeout=15
        )

    except requests.RequestException as erro:
        return {
            "sucesso": False,
            "mensagem": (
                "Erro de conexão com "
                f"o Mercado Pago: {erro}"
            )
        }

    if resposta.status_code != 200:
        return {
            "sucesso": False,
            "mensagem": (
                "A API respondeu com "
                f"status {resposta.status_code}."
            )
        }

    dados = resposta.json()

    return {
        "sucesso": True,
        "user_id": dados.get(
            "id"
        ),
        "nickname": dados.get(
            "nickname"
        )
    }


def main():
    st.set_page_config(
        page_title=(
            "Teste API Mercado Pago"
        ),
        page_icon="🔌"
    )

    st.title(
        "🔌 EntradaPro + Mercado Pago"
    )

    st.caption(
        "Teste seguro de comunicação "
        "com a API."
    )

    if st.button(
        "Testar conexão",
        use_container_width=True
    ):
        with st.spinner(
            "Conectando..."
        ):
            resultado = testar_conexao()

        if resultado[
            "sucesso"
        ]:
            st.success(
                "Conexão com a API "
                "realizada com sucesso."
            )

            st.info(
                "Nenhuma cobrança, pagamento "
                "ou assinatura foi criada."
            )

            if resultado.get(
                "user_id"
            ):
                st.write(
                    "User ID identificado:",
                    resultado[
                        "user_id"
                    ]
                )

        else:
            st.error(
                resultado[
                    "mensagem"
                ]
            )


if __name__ == "__main__":
    main()