"""
Página "Resultados EntradaPro" - histórico transparente de todas
as previsões feitas pelo sistema, com o resultado real (Green/Red)
e as estatísticas gerais (taxa de acerto, ROI, yield, odd média).

Item 22 da especificação original de layout de Bruno: "O histórico
deve ser transparente."
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from auth import (
    inicializar_banco,
    inicializar_estado_autenticacao,
    usuario_esta_autenticado,
)
from prediction_history_service import (
    verificar_previsoes_pendentes,
    obter_estatisticas_historico,
)
from db import conectar_banco


st.set_page_config(
    page_title="Resultados EntradaPro",
    page_icon="📊",
    layout="wide",
)

inicializar_banco()
inicializar_estado_autenticacao()

st.markdown("## 📊 Resultados EntradaPro")

st.caption(
    "Histórico transparente de todas as previsões feitas "
    "automaticamente pelo sistema, comparadas com o resultado real."
)

st.info(
    "Este histórico mostra os resultados reais, incluindo "
    "períodos negativos. Desempenho passado não garante "
    "resultado futuro. Aposta não é investimento."
)

if not usuario_esta_autenticado():
    st.info(
        "Faça login para acompanhar o histórico de previsões."
    )
    st.stop()

try:
    with st.spinner("Conferindo resultados mais recentes..."):
        verificar_previsoes_pendentes()
except Exception:
    pass

stats = obter_estatisticas_historico()

if stats["total"] == 0:
    st.info(
        "Ainda não há previsões conferidas o suficiente para "
        "gerar estatísticas. Volte em breve."
    )
    st.stop()

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total de previsões", stats["total"])

with col2:
    st.metric("Taxa de acerto", f"{stats['taxa_acerto']:.1f}%")

with col3:
    st.metric("ROI", f"{stats['roi']:.1f}%")

with col4:
    st.metric("Yield", f"{stats['yield_']:.1f}%")

with col5:
    st.metric("Odd média", f"{stats['odd_media']:.2f}")

st.divider()

st.markdown("### Últimas previsões conferidas")

with conectar_banco() as conexao:
    previsoes = conexao.execute(
        """
        SELECT mandante, visitante, mercado, odd, status,
               gols_casa_real, gols_visitante_real, verificado_em
        FROM previsoes
        WHERE status IN ('GREEN', 'RED', 'VOID')
        ORDER BY verificado_em DESC
        LIMIT 30
        """
    ).fetchall()

for previsao in previsoes:
    p = dict(previsao)

    emoji = {
        "GREEN": "🟢",
        "RED": "🔴",
        "VOID": "⚪",
    }.get(p["status"], "⚪")

    with st.container(border=True):
        col_jogo, col_status = st.columns([3, 1])

        with col_jogo:
            st.markdown(
                f"**{p['mandante']}** x **{p['visitante']}**"
            )
            st.caption(
                f"{p['mercado']} · Odd {p['odd']:.2f}"
                + (
                    f" · Placar: {p['gols_casa_real']}-"
                    f"{p['gols_visitante_real']}"
                    if p["gols_casa_real"] is not None
                    else ""
                )
            )

        with col_status:
            st.markdown(f"### {emoji} {p['status']}")
