import streamlit as st

from data_storage import carregar_json
from footballai_engine import FootballAIEngine
from engines.recommendation_engine import RecommendationEngine


ARQUIVO_PARTIDAS = "brasileirao_serie_a_2024.json"
JANELA_ANALISE = 5


st.set_page_config(
    page_title="FootballAI",
    page_icon="⚽",
    layout="wide"
)


def extrair_partidas(dados):
    """
    Extrai a lista de partidas do JSON completo
    ou aceita diretamente uma lista.
    """

    if isinstance(dados, list):
        return dados

    if isinstance(dados, dict):
        partidas = dados.get("response")

        if isinstance(partidas, list):
            return partidas

    raise ValueError(
        "O arquivo não possui uma lista válida de partidas."
    )


def extrair_times(partidas):
    """
    Extrai os times existentes nas partidas.

    Retorna:

    {
        team_id: team_name
    }
    """

    times = {}

    for partida in partidas:
        dados_times = partida.get(
            "teams",
            {}
        )

        mandante = dados_times.get(
            "home",
            {}
        )

        visitante = dados_times.get(
            "away",
            {}
        )

        mandante_id = mandante.get("id")
        mandante_nome = mandante.get("name")

        visitante_id = visitante.get("id")
        visitante_nome = visitante.get("name")

        if (
            mandante_id is not None
            and mandante_nome
        ):
            times[int(mandante_id)] = mandante_nome

        if (
            visitante_id is not None
            and visitante_nome
        ):
            times[int(visitante_id)] = visitante_nome

    return dict(
        sorted(
            times.items(),
            key=lambda item: item[1]
        )
    )


def encontrar_indice_time(
    ids_times,
    team_id_padrao
):
    """
    Encontra o índice de um time para definir
    uma seleção inicial no Streamlit.
    """

    try:
        return ids_times.index(
            team_id_padrao
        )
    except ValueError:
        return 0


def formatar_numero(valor, casas=2):
    try:
        return f"{float(valor):.{casas}f}"
    except (TypeError, ValueError):
        return "0.00"


def definir_risco(recomendacao):
    nivel = recomendacao.get(
        "nivel_confianca",
        "Baixa"
    )

    recomendado = recomendacao.get(
        "recomendado",
        False
    )

    if not recomendado:
        return "Alto"

    if nivel == "Alta":
        return "Baixo"

    if nivel == "Moderada":
        return "Médio"

    return "Alto"


def definir_icone_recomendacao(recomendacao):
    recomendado = recomendacao.get(
        "recomendado",
        False
    )

    nivel = recomendacao.get(
        "nivel_confianca",
        "Baixa"
    )

    if not recomendado:
        return "🔴"

    if nivel == "Alta":
        return "🟢"

    if nivel == "Moderada":
        return "🟡"

    return "🔴"


@st.cache_data
def carregar_base():
    """
    Carrega as partidas e identifica os times.

    O cache evita que o arquivo seja aberto novamente
    a cada interação da página.
    """

    dados = carregar_json(
        ARQUIVO_PARTIDAS
    )

    partidas = extrair_partidas(
        dados
    )

    times = extrair_times(
        partidas
    )

    return partidas, times


def gerar_analise(
    partidas,
    mandante_id,
    visitante_id
):
    """
    Executa os motores para o confronto escolhido.
    """

    analise_mandante = FootballAIEngine(
        partidas=partidas,
        team_id=mandante_id,
        janela=JANELA_ANALISE
    ).analisar()

    if analise_mandante.get("erro"):
        raise ValueError(
            "Erro na análise do mandante: "
            f"{analise_mandante['erro']}"
        )

    analise_visitante = FootballAIEngine(
        partidas=partidas,
        team_id=visitante_id,
        janela=JANELA_ANALISE
    ).analisar()

    if analise_visitante.get("erro"):
        raise ValueError(
            "Erro na análise do visitante: "
            f"{analise_visitante['erro']}"
        )

    resultado = RecommendationEngine(
        analise_mandante=analise_mandante,
        analise_visitante=analise_visitante
    ).analisar()

    if resultado.get("erro"):
        raise ValueError(
            "Erro na RecommendationEngine: "
            f"{resultado['erro']}"
        )

    return resultado


