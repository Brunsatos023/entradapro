"""
Componente visual: vitrine pública de "Análises em Destaque" -
visível ANTES de logar, usando partidas reais do histórico
(2024). Não depende de nenhuma API externa, então sempre funciona
e sempre mostra dado real.

Este é o "uau" da primeira tela: mostra a profundidade da análise
(EntradaPro Score, probabilidades) lado a lado com o placar real
que aconteceu - sem prometer taxa de acerto (isso fica só na
página de Resultados, de forma transparente).
"""

import streamlit as st

from engines.showcase_service import construir_vitrine_analises

import logging
logger = logging.getLogger("entradapro.dashboard")


@st.cache_data(ttl=3600, show_spinner=False)
def _construir_vitrine_com_cache(quantidade):
    return construir_vitrine_analises(quantidade=quantidade)


def renderizar_vitrine_publica():
    try:
        resultado = _construir_vitrine_com_cache(quantidade=5)
    except Exception as erro:
        logger.exception("Erro na vitrine publica: %s", erro)
        return

    if not resultado.get("sucesso"):
        return

    analises = resultado.get("analises", [])

    if not analises:
        return

    with st.container(border=True):
        st.markdown("### 🎯 Análises em Destaque")

        st.caption(
            "Partidas reais do Brasileirão, com o EntradaPro Score "
            "calculado e o resultado que realmente aconteceu."
        )

        for analise in analises:
            col_jogo, col_score, col_placar = st.columns([2.2, 1, 1])

            with col_jogo:
                st.markdown(
                    f"**{analise['mandante']}** x "
                    f"**{analise['visitante']}**"
                )
                st.caption(analise["data"])

            with col_score:
                st.markdown(
                    f'<div style="text-align:center;">'
                    f'<div style="font-size:9px;color:var(--text-muted);">'
                    f'ENTRADAPRO SCORE</div>'
                    f'<div style="font-family:\'JetBrains Mono\',monospace;'
                    f'font-weight:600;font-size:18px;color:var(--green);">'
                    f'{analise["entradapro_score"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            with col_placar:
                st.markdown(
                    f'<div style="text-align:center;">'
                    f'<div style="font-size:9px;color:var(--text-muted);">'
                    f'PLACAR REAL</div>'
                    f'<div style="font-family:\'JetBrains Mono\',monospace;'
                    f'font-weight:600;font-size:16px;">'
                    f'{analise["placar_real"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            st.divider()

        st.caption(
            "📊 Estes são exemplos ilustrativos da análise, não "
            "uma taxa de acerto. Veja o histórico real e completo "
            "na página Resultados."
        )
