import streamlit as st

from access_control import usuario_eh_pro, renderizar_bloqueio_pro
from ui.escudos_times import html_escudo


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

    eh_pro_decisao = usuario_eh_pro()
    classe_borrado_decisao = (
        "" if eh_pro_decisao else "conteudo-borrado"
    )

    if not recomendacao_validada:
        with st.container(
            border=True
        ):
            st.markdown(
                f'<div class="{classe_borrado_decisao}">',
                unsafe_allow_html=True
            )
            st.error(
                "🚫 NÃO APOSTAR"
            )

            st.write(
                "Nenhum mercado atingiu os critérios "
                "estratégicos validados da V1."
            )
            st.markdown('</div>', unsafe_allow_html=True)

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
                st.markdown(
                    f'<div class="{classe_borrado_decisao}">',
                    unsafe_allow_html=True
                )
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
                st.markdown('</div>', unsafe_allow_html=True)

            with col2:
                st.markdown(
                    f'<div class="{classe_borrado_decisao}">',
                    unsafe_allow_html=True
                )
                st.metric(
                    "Odd mercado",
                    f"{resultado_value['odd_casa']:.2f}"
                )

                st.metric(
                    "Odd justa",
                    f"{resultado_value['odd_justa']:.2f}"
                )
                st.markdown('</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                f'<div class="{classe_borrado_decisao}">',
                unsafe_allow_html=True
            )
            st.metric(
                "Edge",
                f"{resultado_value['edge']:+.2f}%"
            )
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown(
                f'<div class="{classe_borrado_decisao}">',
                unsafe_allow_html=True
            )
            st.metric(
                "Valor esperado",
                f"{resultado_value['valor_esperado']:+.2f}%"
            )
            st.markdown('</div>', unsafe_allow_html=True)

    if not eh_pro_decisao:
        st.markdown(
            '<div style="text-align:center;margin-top:10px;">'
            '<span style="background:rgba(217,163,83,.12);'
            'border:1px solid rgba(217,163,83,.3);border-radius:8px;'
            'padding:8px 16px;color:var(--green);font-size:13px;">'
            '🔒 Desbloquear Decisão EntradaPro com PRO</span></div>',
            unsafe_allow_html=True
        )

    # =====================================================
    # PROBABILIDADES DA PARTIDA
    # =====================================================

    st.markdown(
        "### Probabilidades da partida"
    )

    maior_prob = max(prob_casa, prob_empate, prob_fora)

    col1, col2, col3 = st.columns(3)

    with col1:
        destaque = " destaque-favorito" if prob_casa == maior_prob else ""
        st.markdown(
            f'<div class="card-probabilidade{destaque}">'
            f'<div style="display:flex;align-items:center;gap:6px;'
            f'margin-bottom:6px;">'
            f'{html_escudo(nome_mandante)}'
            f'<span style="font-size:12px;color:var(--text-muted);">'
            f'{nome_mandante}</span></div>'
            f'<div style="font-size:24px;font-weight:700;">'
            f'{prob_casa:.2f}%</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        _renderizar_barra(
            prob_casa
        )

    with col2:
        destaque = " destaque-favorito" if prob_empate == maior_prob else ""
        st.markdown(
            f'<div class="card-probabilidade{destaque}">'
            f'<div style="font-size:12px;color:var(--text-muted);'
            f'margin-bottom:6px;">Empate</div>'
            f'<div style="font-size:24px;font-weight:700;">'
            f'{prob_empate:.2f}%</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        _renderizar_barra(
            prob_empate
        )

    with col3:
        destaque = " destaque-favorito" if prob_fora == maior_prob else ""
        st.markdown(
            f'<div class="card-probabilidade{destaque}">'
            f'<div style="display:flex;align-items:center;gap:6px;'
            f'margin-bottom:6px;">'
            f'{html_escudo(nome_visitante)}'
            f'<span style="font-size:12px;color:var(--text-muted);">'
            f'{nome_visitante}</span></div>'
            f'<div style="font-size:24px;font-weight:700;">'
            f'{prob_fora:.2f}%</div>'
            f'</div>',
            unsafe_allow_html=True
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
        eh_pro_25 = usuario_eh_pro()

        classe_borrado = "" if eh_pro_25 else "conteudo-borrado"

        col1, col2 = st.columns(
            [4, 1]
        )

        with col1:
            st.markdown(
                f'<div class="{classe_borrado}">'
                f'<strong>Mais de 2,5 gols — {over25:.2f}%</strong>'
                f'</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                f'<div class="{classe_borrado}">',
                unsafe_allow_html=True
            )
            _renderizar_barra(
                over25
            )
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown(
                f'<div class="{classe_borrado}">'
                f'<span style="color:var(--text-muted);font-size:13px;">'
                f'{classificacao_over25} • {status_over25}</span>'
                f'</div>',
                unsafe_allow_html=True
            )

        with col2:
            if eh_pro_25:
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

        if not eh_pro_25:
            st.markdown(
                '<div style="text-align:center;margin-top:6px;">'
                '<span style="background:rgba(217,163,83,.12);'
                'border:1px solid rgba(217,163,83,.3);border-radius:8px;'
                'padding:6px 14px;color:var(--green);font-size:12px;">'
                '🔒 Desbloquear com PRO</span></div>',
                unsafe_allow_html=True
            )

    with st.container(
        border=True
    ):
        eh_pro_btts = usuario_eh_pro()

        classe_borrado_btts = "" if eh_pro_btts else "conteudo-borrado"

        col1, col2 = st.columns(
            [4, 1]
        )

        with col1:
            st.markdown(
                f'<div class="{classe_borrado_btts}">'
                f'<strong>Ambas marcam — {btts:.2f}%</strong>'
                f'</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                f'<div class="{classe_borrado_btts}">',
                unsafe_allow_html=True
            )
            _renderizar_barra(
                btts
            )
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown(
                f'<div class="{classe_borrado_btts}">'
                f'<span style="color:var(--text-muted);font-size:13px;">'
                f'{classificacao_btts} • {status_btts}</span>'
                f'</div>',
                unsafe_allow_html=True
            )

        with col2:
            if eh_pro_btts:
                _renderizar_status(
                    status_btts,
                    positivo=False
                )

        if not eh_pro_btts:
            st.markdown(
                '<div style="text-align:center;margin-top:6px;">'
                '<span style="background:rgba(217,163,83,.12);'
                'border:1px solid rgba(217,163,83,.3);border-radius:8px;'
                'padding:6px 14px;color:var(--green);font-size:12px;">'
                '🔒 Desbloquear com PRO</span></div>',
                unsafe_allow_html=True
            )

    st.caption(
        "⚠️ Análise estatística baseada em dados históricos, não "
        "é garantia de resultado. Aposta não é investimento."
    )

    st.page_link(
        "pages/4_📈_Resultados.py",
        label="📊 Ver histórico real de acertos do EntradaPro",
        use_container_width=True
    )