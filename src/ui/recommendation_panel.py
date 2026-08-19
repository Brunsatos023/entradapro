import streamlit as st


def _formatar_percentual(valor):
    """Converte um valor numérico para percentual legível."""
    try:
        return f"{float(valor):.1f}%"
    except (TypeError, ValueError):
        return "N/D"


def _formatar_ajuste(valor):
    """Formata o ajuste contextual com sinal positivo ou negativo."""
    try:
        return f"{float(valor):+.2f} pts"
    except (TypeError, ValueError):
        return "N/D"


def _formatar_odd(valor):
    """Formata uma odd com duas casas decimais."""
    try:
        return f"{float(valor):.2f}"
    except (TypeError, ValueError):
        return "N/D"


def _formatar_valor_com_sinal(valor):
    """Formata percentuais positivos e negativos com sinal."""
    try:
        return f"{float(valor):+.2f}%"
    except (TypeError, ValueError):
        return "N/D"


def _obter_icone_confianca(nivel):
    """Retorna um ícone conforme o nível de confiança."""
    mapa = {
        "Alta": "🟢",
        "Moderada": "🟡",
        "Baixa": "🔴"
    }
    return mapa.get(str(nivel), "⚪")


def _obter_estrelas(indice):
    """Converte o índice de confiança em uma escala de 1 a 5 estrelas."""
    try:
        valor = float(indice)
    except (TypeError, ValueError):
        valor = 0.0

    if valor >= 85:
        quantidade = 5
    elif valor >= 75:
        quantidade = 4
    elif valor >= 65:
        quantidade = 3
    elif valor >= 55:
        quantidade = 2
    else:
        quantidade = 1

    return "★" * quantidade + "☆" * (5 - quantidade)


def _identificar_chave_mercado(nome_mercado):
    """
    Relaciona o nome exibido pela RecommendationEngine
    ao mercado calculado pela ValueEngine.
    """
    nome = str(nome_mercado).lower()

    if (
        "1,5" in nome
        or "1.5" in nome
        or "over" in nome
    ):
        return "over_15"

    if (
        "btts" in nome
        or "ambas" in nome
        or "ambos" in nome
    ):
        return "btts"

    return None


def _renderizar_lista(titulo, itens, icone):
    """Exibe motivos ou alertas de forma padronizada."""
    st.markdown(f"**{titulo}**")

    if not itens:
        st.caption("Nenhuma informação disponível.")
        return

    for item in itens:
        st.markdown(f"{icone} {item}")


def _renderizar_amostra(amostra):
    """Exibe o tamanho e a classificação da amostra analisada."""
    mandante = amostra.get("mandante", {})
    visitante = amostra.get("visitante", {})

    coluna_mandante, coluna_visitante = st.columns(2)

    with coluna_mandante:
        st.caption("Amostra do mandante")
        st.write(
            f"{mandante.get('jogos', 0)} jogos — "
            f"{mandante.get('classificacao', 'N/D')}"
        )

    with coluna_visitante:
        st.caption("Amostra do visitante")
        st.write(
            f"{visitante.get('jogos', 0)} jogos — "
            f"{visitante.get('classificacao', 'N/D')}"
        )


def _renderizar_value(resultado_value):
    """Exibe os dados calculados pela ValueEngine."""
    if not isinstance(resultado_value, dict):
        st.info("ValueEngine indisponível para este mercado.")
        return

    erro = resultado_value.get("erro")
    if erro:
        st.warning(f"ValueEngine: {erro}")
        return

    value_bet = bool(resultado_value.get("value_bet", False))
    classificacao = resultado_value.get(
        "classificacao",
        "N/D"
    )

    st.divider()
    st.markdown("**Análise de valor da odd**")

    coluna_odd_justa, coluna_odd_mercado = st.columns(2)

    with coluna_odd_justa:
        st.metric(
            label="Odd justa",
            value=_formatar_odd(
                resultado_value.get("odd_justa")
            )
        )

    with coluna_odd_mercado:
        st.metric(
            label="Odd de mercado",
            value=_formatar_odd(
                resultado_value.get("odd_casa")
            )
        )

    coluna_edge, coluna_ev = st.columns(2)

    with coluna_edge:
        st.metric(
            label="Edge",
            value=_formatar_valor_com_sinal(
                resultado_value.get("edge")
            )
        )

    with coluna_ev:
        st.metric(
            label="Valor esperado",
            value=_formatar_valor_com_sinal(
                resultado_value.get("valor_esperado")
            )
        )

    st.caption(
        "Probabilidade implícita da odd: "
        f"{_formatar_percentual(
            resultado_value.get('probabilidade_implicita')
        )}"
    )

    if value_bet:
        st.success(
            f"✅ TEM VALOR — Classificação: {classificacao}"
        )
    else:
        st.warning(
            f"⛔ SEM VALOR — Classificação: {classificacao}"
        )


