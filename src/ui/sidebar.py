import streamlit as st


def renderizar_sidebar(
    nomes_times,
    indice_mandante=0,
    indice_visitante=1
):
    st.sidebar.markdown("## ⚽ Configuração")

    nome_mandante = st.sidebar.selectbox(
        "Mandante",
        nomes_times,
        index=indice_mandante
    )

    nome_visitante = st.sidebar.selectbox(
        "Visitante",
        nomes_times,
        index=indice_visitante
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💰 Odds analisadas")

    odd_over15 = st.sidebar.number_input(
        "Mais de 1,5 gols",
        min_value=1.01,
        max_value=20.00,
        value=1.40,
        step=0.01
    )

    odd_btts = st.sidebar.number_input(
        "Ambas marcam — Sim",
        min_value=1.01,
        max_value=20.00,
        value=1.85,
        step=0.01
    )

    analisar = st.sidebar.button(
        "Analisar partida",
        use_container_width=True,
        type="primary"
    )

    return {
        "mandante": nome_mandante,
        "visitante": nome_visitante,
        "odd_over15": odd_over15,
        "odd_btts": odd_btts,
        "analisar": analisar
    }