def exibir_time(nome, dados_time):
    st.subheader(nome)

    coluna_1, coluna_2 = st.columns(2)

    with coluna_1:
        st.metric(
            label="Inteligência FootballAI",
            value=formatar_numero(
                dados_time.get(
                    "intelligence_score",
                    0.0
                )
            )
        )

        st.metric(
            label="Forma",
            value=formatar_numero(
                dados_time.get(
                    "nota_forma",
                    0.0
                )
            )
        )

    with coluna_2:
        st.metric(
            label="Rating",
            value=formatar_numero(
                dados_time.get(
                    "rating",
                    0.0
                )
            )
        )

        st.metric(
            label="Pulse",
            value=formatar_numero(
                dados_time.get(
                    "pulse_score",
                    0.0
                )
            )
        )

    st.write(
        "**Categoria do rating:** "
        f"{dados_time.get('categoria_rating', 'Não definida')}"
    )

    st.write(
        "**Tendência:** "
        f"{dados_time.get('tendencia', 'Não definida')}"
    )


def exibir_recomendacao(recomendacao):
    mercado = recomendacao.get(
        "mercado",
        "Mercado não identificado"
    )

    recomendado = recomendacao.get(
        "recomendado",
        False
    )

    indice_estatistico = recomendacao.get(
        "indice_estatistico",
        0.0
    )

    ajuste_contextual = recomendacao.get(
        "ajuste_contextual",
        0.0
    )

    indice_confianca = recomendacao.get(
        "indice_confianca",
        0.0
    )

    nivel_confianca = recomendacao.get(
        "nivel_confianca",
        "Baixa"
    )

    risco = definir_risco(
        recomendacao
    )

    icone = definir_icone_recomendacao(
        recomendacao
    )

    st.subheader(
        f"{icone} {mercado}"
    )

    coluna_1, coluna_2, coluna_3 = st.columns(3)

    with coluna_1:
        st.metric(
            label="Recomendação",
            value=(
                "SIM"
                if recomendado
                else "NÃO"
            )
        )

    with coluna_2:
        st.metric(
            label="Confiança final",
            value=(
                f"{formatar_numero(indice_confianca)}%"
            )
        )

    with coluna_3:
        st.metric(
            label="Risco estimado",
            value=risco
        )

    progresso = min(
        max(
            float(indice_confianca) / 100,
            0.0
        ),
        1.0
    )

    st.progress(
        progresso
    )

    st.write(
        "**Índice estatístico:** "
        f"{formatar_numero(indice_estatistico)}%"
    )

    st.write(
        "**Ajuste contextual:** "
        f"{float(ajuste_contextual):+.2f}"
    )

    st.write(
        "**Nível de confiança:** "
        f"{nivel_confianca}"
    )

    motivos = recomendacao.get(
        "motivos",
        []
    )

    with st.expander(
        "Ver motivos da recomendação"
    ):
        if motivos:
            for motivo in motivos:
                st.write(
                    f"- {motivo}"
                )
        else:
            st.write(
                "Nenhum motivo informado."
            )

    alertas = recomendacao.get(
        "alertas",
        []
    )

    if alertas:
        with st.expander(
            "Ver alertas"
        ):
            for alerta in alertas:
                st.warning(
                    alerta
                )
    else:
        st.success(
            "Nenhum alerta identificado."
        )


