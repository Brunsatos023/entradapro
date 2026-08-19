import streamlit as st

from mercado_pago_service import (
    obter_link_checkout
)

from payment_plans import (
    obter_resumo_planos,
    formatar_valor
)


def calcular_valor_mensal_equivalente(
    valor,
    meses
):
    if not meses:
        return valor

    return (
        float(valor)
        / int(meses)
    )


def calcular_desconto_percentual(
    valor_plano,
    meses,
    valor_mensal_base
):
    valor_sem_desconto = (
        valor_mensal_base
        * meses
    )

    if valor_sem_desconto <= 0:
        return 0.0

    economia = (
        valor_sem_desconto
        - valor_plano
    )

    desconto = (
        economia
        / valor_sem_desconto
        * 100
    )

    return max(
        desconto,
        0.0
    )


def obter_valor_mensal_base(
    planos
):
    for plano in planos:
        if (
            plano[
                "codigo"
            ]
            == "PRO_MENSAL"
        ):
            return float(
                plano[
                    "valor"
                ]
            )

    return 0.0


def renderizar_card_plano(
    plano,
    valor_mensal_base
):
    codigo = plano[
        "codigo"
    ]

    nome = plano[
        "nome"
    ]

    valor = float(
        plano[
            "valor"
        ]
    )

    meses = int(
        plano[
            "meses"
        ]
    )

    descricao = plano[
        "descricao"
    ]

    valor_mensal_equivalente = (
        calcular_valor_mensal_equivalente(
            valor=valor,
            meses=meses
        )
    )

    desconto = (
        calcular_desconto_percentual(
            valor_plano=valor,
            meses=meses,
            valor_mensal_base=(
                valor_mensal_base
            )
        )
    )

    with st.container(
        border=True
    ):
        st.markdown(
            f"### {nome}"
        )

        st.markdown(
            f"## {formatar_valor(valor)}"
        )

        if meses == 1:
            st.caption(
                "Cobrança mensal."
            )

        else:
            st.caption(
                "Equivale a "
                f"{formatar_valor(valor_mensal_equivalente)} "
                "por mês."
            )

        if desconto > 0:
            st.success(
                "Economize "
                f"{desconto:.0f}% "
                "em relação ao plano mensal."
            )

        st.markdown(
            descricao
        )

        st.divider()

        st.markdown(
            "✅ Acesso aos recursos PRO"
        )

        st.markdown(
            "✅ Análises completas"
        )

        st.markdown(
            "✅ EntradaPro Score"
        )

        st.markdown(
            "✅ Value e recomendação"
        )

        st.markdown(
            "✅ Motores detalhados"
        )

        st.markdown(
            "✅ Performance e validação histórica"
        )

        escolher = st.button(
            "Escolher plano",
            use_container_width=True,
            key=(
                f"escolher_"
                f"{codigo}"
            )
        )

        if escolher:
            st.session_state[
                "plano_selecionado"
            ] = codigo

            st.session_state[
                "confirmar_plano"
            ] = True

            st.session_state[
                "checkout_url"
            ] = None

            st.session_state[
                "checkout_erro"
            ] = None

            st.rerun()


def buscar_checkout_plano(
    codigo_plano
):
    resultado = obter_link_checkout(
        codigo_plano
    )

    if not resultado.get(
        "sucesso"
    ):
        return {
            "sucesso": False,
            "mensagem": resultado.get(
                "mensagem",
                (
                    "Não foi possível obter "
                    "o checkout do Mercado Pago."
                )
            )
        }

    checkout_url = resultado.get(
        "checkout_url"
    )

    if not checkout_url:
        return {
            "sucesso": False,
            "mensagem": (
                "O Mercado Pago não retornou "
                "um link de checkout."
            )
        }

    return {
        "sucesso": True,
        "checkout_url": checkout_url
    }