def _renderizar_recomendacao(
    recomendacao,
    resultado_value
):
    """Renderiza um card completo de uma recomendação."""
    mercado = recomendacao.get(
        "mercado",
        "Mercado não informado"
    )

    recomendado = bool(
        recomendacao.get("recomendado", False)
    )

    indice = recomendacao.get(
        "indice_confianca",
        0.0
    )

    nivel = recomendacao.get(
        "nivel_confianca",
        "N/D"
    )

    ajuste = recomendacao.get(
        "ajuste_contextual",
        0.0
    )

    score_contextual = recomendacao.get(
        "score_contextual",
        0.0
    )

    status_texto = (
        "RECOMENDADO"
        if recomendado
        else "NÃO RECOMENDADO"
    )

    status_icone = "✅" if recomendado else "⛔"
    confianca_icone = _obter_icone_confianca(nivel)

    with st.container(border=True):
        st.markdown(f"### {mercado}")
        st.markdown(
            f"## {status_icone} {status_texto}"
        )
        st.markdown(
            f"**{_obter_estrelas(indice)}**"
        )

        coluna_indice, coluna_nivel, coluna_contexto = (
            st.columns(3)
        )

        with coluna_indice:
            st.metric(
                label="Índice de confiança",
                value=_formatar_percentual(indice)
            )

        with coluna_nivel:
            st.metric(
                label="Nível",
                value=f"{confianca_icone} {nivel}"
            )

        with coluna_contexto:
            st.metric(
                label="Ajuste contextual",
                value=_formatar_ajuste(ajuste)
            )

        try:
            progresso = max(
                0.0,
                min(float(indice) / 100.0, 1.0)
            )
        except (TypeError, ValueError):
            progresso = 0.0

        st.progress(progresso)

        st.caption(
            "Score contextual: "
            f"{_formatar_percentual(score_contextual)}"
        )

        _renderizar_value(resultado_value)

        st.divider()

        _renderizar_lista(
            titulo="Motivos da análise",
            itens=recomendacao.get("motivos", []),
            icone="✔️"
        )

        alertas = recomendacao.get("alertas", [])

        if alertas:
            st.divider()

            _renderizar_lista(
                titulo="Pontos de atenção",
                itens=alertas,
                icone="⚠️"
            )

        st.divider()

        _renderizar_amostra(
            recomendacao.get("amostra", {})
        )

        aviso = recomendacao.get("aviso")

        if aviso:
            st.caption(aviso)


def renderizar_painel_recomendacoes(
    resultado_recommendation,
    resultados_value_mercados
):
    """
    Exibe as recomendações da RecommendationEngine
    junto com os resultados da ValueEngine.
    """
    if not isinstance(
        resultado_recommendation,
        dict
    ):
        st.error(
            "A RecommendationEngine não retornou "
            "um resultado válido."
        )
        return

    erro = resultado_recommendation.get("erro")

    if erro:
        st.error(
            f"Erro na RecommendationEngine: {erro}"
        )
        return

    recomendacoes = resultado_recommendation.get(
        "recomendacoes",
        []
    )

    if not recomendacoes:
        st.warning(
            "Nenhuma recomendação foi produzida "
            "para esta partida."
        )
        return

    if not isinstance(
        resultados_value_mercados,
        dict
    ):
        resultados_value_mercados = {}

    st.caption(
        "Os índices combinam o histórico recente "
        "com o contexto de cada mercado. "
        "A ValueEngine compara a probabilidade "
        "calculada com a odd informada."
    )

    colunas = st.columns(len(recomendacoes))

    for coluna, recomendacao in zip(
        colunas,
        recomendacoes
    ):
        mercado = recomendacao.get(
            "mercado",
            ""
        )

        chave_mercado = _identificar_chave_mercado(
            mercado
        )

        resultado_value = (
            resultados_value_mercados.get(
                chave_mercado,
                {}
            )
        )

        with coluna:
            _renderizar_recomendacao(
                recomendacao=recomendacao,
                resultado_value=resultado_value
            )