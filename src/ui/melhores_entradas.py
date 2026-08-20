"""
Componente visual: "Melhores Entradas do Dia" - a Etapa B do
roteiro "EntradaPro Autônomo" em tela. Mostra automaticamente as
melhores oportunidades encontradas pela varredura, sem o usuário
precisar checar jogo por jogo.

Assim como os jogos futuros, é ADITIVO e com falha silenciosa: se
a varredura não funcionar por qualquer motivo, esta seção
simplesmente não aparece - o resto do site continua normal.
"""

import streamlit as st

from engines.opportunity_scanner import escanear_melhores_oportunidades


def renderizar_melhores_entradas():
    try:
        resultado = escanear_melhores_oportunidades(
            dias_a_frente=3, limite=5
        )
    except Exception:
        return

    if not resultado.get("sucesso"):
        return

    oportunidades = resultado.get("oportunidades", [])

    if not oportunidades:
        return

    with st.container(border=True):
        st.markdown("### 🔥 Melhores Entradas do Dia")

        st.caption(
            "Selecionadas automaticamente entre os próximos jogos "
            "do Brasileirão, comparando a probabilidade calculada "
            "com as odds reais do mercado."
        )

        for oportunidade in oportunidades:
            with st.container(border=True):
                col_info, col_metrica = st.columns([3, 1])

                with col_info:
                    st.markdown(
                        f"**{oportunidade['mandante']}** x "
                        f"**{oportunidade['visitante']}**"
                    )

                    st.caption(
                        f"{oportunidade['melhor_mercado']} · "
                        f"Odd {oportunidade['odd']:.2f}"
                        + (
                            f" ({oportunidade['casa_da_odd']})"
                            if oportunidade.get("casa_da_odd")
                            else ""
                        )
                    )

                    st.caption(
                        f"Confiança: {oportunidade['probabilidade']:.0f}% · "
                        f"{oportunidade['classificacao']}"
                    )

                with col_metrica:
                    st.metric(
                        "Value",
                        f"+{oportunidade['edge']:.1f}%"
                    )
