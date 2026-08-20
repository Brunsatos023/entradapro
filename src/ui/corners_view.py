"""
Componente visual: análise de escanteios sob demanda. Diferente
dos outros mercados (que já vêm calculados automaticamente), este
precisa de um clique explícito do usuário - porque busca dados
direto na API-Football (custo de chamadas mais alto que os
outros mercados, que usam o dataset local já carregado).

Reservado para assinantes PRO: além de ser um benefício a mais do
plano pago, limita o uso dessa função mais cara a quem realmente
está pagando pelo serviço.
"""

import streamlit as st

from access_control import usuario_eh_pro, renderizar_bloqueio_pro
from engines.corners_engine import analisar_corners


def renderizar_secao_corners(id_mandante, id_visitante):
    st.markdown("### 🚩 Escanteios")

    if not usuario_eh_pro():
        renderizar_bloqueio_pro(
            titulo="Análise de escanteios",
            mensagem=(
                "Disponível para assinantes PRO. Busca dados "
                "detalhados direto na fonte para cada partida."
            )
        )
        return

    st.caption(
        "Este mercado busca dados em tempo real (não usa o "
        "histórico já carregado) - por isso é sob demanda."
    )

    with st.expander("Definir odd (opcional)"):
        odd_corners = st.number_input(
            "Odd — Mais de 9,5 escanteios",
            min_value=1.01,
            max_value=20.00,
            value=1.90,
            step=0.01,
            format="%.2f",
            key="odd_corners"
        )

    if st.button(
        "🔍 Buscar análise de escanteios",
        key="buscar_corners"
    ):
        with st.spinner("Buscando dados de escanteios..."):
            try:
                resultado = analisar_corners(
                    id_mandante=id_mandante,
                    id_visitante=id_visitante,
                    odd_over_corners=odd_corners,
                )
            except Exception as erro:
                st.error(f"Não foi possível buscar os dados: {erro}")
                return

        if not resultado.get("sucesso"):
            st.warning(resultado.get("mensagem", "Sem dados disponíveis."))
            return

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Média mandante", f"{resultado['media_casa']:.1f}"
            )

        with col2:
            st.metric(
                "Média visitante", f"{resultado['media_fora']:.1f}"
            )

        with col3:
            st.metric(
                f"Prob. +{resultado['linha']} escanteios",
                f"{resultado['probabilidade_over']:.0f}%"
            )

        valor = resultado.get("resultado_value")

        if valor:
            if valor.get("value_bet"):
                st.success(
                    f"💎 Value detectado — Edge: {valor['edge']:.1f}%"
                )
            else:
                st.info(
                    f"Sem value nesta odd — Edge: {valor['edge']:.1f}%"
                )
