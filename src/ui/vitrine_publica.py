"""
Componente visual: vitrine pública de "Análises em Destaque" -
visível ANTES de logar, usando partidas reais do histórico
(2024). Não depende de nenhuma API externa, então sempre funciona
e sempre mostra dado real.

Organizada em abas (Destaques / Ao vivo / Meus times), estilo
Forebet/R10 Score, com jogos em linhas densas (estrela, escudo,
nomes, data, Score) em vez de cards grandes separados.
"""

import streamlit as st

from engines.showcase_service import construir_vitrine_analises
from ui.escudos_times import html_escudo

import logging
logger = logging.getLogger("entradapro.dashboard")


@st.cache_data(ttl=3600, show_spinner=False)
def _construir_vitrine_com_cache(quantidade):
    return construir_vitrine_analises(quantidade=quantidade)


def _renderizar_linha_jogo(analise, indice, usuario_logado, usuario_id):
    if usuario_logado:
        from favoritos_service import eh_favorito, alternar_favorito

        col_estrela, col_jogo, col_data, col_score = st.columns(
            [0.35, 2.4, 0.9, 0.6]
        )

        with col_estrela:
            favorito_atual = eh_favorito(usuario_id, analise["mandante"])
            icone = "⭐" if favorito_atual else "☆"

            if st.button(icone, key=f"fav_vitrine_{indice}"):
                alternar_favorito(usuario_id, analise["mandante"])
                st.rerun()
    else:
        col_estrela, col_jogo, col_data, col_score = st.columns(
            [0.35, 2.4, 0.9, 0.6]
        )

        with col_estrela:
            st.markdown(
                '<span style="color:var(--text-muted);">☆</span>',
                unsafe_allow_html=True
            )

    with col_jogo:
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:6px;'
            f'padding-top:6px;">'
            f'{html_escudo(analise["mandante"])}'
            f'<span style="font-size:13px;">{analise["mandante"]}</span>'
            f'<span style="color:var(--text-muted);font-size:12px;">x</span>'
            f'{html_escudo(analise["visitante"])}'
            f'<span style="font-size:13px;">{analise["visitante"]}</span>'
            f'</div>',
            unsafe_allow_html=True
        )

    with col_data:
        st.markdown(
            f'<div style="padding-top:8px;color:var(--text-muted);'
            f'font-size:11px;">{analise["data"]}</div>',
            unsafe_allow_html=True
        )

    with col_score:
        st.markdown(
            f'<div style="padding-top:6px;text-align:center;">'
            f'<span style="background:var(--bg-card);color:var(--green);'
            f'font-size:12px;padding:3px 9px;border-radius:6px;'
            f'font-family:\'JetBrains Mono\',monospace;">'
            f'{analise["entradapro_score"]}</span></div>',
            unsafe_allow_html=True
        )

    st.markdown(
        '<div style="border-bottom:1px solid var(--border);'
        'margin:4px 0 8px 0;"></div>',
        unsafe_allow_html=True
    )


def renderizar_vitrine_publica():
    try:
        resultado = _construir_vitrine_com_cache(quantidade=8)
    except Exception as erro:
        logger.exception("Erro na vitrine publica: %s", erro)
        return

    if not resultado.get("sucesso"):
        return

    analises = resultado.get("analises", [])

    if not analises:
        return

    from auth import usuario_esta_autenticado

    usuario_logado = usuario_esta_autenticado()
    usuario_id = (
        st.session_state.usuario["id"] if usuario_logado else None
    )

    favoritos_atuais = []
    if usuario_logado:
        try:
            from favoritos_service import listar_favoritos
            favoritos_atuais = listar_favoritos(usuario_id)
        except Exception:
            favoritos_atuais = []

    with st.container(border=True):
        aba_destaques, aba_ao_vivo, aba_meus_times = st.tabs(
            ["Destaques", "Ao vivo", "Meus times"]
        )

        with aba_destaques:
            st.markdown(
                '<div style="color:var(--text-muted);font-size:11px;'
                'font-weight:600;margin-bottom:8px;">'
                '🇧🇷 BRASILEIRÃO SÉRIE A</div>',
                unsafe_allow_html=True
            )

            for indice, analise in enumerate(analises):
                _renderizar_linha_jogo(
                    analise, indice, usuario_logado, usuario_id
                )

            st.caption(
                "📊 Exemplos ilustrativos da análise com dados reais, "
                "não uma taxa de acerto. Veja o histórico completo "
                "na página Resultados."
            )

        with aba_ao_vivo:
            st.info(
                "🔒 Jogos ao vivo dependem de uma temporada atual "
                "da API-Football, ainda não disponível no plano "
                "contratado. Em breve."
            )

        with aba_meus_times:
            if not usuario_logado:
                st.info(
                    "Faça login e marque times com ⭐ para "
                    "acompanhá-los aqui."
                )
            elif not favoritos_atuais:
                st.info(
                    "Você ainda não marcou nenhum time favorito. "
                    "Clique na ⭐ ao lado de um time na aba "
                    "\"Destaques\" para adicioná-lo aqui."
                )
            else:
                analises_filtradas = [
                    a for a in analises
                    if a["mandante"] in favoritos_atuais
                    or a["visitante"] in favoritos_atuais
                ]

                if not analises_filtradas:
                    st.info(
                        "Nenhuma análise em destaque envolve seus "
                        "times favoritos no momento."
                    )
                else:
                    for indice, analise in enumerate(analises_filtradas):
                        _renderizar_linha_jogo(
                            analise, f"mt_{indice}",
                            usuario_logado, usuario_id
                        )
