"""
Componente visual: lista de jogos futuros reais do Brasileirão
(via FixturesEngine), permitindo ao usuário clicar num confronto
real e já cair na análise histórica desses dois times - sem
precisar escolher manualmente nos menus.

Este componente é ADITIVO: se a busca falhar (sem chave de API,
sem internet, jogo indisponível), simplesmente não aparece nada
aqui - o restante do site (seleção manual) continua funcionando
normalmente.
"""

import unicodedata

import streamlit as st

from engines.fixtures_engine import buscar_jogos_futuros


def _normalizar_nome(nome):
    """
    Remove acentos e caixa para comparar nomes de times com
    segurança (ex: "São Paulo" da API vs "Sao Paulo" do dataset
    local precisam ser reconhecidos como o mesmo time).
    """
    sem_acento = unicodedata.normalize("NFKD", str(nome or ""))
    sem_acento = "".join(
        c for c in sem_acento if not unicodedata.combining(c)
    )
    return sem_acento.strip().lower()


def _encontrar_time_local(nome_api, nomes_times_locais):
    """
    Tenta casar o nome de um time vindo da API-Football com o
    nome correspondente no dataset local. Retorna o nome local
    exato (para reaproveitar toda a análise já existente) ou None
    se esse time não estiver no dataset local.
    """
    alvo = _normalizar_nome(nome_api)

    for nome_local in nomes_times_locais:
        candidato = _normalizar_nome(nome_local)

        if alvo == candidato:
            return nome_local

        # Casamento parcial (ex: "Atletico-MG" vs "Atletico
        # Mineiro", ou nomes com sufixo tipo "EC", "DA Gama")
        if alvo in candidato or candidato in alvo:
            return nome_local

    return None


def renderizar_jogos_futuros(nomes_times_locais):
    """
    Mostra os próximos jogos reais do Brasileirão. Se o usuário
    clicar em "Analisar este jogo", retorna (mandante, visitante)
    com os nomes exatos do dataset local, prontos para alimentar
    o restante do fluxo de análise já existente.

    Retorna None se nada foi clicado (ou se a busca falhou / não
    há jogos disponíveis - falha silenciosa e segura).
    """
    resultado = buscar_jogos_futuros(dias_a_frente=7)

    if not resultado.get("sucesso"):
        return None

    jogos = resultado.get("jogos", [])

    if not jogos:
        return None

    with st.container(border=True):
        st.markdown("### 🗓️ Próximos jogos do Brasileirão")

        st.caption(
            "Clique em um confronto real para já carregar a "
            "análise histórica dessas equipes."
        )

        for jogo in jogos:
            mandante_local = _encontrar_time_local(
                jogo["mandante"], nomes_times_locais
            )
            visitante_local = _encontrar_time_local(
                jogo["visitante"], nomes_times_locais
            )

            col_info, col_botao = st.columns([3, 1])

            with col_info:
                st.markdown(
                    f"**{jogo['mandante']}** x **{jogo['visitante']}**"
                )
                st.caption(jogo.get("data_iso", "")[:16].replace("T", " "))

            with col_botao:
                disponivel = mandante_local and visitante_local

                if st.button(
                    "Analisar" if disponivel else "Sem dados",
                    key=f"jogo_futuro_{jogo['fixture_id']}",
                    disabled=not disponivel,
                    use_container_width=True,
                ):
                    return (mandante_local, visitante_local)

    return None
