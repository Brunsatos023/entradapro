import streamlit as st


def renderizar_cabecalho(total_partidas_base=None):
    indicador_html = ""

    if total_partidas_base:
        indicador_html = (
            '<div class="hero-indicador">'
            f'{total_partidas_base} partidas do Brasileirão '
            'analisadas na base de dados'
            '</div>'
        )

    html = (
        '<div class="hero">'
        '<p class="hero-title">'
        'Entrada<span class="hero-highlight">Pro</span>'
        '</p>'
        '<p class="hero-subtitle">'
        'Football Intelligence · '
        'Análise inteligente de partidas, probabilidades '
        'e identificação de apostas de valor.'
        '</p>'
        f'{indicador_html}'
        '</div>'
    )

    st.markdown(
        html,
        unsafe_allow_html=True
    )


def renderizar_partida(
    nome_mandante,
    nome_visitante
):
    html = (
        '<div class="match-header">'
        '<div class="match-label">'
        'Análise da partida'
        '</div>'
        '<div class="match-name">'
        f'{nome_mandante} &nbsp;&nbsp; x &nbsp;&nbsp; '
        f'{nome_visitante}'
        '</div>'
        '</div>'
    )

    st.markdown(
        html,
        unsafe_allow_html=True
    )


def renderizar_estado_inicial():
    html = (
        '<div class="match-header">'
        '<div class="match-label">'
        'EntradaPro está pronto'
        '</div>'
        '<div class="match-name">'
        'Selecione os times e clique em '
        '<span style="color:#d9a353;">'
        '“Analisar partida”'
        '</span>'
        '</div>'
        '</div>'
    )

    st.markdown(
        html,
        unsafe_allow_html=True
    )


def renderizar_titulo_secao(titulo):
    html = (
        '<div class="section-title">'
        f'{titulo}'
        '</div>'
    )

    st.markdown(
        html,
        unsafe_allow_html=True
    )