def renderizar_confirmacao():
    if not st.session_state.get(
        "confirmar_plano",
        False
    ):
        return

    codigo = st.session_state.get(
        "plano_selecionado"
    )

    planos = obter_resumo_planos()

    plano = None

    for item in planos:
        if (
            item[
                "codigo"
            ]
            == codigo
        ):
            plano = item
            break

    if not plano:
        st.error(
            "Plano selecionado não encontrado."
        )
        return

    st.divider()

    st.markdown(
        "## Confirmar plano"
    )

    with st.container(
        border=True
    ):
        st.markdown(
            f"### {plano['nome']}"
        )

        st.markdown(
            f"**Valor:** "
            f"{plano['valor_formatado']}"
        )

        st.markdown(
            f"**Periodicidade:** "
            f"{plano['periodicidade']}"
        )

        st.info(
            "Ao continuar, você será direcionado "
            "ao ambiente oficial do Mercado Pago "
            "para concluir a assinatura."
        )

        col1, col2 = st.columns(
            2
        )

        with col1:
            if st.button(
                "Voltar",
                use_container_width=True,
                key="voltar_planos"
            ):
                st.session_state[
                    "confirmar_plano"
                ] = False

                st.session_state[
                    "plano_selecionado"
                ] = None

                st.session_state[
                    "checkout_url"
                ] = None

                st.session_state[
                    "checkout_erro"
                ] = None

                st.rerun()

        with col2:
            if st.button(
                "Gerar checkout Mercado Pago",
                use_container_width=True,
                key="gerar_checkout"
            ):
                with st.spinner(
                    "Preparando checkout..."
                ):
                    resultado = (
                        buscar_checkout_plano(
                            codigo
                        )
                    )

                if resultado[
                    "sucesso"
                ]:
                    st.session_state[
                        "checkout_url"
                    ] = resultado[
                        "checkout_url"
                    ]

                    st.session_state[
                        "checkout_erro"
                    ] = None

                else:
                    st.session_state[
                        "checkout_url"
                    ] = None

                    st.session_state[
                        "checkout_erro"
                    ] = resultado[
                        "mensagem"
                    ]

                st.rerun()

        checkout_erro = (
            st.session_state.get(
                "checkout_erro"
            )
        )

        if checkout_erro:
            st.error(
                checkout_erro
            )

        checkout_url = (
            st.session_state.get(
                "checkout_url"
            )
        )

        if checkout_url:
            st.success(
                "Checkout preparado com sucesso."
            )

            st.link_button(
                "Ir para o Mercado Pago",
                checkout_url,
                use_container_width=True
            )

            st.caption(
                "O pagamento acontece no ambiente "
                "seguro do Mercado Pago."
            )


def renderizar_assinatura():
    st.markdown(
        "# ⭐ EntradaPro PRO"
    )

    st.caption(
        "Escolha o plano que melhor se adapta "
        "ao seu uso."
    )

    planos = obter_resumo_planos()

    if not planos:
        st.error(
            "Nenhum plano disponível."
        )
        return

    valor_mensal_base = (
        obter_valor_mensal_base(
            planos
        )
    )

    col1, col2, col3 = st.columns(
        3
    )

    colunas = [
        col1,
        col2,
        col3
    ]

    for coluna, plano in zip(
        colunas,
        planos
    ):
        with coluna:
            renderizar_card_plano(
                plano=plano,
                valor_mensal_base=(
                    valor_mensal_base
                )
            )

    renderizar_confirmacao()


def inicializar_estado():
    if (
        "plano_selecionado"
        not in st.session_state
    ):
        st.session_state[
            "plano_selecionado"
        ] = None

    if (
        "confirmar_plano"
        not in st.session_state
    ):
        st.session_state[
            "confirmar_plano"
        ] = False

    if (
        "checkout_url"
        not in st.session_state
    ):
        st.session_state[
            "checkout_url"
        ] = None

    if (
        "checkout_erro"
        not in st.session_state
    ):
        st.session_state[
            "checkout_erro"
        ] = None


def main():
    st.set_page_config(
        page_title=(
            "EntradaPro PRO"
        ),
        page_icon="⭐",
        layout="wide"
    )

    inicializar_estado()

    renderizar_assinatura()


if __name__ == "__main__":
    main()