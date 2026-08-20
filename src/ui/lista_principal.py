"""
Componente visual: a nova tela principal, inspirada no Forebet/R10
Score - lista de jogos com Score, Odd e Value visíveis direto,
organizados por dia (abas Hoje/Amanhã/...).

Substitui a lista simples de "jogos futuros" por uma versão mais
densa de informação, com a identidade do EntradaPro.
"""

from datetime import datetime, date

import streamlit as st

from engines.match_list_service import construir_lista_jogos


DIAS_SEMANA = [
    "Segunda", "Terça", "Quarta", "Quinta",
    "Sexta", "Sábado", "Domingo",
]


@st.cache_data(ttl=600, show_spinner=False)
def _construir_lista_com_cache(dias_a_frente):
    return construir_lista_jogos(dias_a_frente=dias_a_frente)


def _rotulo_dia(data_jogo, hoje):
    dias_diferenca = (data_jogo - hoje).days

    if dias_diferenca == 0:
        return "Hoje"

    if dias_diferenca == 1:
        return "Amanhã"

    nome_dia = DIAS_SEMANA[data_jogo.weekday()]
    return f"{nome_dia} {data_jogo.day:02d}/{data_jogo.month:02d}"


def _agrupar_por_dia(jogos):
    grupos = {}

    for jogo in jogos:
        data_iso = jogo.get("data_iso", "")

        try:
            data_jogo = datetime.fromisoformat(
                data_iso.replace("Z", "+00:00")
            ).date()
        except (ValueError, AttributeError):
            continue

        grupos.setdefault(data_jogo, []).append(jogo)

    return dict(sorted(grupos.items()))


def _cor_do_score(score):
    if score >= 80:
        return "var(--green)"
    if score >= 60:
        return "#e6d3ae"
    return "var(--text-muted)"


def renderizar_lista_principal(callback_selecao):
    """
    Renderiza a nova lista principal de jogos. Se o usuário
    clicar em um jogo, chama callback_selecao(mandante, visitante)
    com os nomes exatos do dataset local.
    """
    try:
        resultado = _construir_lista_com_cache(dias_a_frente=7)
    except Exception:
        return

    if not resultado.get("sucesso"):
        return

    jogos = resultado.get("jogos", [])

    if not jogos:
        return

    quantidade_oportunidades = sum(
        1 for j in jogos if j.get("value_bet")
    )

    grupos_por_dia = _agrupar_por_dia(jogos)
    hoje = date.today()

    with st.container(border=True):
        col_titulo, col_badge = st.columns([3, 1.4])

        with col_titulo:
            st.markdown("### 🇧🇷 Brasileirão Série A")

        with col_badge:
            if quantidade_oportunidades > 0:
                st.markdown(
                    f'<div style="background:rgba(217,163,83,.12);'
                    f'border:1px solid rgba(217,163,83,.3);'
                    f'border-radius:20px;padding:6px 12px;'
                    f'color:var(--green);font-size:12px;'
                    f'text-align:center;">'
                    f'🔥 {quantidade_oportunidades} oportunidade(s) hoje'
                    f'</div>',
                    unsafe_allow_html=True
                )

        rotulos = [_rotulo_dia(dia, hoje) for dia in grupos_por_dia]
        abas = st.tabs(rotulos)

        for aba, (dia, jogos_do_dia) in zip(
            abas, grupos_por_dia.items()
        ):
            with aba:
                for jogo in jogos_do_dia:
                    horario = jogo.get("data_iso", "")[11:16]
                    score = jogo["entradapro_score"]
                    cor_score = _cor_do_score(score)

                    col_hora, col_jogo, col_score, col_odd, col_btn = (
                        st.columns([0.7, 2.3, 0.8, 0.8, 1])
                    )

                    with col_hora:
                        st.markdown(
                            f'<div style="color:#e6d3ae;font-size:12px;'
                            f'font-weight:600;padding-top:8px;">'
                            f'{horario}</div>',
                            unsafe_allow_html=True
                        )

                    with col_jogo:
                        st.markdown(
                            f'<div style="padding-top:8px;">'
                            f"{jogo['mandante']} x {jogo['visitante']}"
                            f'</div>',
                            unsafe_allow_html=True
                        )

                    with col_score:
                        st.markdown(
                            f'<div style="text-align:center;">'
                            f'<div style="font-size:9px;'
                            f'color:var(--text-muted);">SCORE</div>'
                            f'<div style="font-family:\'JetBrains Mono\','
                            f'monospace;font-weight:600;'
                            f'color:{cor_score};">{score}</div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )

                    with col_odd:
                        odd_texto = (
                            f"{jogo['odd']:.2f}" if jogo["odd"] else "—"
                        )
                        st.markdown(
                            f'<div style="text-align:center;">'
                            f'<div style="font-size:9px;'
                            f'color:var(--text-muted);">ODD</div>'
                            f'<div style="font-family:\'JetBrains Mono\','
                            f'monospace;">{odd_texto}</div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )

                    with col_btn:
                        if st.button(
                            "Analisar",
                            key=f"lista_principal_{jogo['fixture_id']}",
                            use_container_width=True,
                        ):
                            callback_selecao(
                                jogo["mandante"], jogo["visitante"]
                            )

                    if jogo.get("value_bet"):
                        st.caption(
                            f"💎 Value: +{jogo['edge']:.1f}% "
                            f"({jogo.get('casa_da_odd', '')})"
                        )

                    st.divider()
