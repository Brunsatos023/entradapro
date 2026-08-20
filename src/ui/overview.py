import streamlit as st

from access_control import usuario_eh_pro


def _limitar_percentual(valor):
    return max(
        0.0,
        min(
            float(valor),
            100.0
        )
    )


def _renderizar_barra(valor):
    percentual = int(
        round(
            _limitar_percentual(valor)
        )
    )

    st.progress(
        percentual
    )


def _renderizar_status(
    status,
    positivo=False
):
    if positivo:
        st.success(
            status
        )
    else:
        st.warning(
            status
        )


def renderizar_overview(
    nome_mandante,
    nome_visitante,
    favorito,
    resultado_match,
    resultado_prediction,
    melhor_mercado,
    resultado_value,
    resultado_oportunidade
):
    recomendacao_validada = resultado_oportunidade.get(
        "recomendacao_validada",
        True
    )

    inteligencia_casa = float(
        resultado_match.get(
            "intelligence_casa",
            0.0
        )
    )

    inteligencia_fora = float(
        resultado_match.get(
            "intelligence_fora",
            0.0
        )
    )

    score_geral = round(
        (
            inteligencia_casa
            + inteligencia_fora
        )
        / 2
    )

    confianca = resultado_match.get(
        "confianca",
        "N/D"
    )

    prob_casa = float(
        resultado_match.get(
            "probabilidade_casa",
            0.0
        )
    )

    prob_empate = float(
        resultado_match.get(
            "probabilidade_empate",
            0.0
        )
    )

    prob_fora = float(
        resultado_match.get(
            "probabilidade_fora",
            0.0
        )
    )

    over15 = float(
        resultado_prediction.get(
            "mais_15",
            0.0
        )
    )

    over25 = float(
        resultado_prediction.get(
            "mais_25",
            0.0
        )
    )

    btts = float(
        resultado_prediction.get(
            "ambas_marcam",
            0.0
        )
    )

    classificacao_over15 = resultado_prediction.get(
        "classificacao_over15",
        "NÃO CLASSIFICADO"
    )

    status_over15 = resultado_prediction.get(
        "status_estrategico_over15",
        "NÃO AVALIADO"
    )

    classificacao_over25 = resultado_prediction.get(
        "classificacao_over25",
        "NÃO CLASSIFICADO"
    )

    status_over25 = resultado_prediction.get(
        "status_estrategico_over25",
        "NÃO AVALIADO"
    )

    classificacao_btts = resultado_prediction.get(
        "classificacao_btts",
        "SINAL"
    )

    status_btts = resultado_prediction.get(
        "status_estrategico_btts",
        "NÃO VALIDADO"
    )

    # =====================================================
    # CABEÇALHO DA PARTIDA
    # =====================================================

    with st.container(
        border=True
    ):
        st.caption(
            "ANÁLISE ENTRADAPRO"
        )

        st.markdown(
            f"## ⚽ {nome_mandante} × {nome_visitante}"
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            if usuario_eh_pro():
                st.metric(
                    "EntradaPro Score",
                    f"{score_geral}/100"
                )
            else:
                st.metric(
                    "EntradaPro Score",
                    "🔒 PRO"
                )

        with col2:
            st.metric(
                "Favorito",
                favorito
            )

        with col3:
            st.metric(
                "Confiança",
                confianca
            )

    # =====================================================
    # DECISÃO PRINCIPAL
    # =====================================================

    st.markdown(
        "### 🎯 Decisão EntradaPro"
    )

    if usuario_eh_pro():
        if not recomendacao_validada:
            with st.container(
                border=True
            ):
                st.error(
                    "🚫 NÃO APOSTAR"
                )

                st.write(
                    "Nenhum mercado atingiu os critérios "
                    "estratégicos validados da V1."
                )

        else:
            if melhor_mercado == "Mais de 1,5 gols":
                probabilidade_mercado = over15

                status_mercado = status_over15

            else:
                probabilidade_mercado = btts

                status_mercado = status_btts

            with st.container(
                border=True
            ):
                col1, col2 = st.columns(
                    [2, 1]
                )

                with col1:
                    st.caption(
                        "MELHOR OPORTUNIDADE"
                    )

                    st.markdown(
                        f"## {melhor_mercado}"
                    )

                    st.markdown(
                        f"### {probabilidade_mercado:.2f}%"
                    )

                    _renderizar_barra(
                        probabilidade_mercado
                    )

                    st.success(
                        status_mercado
                    )

                with col2:
                    st.metric(
                        "Odd mercado",
                        f"{resultado_value['odd_casa']:.2f}"
                    )

                    st.metric(
                        "Odd justa",
                        f"{resultado_value['odd_justa']:.2f}"
                    )

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Edge",
                    f"{resultado_value['edge']:+.2f}%"
                )

            with col2:
                st.metric(
                    "Valor esperado",
                    f"{resultado_value['valor_esperado']:+.2f}%"
                )

    else:
        st.warning(
            "🔒 Decisão, odd justa, edge e valor esperado "
            "são exclusivos do plano PRO."
        )

        st.caption(
            "No plano FREE, as probabilidades da partida "
            "e os mercados analisados continuam disponíveis."
        )

    # =====================================================
    # PROBABILIDADES DA PARTIDA
    # =====================================================

    st.markdown(
        "### Probabilidades da partida"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            nome_mandante,
            f"{prob_casa:.2f}%"
        )

        _renderizar_barra(
            prob_casa
        )

    with col2:
        st.metric(
            "Empate",
            f"{prob_empate:.2f}%"
        )

        _renderizar_barra(
            prob_empate
        )

    with col3:
        st.metric(
            nome_visitante,
            f"{prob_fora:.2f}%"
        )

        _renderizar_barra(
            prob_fora
        )

    # =====================================================
    # MERCADOS
    # =====================================================

    st.markdown(
        "### Mercados"
    )

    with st.container(
        border=True
    ):
        col1, col2 = st.columns(
            [4, 1]
        )

        with col1:
            st.markdown(
                f"**Mais de 1,5 gols — {over15:.2f}%**"
            )

            _renderizar_barra(
                over15
            )

            st.caption(
                f"{classificacao_over15} • {status_over15}"
            )

        with col2:
            _renderizar_status(
                status_over15,
                positivo=(
                    status_over15
                    in {
                        "APTO",
                        "APTO FORTE",
                        "APTO EXPERIMENTAL"
                    }
                )
            )

    with st.container(
        border=True
    ):
        col1, col2 = st.columns(
            [4, 1]
        )

        with col1:
            st.markdown(
                f"**Mais de 2,5 gols — {over25:.2f}%**"
            )

            _renderizar_barra(
                over25
            )

            st.caption(
                f"{classificacao_over25} • {status_over25}"
            )

        with col2:
            _renderizar_status(
                status_over25,
                positivo=(
                    status_over25
                    in {
                        "APTO",
                        "APTO FORTE",
                        "APTO EXPERIMENTAL"
                    }
                )
            )

    with st.container(
        border=True
    ):
        col1, col2 = st.columns(
            [4, 1]
        )

        with col1:
            st.markdown(
                f"**Ambas marcam — {btts:.2f}%**"
            )

            _renderizar_barra(
                btts
            )

            st.caption(
                f"{classificacao_btts} • {status_btts}"
            )

        with col2:
            _renderizar_status(
                status_btts,
                positivo=False
            )