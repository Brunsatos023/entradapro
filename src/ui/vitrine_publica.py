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
from ui.escudos_times import html_escudo
from auth import usuario_esta_autenticado
from favoritos_service import eh_favorito, alternar_favorito

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

        st.write("")

        usuario_logado = usuario_esta_autenticado()
        usuario_id = (
            st.session_state.usuario["id"]
            if usuario_logado else None
        )

        for indice, analise in enumerate(analises):
            with st.container(border=True):
                col_estrela, col_jogo, col_score, col_placar = (
                    st.columns([0.4, 2.0, 1, 1])
                )

                with col_estrela:
                    if usuario_logado:
                        favorito_atual = eh_favorito(
                            usuario_id, analise["mandante"]
                        )
                        icone = "⭐" if favorito_atual else "☆"

                        if st.button(
                            icone,
                            key=f"fav_vitrine_{indice}",
                        ):
                            alternar_favorito(
                                usuario_id, analise["mandante"]
                            )
                            st.rerun()
                    else:
                        st.markdown(
                            '<span style="color:var(--text-muted);">'
                            '☆</span>',
                            unsafe_allow_html=True
                        )

                with col_jogo:
                    st.markdown(
                        f'<div style="display:flex;align-items:center;'
                        f'gap:8px;">'
                        f'{html_escudo(analise["mandante"])}'
                        f'<span>{analise["mandante"]}</span>'
                        f'<span style="color:var(--text-muted);">x</span>'
                        f'{html_escudo(analise["visitante"])}'
                        f'<span>{analise["visitante"]}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                    st.caption(analise["data"])

                with col_score:
                    st.markdown(
                        f'<div style="text-align:center;">'
                        f'<div style="font-size:9px;'
                        f'color:var(--text-muted);">'
                        f'ENTRADAPRO SCORE</div>'
                        f'<div style="font-family:\'JetBrains Mono\','
                        f'monospace;font-weight:600;font-size:18px;'
                        f'color:var(--green);">'
                        f'{analise["entradapro_score"]}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

                with col_placar:
                    st.markdown(
                        f'<div style="text-align:center;">'
                        f'<div style="font-size:9px;'
                        f'color:var(--text-muted);">'
                        f'PLACAR REAL</div>'
                        f'<div style="font-family:\'JetBrains Mono\','
                        f'monospace;font-weight:600;font-size:16px;">'
                        f'{analise["placar_real"]}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

            st.write("")

        st.caption(
            "📊 Estes são exemplos ilustrativos da análise, não "
            "uma taxa de acerto. Veja o histórico real e completo "
            "na página Resultados."
        )