def exibir_resultado(
    resultado,
    mandante_nome,
    visitante_nome
):
    dados_base = resultado.get(
        "dados_base",
        {}
    )

    recomendacoes = resultado.get(
        "recomendacoes",
        []
    )

    st.divider()

    st.header(
        f"{mandante_nome} x {visitante_nome}"
    )

    st.caption(
        f"Janela estatística: últimos "
        f"{JANELA_ANALISE} jogos"
    )

    st.success(
        "Análise concluída com sucesso."
    )

    st.divider()

    st.header(
        "Resumo dos times"
    )

    coluna_mandante, coluna_visitante = st.columns(2)

    with coluna_mandante:
        with st.container(
            border=True
        ):
            exibir_time(
                mandante_nome,
                dados_base.get(
                    "mandante",
                    {}
                )
            )

    with coluna_visitante:
        with st.container(
            border=True
        ):
            exibir_time(
                visitante_nome,
                dados_base.get(
                    "visitante",
                    {}
                )
            )

    st.divider()

    st.header(
        "Recomendações de mercado"
    )

    if not recomendacoes:
        st.warning(
            "Nenhuma recomendação foi gerada."
        )

    for recomendacao in recomendacoes:
        with st.container(
            border=True
        ):
            exibir_recomendacao(
                recomendacao
            )

    st.divider()

    st.warning(
        "As análises do FootballAI são baseadas em "
        "dados estatísticos históricos. Nenhuma "
        "recomendação representa garantia de acerto "
        "ou retorno financeiro."
    )


def main():
    st.title(
        "⚽ FootballAI"
    )

    st.caption(
        "Análise estatística inteligente para "
        "mercados de futebol."
    )

    st.divider()

    try:
        partidas, times = carregar_base()

        if len(times) < 2:
            st.error(
                "Não foram encontrados times suficientes "
                "para formar um confronto."
            )
            return

        ids_times = list(
            times.keys()
        )

        indice_flamengo = encontrar_indice_time(
            ids_times,
            127
        )

        indice_palmeiras = encontrar_indice_time(
            ids_times,
            121
        )

        st.header(
            "Selecione o confronto"
        )

        with st.form(
            "formulario_confronto"
        ):
            coluna_mandante, coluna_visitante = st.columns(2)

            with coluna_mandante:
                mandante_id = st.selectbox(
                    label="Mandante",
                    options=ids_times,
                    index=indice_flamengo,
                    format_func=lambda team_id: times[
                        team_id
                    ]
                )

            with coluna_visitante:
                visitante_id = st.selectbox(
                    label="Visitante",
                    options=ids_times,
                    index=indice_palmeiras,
                    format_func=lambda team_id: times[
                        team_id
                    ]
                )

            analisar = st.form_submit_button(
                label="Analisar confronto",
                type="primary",
                use_container_width=True
            )

        st.caption(
            f"Times disponíveis: {len(times)}"
        )

        if analisar:
            if mandante_id == visitante_id:
                st.error(
                    "O mandante e o visitante precisam "
                    "ser times diferentes."
                )

                return

            mandante_nome = times[
                mandante_id
            ]

            visitante_nome = times[
                visitante_id
            ]

            with st.spinner(
                "FootballAI está analisando o confronto..."
            ):
                resultado = gerar_analise(
                    partidas=partidas,
                    mandante_id=mandante_id,
                    visitante_id=visitante_id
                )

            st.session_state[
                "resultado_analise"
            ] = resultado

            st.session_state[
                "mandante_nome"
            ] = mandante_nome

            st.session_state[
                "visitante_nome"
            ] = visitante_nome

        resultado_salvo = st.session_state.get(
            "resultado_analise"
        )

        if resultado_salvo:
            exibir_resultado(
                resultado=resultado_salvo,
                mandante_nome=st.session_state.get(
                    "mandante_nome",
                    "Mandante"
                ),
                visitante_nome=st.session_state.get(
                    "visitante_nome",
                    "Visitante"
                )
            )
        else:
            st.info(
                "Selecione o mandante e o visitante e "
                "clique em Analisar confronto."
            )

    except FileNotFoundError:
        st.error(
            "O arquivo de partidas não foi encontrado."
        )

    except ValueError as erro:
        st.error(
            str(erro)
        )

    except Exception as erro:
        st.error(
            "Erro inesperado ao gerar a análise."
        )

        st.exception(
            erro
        )


if __name__ == "__main__":
    main()