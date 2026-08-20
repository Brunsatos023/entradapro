"""
Componente visual: lista de jogos futuros reais do Brasileirão
(via FixturesEngine), organizados por dia em abas (inspirado na
organização do R10 Score) - permitindo ao usuário clicar num
confronto real e já cair na análise histórica desses dois times,
sem precisar escolher manualmente nos menus.

Este componente é ADITIVO: se a busca falhar (sem chave de API,
sem internet, jogo indisponível), simplesmente não aparece nada
aqui - o restante do site (seleção manual) continua funcionando
normalmente.
"""

from datetime import datetime, date

import streamlit as st

from engines.fixtures_engine import buscar_jogos_futuros
from utils.nomes_times import encontrar_time_local


DIAS_SEMANA = [
    "Segunda", "Terça", "Quarta", "Quinta",
    "Sexta", "Sábado", "Domingo",
]


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


def renderizar_jogos_futuros(nomes_times_locais):
    """
    Mostra os próximos jogos reais do Brasileirão, organizados em
    abas por dia. Se o usuário clicar em "Analisar este jogo",
    retorna (mandante, visitante) com os nomes exatos do dataset
    local, prontos para alimentar o restante do fluxo de análise
    já existente.

    Retorna None se nada foi clicado (ou se a busca falhou / não
    há jogos disponíveis - falha silenciosa e segura).
    """
    resultado = buscar_jogos_futuros(dias_a_frente=7)

    if not resultado.get("sucesso"):
        return None

    jogos = resultado.get("jogos", [])

    if not jogos:
        return None

    grupos_por_dia = _agrupar_por_dia(jogos)

    if not grupos_por_dia:
        return None

    hoje = date.today()

    with st.container(border=True):
        st.markdown("### 🗓️ Próximos jogos do Brasileirão")

        st.caption(
            "Clique em um confronto real para já carregar a "
            "análise histórica dessas equipes."
        )

        rotulos = [
            _rotulo_dia(dia, hoje) for dia in grupos_por_dia
        ]

        abas = st.tabs(rotulos)

        for aba, (dia, jogos_do_dia) in zip(
            abas, grupos_por_dia.items()
        ):
            with aba:
                for jogo in jogos_do_dia:
                    mandante_local = encontrar_time_local(
                        jogo["mandante"], nomes_times_locais
                    )
                    visitante_local = encontrar_time_local(
                        jogo["visitante"], nomes_times_locais
                    )

                    horario = jogo.get("data_iso", "")[11:16]

                    col_horario, col_info, col_botao = st.columns(
                        [0.8, 3, 1]
                    )

                    with col_horario:
                        st.markdown(f"**{horario}**")

                    with col_info:
                        st.markdown(
                            f"{jogo['mandante']} x {jogo['visitante']}"
                        )

                    with col_botao:
                        disponivel = (
                            mandante_local and visitante_local
                        )

                        if st.button(
                            "Analisar" if disponivel else "Sem dados",
                            key=f"jogo_futuro_{jogo['fixture_id']}",
                            disabled=not disponivel,
                            use_container_width=True,
                        ):
                            return (mandante_local, visitante_local)

                    st.divider()

    return None
