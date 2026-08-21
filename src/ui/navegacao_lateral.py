"""
Componente visual: navegação lateral estilo Forebet/R10 - lista de
times favoritos do usuário e as ligas disponíveis. Fica na barra
lateral, logo abaixo da marca.
"""

import streamlit as st

from ui.escudos_times import html_escudo

import logging
logger = logging.getLogger("entradapro.dashboard")


def renderizar_navegacao_lateral(usuario_logado, usuario_id):
    if usuario_logado:
        try:
            from favoritos_service import listar_favoritos
            favoritos = listar_favoritos(usuario_id)
        except Exception as erro:
            logger.exception("Erro ao listar favoritos: %s", erro)
            favoritos = []

        st.markdown(
            '<div style="color:var(--text-muted);font-size:10px;'
            'letter-spacing:.05em;margin-bottom:6px;">'
            '⭐ TIMES FAVORITOS</div>',
            unsafe_allow_html=True
        )

        if favoritos:
            for time in favoritos:
                st.markdown(
                    f'<div style="display:flex;align-items:center;'
                    f'gap:6px;padding:4px 2px;color:var(--text-primary);'
                    f'font-size:12px;">'
                    f'{html_escudo(time)}<span>{time}</span></div>',
                    unsafe_allow_html=True
                )
        else:
            st.markdown(
                '<div style="color:var(--text-muted);font-size:11px;'
                'padding:2px;">Marque times com ⭐ nas listas de '
                'jogos para vê-los aqui.</div>',
                unsafe_allow_html=True
            )

        st.markdown(
            '<div style="height:1px;background:var(--border);'
            'margin:10px 0;"></div>',
            unsafe_allow_html=True
        )

    st.markdown(
        '<div style="color:var(--text-muted);font-size:10px;'
        'letter-spacing:.05em;margin-bottom:6px;">LIGAS</div>'
        '<div style="display:flex;align-items:center;gap:6px;'
        'color:var(--green);font-size:12px;padding:5px 4px;'
        'background:var(--bg-card);border-radius:6px;'
        'margin-bottom:2px;">'
        '<img src="https://media.api-sports.io/football/leagues/71.png" '
        'style="width:18px;height:18px;object-fit:contain;" '
        'onerror="this.style.display=\'none\';" />'
        'Brasileirão Série A</div>'
        '<div style="color:var(--text-muted);font-size:12px;'
        'padding:5px 4px;">🌍 Outras (em breve)</div>',
        unsafe_allow_html=True
    )

    try:
        from ui.tabela_classificacao import renderizar_tabela_classificacao
        renderizar_tabela_classificacao()
    except Exception as erro:
        logger.exception("Erro ao renderizar tabela de classificacao: %s", erro)

    st.divider()
