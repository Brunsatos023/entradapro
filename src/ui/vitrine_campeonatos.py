"""
Componente visual: vitrine de múltiplos campeonatos (Champions,
Premier League, La Liga, etc.), com indicador de jogo ao vivo.

Puramente informativo - sem análise/probabilidade/Value, já que
o EntradaPro só tem dados históricos suficientes para o
Brasileirão Série A por enquanto.
"""

import streamlit as st

from access_control import usuario_eh_pro, renderizar_bloqueio_pro
from engines.multi_league_service import buscar_vitrine_campeonatos


@st.cache_data(ttl=900, show_spinner=False)
def _buscar_vitrine_com_cache(dias_a_frente):
    return buscar_vitrine_campeonatos(dias_a_frente=dias_a_frente)


def renderizar_vitrine_campeonatos():
    if not usuario_eh_pro():
        with st.container(border=True):
            st.markdown("### 🌍 Outros Campeonatos")
            renderizar_bloqueio_pro(
                titulo="Vitrine de campeonatos internacionais",
                mensagem=(
                    "Acompanhe Champions League, Premier League, "
                    "La Liga e outros — disponível para assinantes PRO."
                )
            )
        return

    try:
        resultado = _buscar_vitrine_com_cache(dias_a_frente=3)
    except Exception:
        return

    if not resultado.get("sucesso"):
        return

    campeonatos = resultado.get("campeonatos", [])

    if not campeonatos:
        return

    with st.container(border=True):
        st.markdown("### 🌍 Outros Campeonatos")

        st.caption(
            "Exibição informativa — sem análise EntradaPro "
            "(disponível apenas para o Brasileirão Série A por enquanto)."
        )

        nomes_abas = [c["nome"] for c in campeonatos]
        abas = st.tabs(nomes_abas)

        for aba, campeonato in zip(abas, campeonatos):
            with aba:
                for jogo in campeonato["jogos"][:8]:
                    horario = jogo.get("data_iso", "")[11:16]

                    col_horario, col_jogo, col_placar = st.columns(
                        [0.8, 2.5, 1]
                    )

                    with col_horario:
                        if jogo.get("ao_vivo"):
                            st.markdown("🔴 **AO VIVO**")
                        else:
                            st.markdown(f"**{horario}**")

                    with col_jogo:
                        st.markdown(
                            f"{jogo['mandante']} x {jogo['visitante']}"
                        )

                    with col_placar:
                        if (
                            jogo.get("ao_vivo")
                            or jogo.get("encerrado")
                        ):
                            gc = jogo.get("gols_casa")
                            gv = jogo.get("gols_visitante")
                            if gc is not None and gv is not None:
                                st.markdown(f"**{gc} - {gv}**")

                    st.divider()
