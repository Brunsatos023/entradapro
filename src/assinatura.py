import streamlit as st

from auth import (
    inicializar_banco,
    inicializar_estado_autenticacao,
    obter_usuario_logado,
    renderizar_autenticacao
)

from mercado_pago_service import (
    obter_link_checkout
)

from payment_plans import (
    obter_resumo_planos,
    formatar_valor
)

from subscription_service import (
    registrar_assinatura_pendente,
    buscar_assinatura_por_id
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
            plano["codigo"]
            == "PRO_MENSAL"
        ):
            return float(
                plano["valor"]
            )

    return 0.0


def obter_plano_por_codigo(
    codigo
):
    planos = obter_resumo_planos()

    for plano in planos:
        if (
            plano["codigo"]
            == codigo
        ):
            return plano

    return None


def limpar_checkout():
    st.session_state[
        "checkout_url"
    ] = None

    st.session_state[
        "checkout_erro"
    ] = None

    st.session_state[
        "assinatura_local_id"
    ] = None


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

            limpar_checkout()

            st.rerun()


def preparar_checkout(
    usuario,
    codigo_plano
):
    resultado_assinatura = (
        registrar_assinatura_pendente(
            usuario_id=usuario[
                "id"
            ],
            codigo_plano=(
                codigo_plano
            )
        )
    )

    if not resultado_assinatura.get(
        "sucesso"
    ):
        return {
            "sucesso": False,
            "mensagem": (
                resultado_assinatura.get(
                    "mensagem",
                    (
                        "Não foi possível registrar "
                        "a assinatura no EntradaPro."
                    )
                )
            )
        }

    assinatura_id = (
        resultado_assinatura[
            "assinatura_id"
        ]
    )

    assinatura = (
        buscar_assinatura_por_id(
            assinatura_id
        )
    )

    if not assinatura:
        return {
            "sucesso": False,
            "mensagem": (
                "A assinatura foi registrada, "
                "mas não pôde ser localizada."
            )
        }

    resultado_checkout = (
        obter_link_checkout(
            codigo_plano
        )
    )

    if not resultado_checkout.get(
        "sucesso"
    ):
        return {
            "sucesso": False,
            "mensagem": (
                resultado_checkout.get(
                    "mensagem",
                    (
                        "Não foi possível obter "
                        "o checkout do Mercado Pago."
                    )
                )
            )
        }

    checkout_url = (
        resultado_checkout.get(
            "checkout_url"
        )
    )

    if not checkout_url:
        return {
            "sucesso": False,
            "mensagem": (
                "O Mercado Pago não retornou "
                "o link de checkout."
            )
        }

    return {
        "sucesso": True,
        "checkout_url": (
            checkout_url
        ),
        "assinatura_id": (
            assinatura_id
        )
    }


def renderizar_confirmacao(
    usuario
):
    if not st.session_state.get(
        "confirmar_plano",
        False
    ):
        return

    codigo = st.session_state.get(
        "plano_selecionado"
    )

    plano = obter_plano_por_codigo(
        codigo
    )

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

        st.markdown(
            f"**Conta:** "
            f"@{usuario['usuario']}"
        )

        st.markdown(
            f"**E-mail:** "
            f"{usuario['email']}"
        )

        st.info(
            "Ao continuar, o EntradaPro "
            "registrará a intenção de assinatura "
            "e abrirá o checkout oficial "
            "do Mercado Pago."
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

                limpar_checkout()

                st.rerun()

        with col2:
            if st.button(
                "Preparar pagamento",
                use_container_width=True,
                key="preparar_pagamento"
            ):
                with st.spinner(
                    "Preparando checkout..."
                ):
                    resultado = (
                        preparar_checkout(
                            usuario=usuario,
                            codigo_plano=(
                                codigo
                            )
                        )
                    )

                if resultado.get(
                    "sucesso"
                ):
                    st.session_state[
                        "checkout_url"
                    ] = resultado[
                        "checkout_url"
                    ]

                    st.session_state[
                        "assinatura_local_id"
                    ] = resultado[
                        "assinatura_id"
                    ]

                    st.session_state[
                        "checkout_erro"
                    ] = None

                else:
                    st.session_state[
                        "checkout_url"
                    ] = None

                    st.session_state[
                        "assinatura_local_id"
                    ] = None

                    st.session_state[
                        "checkout_erro"
                    ] = resultado.get(
                        "mensagem",
                        (
                            "Não foi possível "
                            "preparar o pagamento."
                        )
                    )

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

        assinatura_local_id = (
            st.session_state.get(
                "assinatura_local_id"
            )
        )

        if checkout_url:
            st.success(
                "Checkout preparado "
                "com sucesso."
            )

            if assinatura_local_id:
                st.caption(
                    "Referência interna "
                    f"da assinatura: #{assinatura_local_id}"
                )

            st.link_button(
                "Ir para o Mercado Pago",
                checkout_url,
                use_container_width=True
            )

            st.caption(
                "A conclusão da assinatura "
                "acontece no ambiente seguro "
                "do Mercado Pago."
            )


def renderizar_assinatura(
    usuario
):
    st.markdown(
        "# ⭐ EntradaPro PRO"
    )

    st.caption(
        "Escolha o plano que melhor "
        "se adapta ao seu uso."
    )

    st.markdown(
        f"Logado como **@{usuario['usuario']}**"
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

    col1, col2, col3 = (
        st.columns(
            3
        )
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

    renderizar_confirmacao(
        usuario
    )


def inicializar_estado_assinatura():
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

    if (
        "assinatura_local_id"
        not in st.session_state
    ):
        st.session_state[
            "assinatura_local_id"
        ] = None


def main():
    st.set_page_config(
        page_title=(
            "EntradaPro PRO"
        ),
        page_icon="⭐",
        layout="wide"
    )

    inicializar_banco()
    inicializar_estado_autenticacao()
    inicializar_estado_assinatura()

    if not renderizar_autenticacao():
        return

    usuario = obter_usuario_logado()

    if not usuario:
        st.error(
            "Não foi possível identificar "
            "o usuário logado."
        )

        return

    renderizar_assinatura(
        usuario
    )


if __name__ == "__main__":
    main()