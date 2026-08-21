"""
Componente visual: tabela de classificação do Brasileirão na
barra lateral, calculada de verdade a partir do dataset
histórico (não depende da API bloqueada).
"""

import streamlit as st

from engines.standings_service import calcular_tabela_classificacao
from ui.escudos_times import html_escudo

import logging
logger = logging.getLogger("entradapro.dashboard")


@st.cache_data(ttl=86400, show_spinner=False)
def _calcular_tabela_com_cache():
    return calcular_tabela_classificacao()


def renderizar_tabela_classificacao():
    try:
        resultado = _calcular_tabela_com_cache()
    except Exception as erro:
        logger.exception("Erro ao calcular tabela: %s", erro)
        return

    if not resultado.get("sucesso"):
        return

    tabela = resultado.get("tabela", [])

    if not tabela:
        return

    with st.expander("📊 Tabela — Brasileirão Série A", expanded=False):
        st.markdown(
            '<div style="display:flex;font-size:10px;'
            'color:var(--text-muted);padding:2px 4px;'
            'font-weight:600;">'
            '<div style="width:22px;">#</div>'
            '<div style="flex:1;">Time</div>'
            '<div style="width:28px;text-align:center;">Pts</div>'
            '<div style="width:28px;text-align:center;">J</div>'
            '<div style="width:32px;text-align:center;">+/-</div>'
            '</div>',
            unsafe_allow_html=True
        )

        for linha in tabela:
            cor_posicao = "var(--text-muted)"
            if linha["posicao"] <= 4:
                cor_posicao = "var(--green)"
            elif linha["posicao"] >= 17:
                cor_posicao = "var(--red)"

            st.markdown(
                f'<div style="display:flex;align-items:center;'
                f'font-size:11px;padding:4px;border-bottom:1px solid '
                f'var(--border);">'
                f'<div style="width:22px;color:{cor_posicao};'
                f'font-weight:700;">{linha["posicao"]}</div>'
                f'<div style="flex:1;display:flex;align-items:center;'
                f'gap:5px;overflow:hidden;">'
                f'{html_escudo(linha["time"], tamanho=16)}'
                f'<span style="white-space:nowrap;overflow:hidden;'
                f'text-overflow:ellipsis;">{linha["time"]}</span>'
                f'</div>'
                f'<div style="width:28px;text-align:center;'
                f'font-weight:700;color:var(--text-primary);">'
                f'{linha["pontos"]}</div>'
                f'<div style="width:28px;text-align:center;'
                f'color:var(--text-muted);">{linha["jogos"]}</div>'
                f'<div style="width:32px;text-align:center;'
                f'color:var(--text-muted);">'
                f'{linha["saldo_gols"]:+d}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

        st.caption(
            "🟢 G-4 · 🔴 Z-4 · dados históricos 2024"
        )
