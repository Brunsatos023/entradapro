import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st

# st.set_page_config() nao e mais chamado aqui - com st.navigation(),
# so o ponto de entrada (dashboard.py) pode chamar isso, uma unica
# vez por sessao. O titulo/icone desta pagina agora vem do
# st.Page(...) definido em dashboard.py.


CAMINHOS_RELATORIO = (
    Path("performance_report.json"),
    Path("data/processed/performance_report.json"),
    Path("src/performance_report.json"),
)


def localizar_relatorio() -> Optional[Path]:
    """
    Procura o performance_report.json nos caminhos conhecidos.
    """

    for caminho in CAMINHOS_RELATORIO:
        if caminho.exists() and caminho.is_file():
            return caminho

    return None


@st.cache_data
def carregar_relatorio(
    caminho: str,
    data_modificacao: float,
) -> Dict[str, Any]:
    """
    Carrega o relatório JSON.

    O parâmetro data_modificacao é usado para invalidar o cache
    sempre que o arquivo for atualizado.
    """

    del data_modificacao

    caminho_arquivo = Path(caminho)

    with caminho_arquivo.open(
        "r",
        encoding="utf-8",
    ) as arquivo:
        dados = json.load(arquivo)

    if not isinstance(dados, dict):
        raise TypeError(
            "O performance_report.json precisa conter "
            "um objeto JSON principal."
        )

    return dados


def obter_primeiro_dicionario(
    dados: Dict[str, Any],
    chaves: List[str],
) -> Dict[str, Any]:
    """
    Retorna o primeiro dicionário encontrado entre as chaves.
    """

    for chave in chaves:
        valor = dados.get(chave)

        if isinstance(valor, dict):
            return valor

    return {}


def obter_valor(
    dados: Dict[str, Any],
    chaves: List[str],
    padrao: Any = None,
) -> Any:
    """
    Retorna o primeiro valor existente entre as chaves informadas.
    """

    for chave in chaves:
        if chave in dados:
            return dados[chave]

    return padrao


def converter_numero(
    valor: Any,
    padrao: float = 0.0,
) -> float:
    """
    Converte valores numéricos de forma segura.
    """

    if isinstance(valor, bool):
        return padrao

    if isinstance(valor, (int, float)):
        return float(valor)

    if isinstance(valor, str):
        texto = (
            valor.strip()
            .replace("R$", "")
            .replace("%", "")
            .replace(" ", "")
        )

        if "," in texto and "." in texto:
            texto = texto.replace(".", "").replace(",", ".")
        else:
            texto = texto.replace(",", ".")

        try:
            return float(texto)
        except ValueError:
            return padrao

    return padrao


def formatar_moeda(valor: Any) -> str:
    """
    Formata um número no padrão monetário brasileiro.
    """

    numero = converter_numero(valor)

    texto = f"{numero:,.2f}"

    texto = (
        texto.replace(",", "TEMP")
        .replace(".", ",")
        .replace("TEMP", ".")
    )

    return f"R$ {texto}"


def formatar_percentual(valor: Any) -> str:
    """
    Formata um valor percentual.
    """

    numero = converter_numero(valor)

    return f"{numero:.2f}%".replace(".", ",")


def formatar_inteiro(valor: Any) -> str:
    """
    Formata valores inteiros.
    """

    numero = int(
        round(
            converter_numero(valor)
        )
    )

    return f"{numero:,}".replace(",", ".")


def localizar_backtest(
    relatorio: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Localiza a seção do BacktestEngine.
    """

    backtest = obter_primeiro_dicionario(
        relatorio,
        [
            "backtest",
            "resultado_backtest",
            "backtest_engine",
        ],
    )

    if backtest:
        return backtest

    if "total_apostas" in relatorio:
        return relatorio

    return {}


def localizar_analytics(
    relatorio: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Localiza a seção do PerformanceAnalytics.
    """

    return obter_primeiro_dicionario(
        relatorio,
        [
            "performance_analytics",
            "analytics",
            "resultado_analytics",
            "performance",
        ],
    )


def localizar_optimizer(
    relatorio: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Localiza a seção do StrategyOptimizer.
    """

    return obter_primeiro_dicionario(
        relatorio,
        [
            "strategy_optimizer",
            "optimizer",
            "resultado_optimizer",
            "otimizacao",
        ],
    )


def localizar_geral(
    optimizer: Dict[str, Any],
    analytics: Dict[str, Any],
    backtest: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Localiza as métricas gerais seguindo a ordem de prioridade.
    """

    geral_optimizer = optimizer.get("geral")

    if isinstance(geral_optimizer, dict):
        return geral_optimizer

    geral_analytics = analytics.get("geral")

    if isinstance(geral_analytics, dict):
        return geral_analytics

    return backtest


def localizar_mercados(
    optimizer: Dict[str, Any],
    analytics: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Localiza a estrutura de métricas por mercado.
    """

    mercados_optimizer = optimizer.get("mercados")

    if isinstance(mercados_optimizer, dict):
        return mercados_optimizer

    mercados_analytics = analytics.get("mercados")

    if isinstance(mercados_analytics, dict):
        return mercados_analytics

    return {}


def localizar_comparacao_cortes(
    optimizer: Dict[str, Any],
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Localiza as simulações de pontos de corte.
    """

    chaves_possiveis = [
        "comparacao_cortes",
        "pontos_corte",
        "analise_pontos_corte",
        "cortes",
    ]

    for chave in chaves_possiveis:
        estrutura = optimizer.get(chave)

        if isinstance(estrutura, dict):
            resultado = {}

            for mercado, cortes in estrutura.items():
                if isinstance(cortes, list):
                    resultado[mercado] = cortes

            if resultado:
                return resultado

    return {}


def localizar_recomendacoes(
    optimizer: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Localiza as recomendações geradas pelo StrategyOptimizer.
    """

    recomendacoes = optimizer.get("recomendacoes")

    if isinstance(recomendacoes, dict):
        return recomendacoes

    return {}


def localizar_diagnostico(
    optimizer: Dict[str, Any],
    analytics: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Localiza o diagnóstico de consistência.
    """

    diagnostico = optimizer.get("diagnostico")

    if isinstance(diagnostico, dict):
        return diagnostico

    diagnostico = analytics.get("diagnostico")

    if isinstance(diagnostico, dict):
        return diagnostico

    return {}


def obter_mercado(
    mercados: Dict[str, Any],
    nomes: List[str],
) -> Dict[str, Any]:
    """
    Localiza um mercado utilizando possíveis nomes de chave.
    """

    for nome in nomes:
        resultado = mercados.get(nome)

        if isinstance(resultado, dict):
            return resultado

    return {}


def criar_dataframe_mercados(
    mercados: Dict[str, Any],
) -> pd.DataFrame:
    """
    Converte as métricas de mercados em DataFrame.
    """

    configuracoes = [
        (
            "Over 1.5",
            ["over15", "over_15", "over1_5"],
        ),
        (
            "BTTS",
            ["btts", "ambas_marcam"],
        ),
    ]

    linhas = []

    for nome_visual, chaves in configuracoes:
        dados_mercado = obter_mercado(
            mercados=mercados,
            nomes=chaves,
        )

        if not dados_mercado:
            continue

        linhas.append(
            {
                "Mercado": nome_visual,
                "Apostas": int(
                    converter_numero(
                        obter_valor(
                            dados_mercado,
                            ["total_apostas", "apostas"],
                            0,
                        )
                    )
                ),
                "Vitórias": int(
                    converter_numero(
                        obter_valor(
                            dados_mercado,
                            [
                                "apostas_vencedoras",
                                "vitorias",
                                "acertos",
                            ],
                            0,
                        )
                    )
                ),
                "Derrotas": int(
                    converter_numero(
                        obter_valor(
                            dados_mercado,
                            [
                                "apostas_perdedoras",
                                "derrotas",
                                "erros",
                            ],
                            0,
                        )
                    )
                ),
                "Taxa de acerto (%)": converter_numero(
                    obter_valor(
                        dados_mercado,
                        ["taxa_acerto", "acerto"],
                        0,
                    )
                ),
                "Lucro líquido": converter_numero(
                    obter_valor(
                        dados_mercado,
                        ["lucro_liquido", "lucro"],
                        0,
                    )
                ),
                "ROI (%)": converter_numero(
                    obter_valor(
                        dados_mercado,
                        ["roi"],
                        0,
                    )
                ),
                "Odd média": converter_numero(
                    obter_valor(
                        dados_mercado,
                        ["odd_media"],
                        0,
                    )
                ),
                "Probabilidade média (%)": converter_numero(
                    obter_valor(
                        dados_mercado,
                        ["probabilidade_media"],
                        0,
                    )
                ),
            }
        )

    return pd.DataFrame(
        linhas
    )


def criar_dataframe_cortes(
    comparacao_cortes: Dict[str, List[Dict[str, Any]]],
) -> pd.DataFrame:
    """
    Converte as simulações de corte em uma única tabela.
    """

    nomes_mercados = {
        "over15": "Over 1.5",
        "over_15": "Over 1.5",
        "over1_5": "Over 1.5",
        "btts": "BTTS",
        "ambas_marcam": "BTTS",
    }

    linhas = []

    for mercado, cortes in comparacao_cortes.items():
        if not isinstance(cortes, list):
            continue

        nome_mercado = nomes_mercados.get(
            mercado,
            mercado,
        )

        for corte in cortes:
            if not isinstance(corte, dict):
                continue

            linhas.append(
                {
                    "Mercado": nome_mercado,
                    "Corte mínimo (%)": converter_numero(
                        corte.get(
                            "probabilidade_minima",
                            0,
                        )
                    ),
                    "Apostas": int(
                        converter_numero(
                            corte.get(
                                "total_apostas",
                                0,
                            )
                        )
                    ),
                    "Acertos": int(
                        converter_numero(
                            corte.get(
                                "apostas_vencedoras",
                                0,
                            )
                        )
                    ),
                    "Erros": int(
                        converter_numero(
                            corte.get(
                                "apostas_perdedoras",
                                0,
                            )
                        )
                    ),
                    "Taxa de acerto (%)": converter_numero(
                        corte.get(
                            "taxa_acerto",
                            0,
                        )
                    ),
                    "Lucro líquido": converter_numero(
                        corte.get(
                            "lucro_liquido",
                            0,
                        )
                    ),
                    "ROI (%)": converter_numero(
                        corte.get(
                            "roi",
                            0,
                        )
                    ),
                    "Odd média": converter_numero(
                        corte.get(
                            "odd_media",
                            0,
                        )
                    ),
                    "Amostra suficiente": bool(
                        corte.get(
                            "amostra_suficiente",
                            False,
                        )
                    ),
                }
            )

    dataframe = pd.DataFrame(
        linhas
    )

    if dataframe.empty:
        return dataframe

    return dataframe.sort_values(
        by=[
            "Mercado",
            "Corte mínimo (%)",
        ],
        ascending=[
            True,
            True,
        ],
    ).reset_index(
        drop=True
    )


def localizar_melhor_corte(
    recomendacao: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """
    Retorna o melhor ponto de corte de uma recomendação.
    """

    melhor_corte = recomendacao.get(
        "melhor_ponto_corte"
    )

    if isinstance(melhor_corte, dict):
        return melhor_corte

    return None


def renderizar_cabecalho(
    caminho_relatorio: Path,
) -> None:
    """
    Renderiza o cabeçalho principal.
    """

    st.title(
        "📊 Performance Analytics"
    )

    st.caption(
        "Análise do backtest, desempenho dos mercados "
        "e otimização dos pontos de corte."
    )

    st.info(
        f"Relatório carregado: {caminho_relatorio}"
    )


def renderizar_resumo_geral(
    geral: Dict[str, Any],
) -> None:
    """
    Exibe as métricas gerais do FootballAI.
    """

    st.subheader(
        "Resultado geral"
    )

    total_apostas = obter_valor(
        geral,
        ["total_apostas", "apostas"],
        0,
    )

    taxa_acerto = obter_valor(
        geral,
        ["taxa_acerto", "acerto"],
        0,
    )

    lucro_liquido = obter_valor(
        geral,
        ["lucro_liquido", "lucro"],
        0,
    )

    roi = obter_valor(
        geral,
        ["roi"],
        0,
    )

    valor_apostado = obter_valor(
        geral,
        ["valor_apostado", "stake_total"],
        0,
    )

    coluna_1, coluna_2, coluna_3, coluna_4, coluna_5 = (
        st.columns(5)
    )

    coluna_1.metric(
        "Total de apostas",
        formatar_inteiro(
            total_apostas
        ),
    )

    coluna_2.metric(
        "Taxa de acerto",
        formatar_percentual(
            taxa_acerto
        ),
    )

    coluna_3.metric(
        "Valor apostado",
        formatar_moeda(
            valor_apostado
        ),
    )

    coluna_4.metric(
        "Lucro líquido",
        formatar_moeda(
            lucro_liquido
        ),
    )

    coluna_5.metric(
        "ROI",
        formatar_percentual(
            roi
        ),
    )


def renderizar_desempenho_mercados(
    dataframe: pd.DataFrame,
) -> None:
    """
    Exibe a comparação entre os mercados.
    """

    st.subheader(
        "Desempenho por mercado"
    )

    if dataframe.empty:
        st.warning(
            "Não foram localizadas métricas por mercado."
        )

        return

    dataframe_visual = dataframe.copy()

    dataframe_visual["Lucro líquido"] = (
        dataframe_visual["Lucro líquido"].map(
            formatar_moeda
        )
    )

    dataframe_visual["ROI (%)"] = (
        dataframe_visual["ROI (%)"].map(
            formatar_percentual
        )
    )

    dataframe_visual["Taxa de acerto (%)"] = (
        dataframe_visual["Taxa de acerto (%)"].map(
            formatar_percentual
        )
    )

    dataframe_visual["Probabilidade média (%)"] = (
        dataframe_visual[
            "Probabilidade média (%)"
        ].map(
            formatar_percentual
        )
    )

    st.dataframe(
        dataframe_visual,
        use_container_width=True,
        hide_index=True,
    )

    grafico_roi = (
        dataframe.set_index(
            "Mercado"
        )[["ROI (%)"]]
    )

    st.markdown(
        "#### ROI por mercado"
    )

    st.bar_chart(
        grafico_roi
    )


def renderizar_recomendacao_mercado(
    nome_visual: str,
    recomendacao: Dict[str, Any],
) -> None:
    """
    Exibe a recomendação de um mercado.
    """

    st.markdown(
        f"### {nome_visual}"
    )

    roi_atual = recomendacao.get(
        "roi_configuracao_atual",
        0,
    )

    lucro_atual = recomendacao.get(
        "lucro_configuracao_atual",
        0,
    )

    melhor_corte = localizar_melhor_corte(
        recomendacao
    )

    coluna_1, coluna_2 = st.columns(2)

    coluna_1.metric(
        "ROI atual",
        formatar_percentual(
            roi_atual
        ),
    )

    coluna_2.metric(
        "Lucro atual",
        formatar_moeda(
            lucro_atual
        ),
    )

    if melhor_corte is not None:
        st.success(
            "Foi encontrado um ponto de corte lucrativo "
            "com amostra suficiente."
        )

        coluna_1, coluna_2, coluna_3, coluna_4 = (
            st.columns(4)
        )

        coluna_1.metric(
            "Corte recomendado",
            formatar_percentual(
                melhor_corte.get(
                    "probabilidade_minima",
                    0,
                )
            ),
        )

        coluna_2.metric(
            "Apostas",
            formatar_inteiro(
                melhor_corte.get(
                    "total_apostas",
                    0,
                )
            ),
        )

        coluna_3.metric(
            "Taxa de acerto",
            formatar_percentual(
                melhor_corte.get(
                    "taxa_acerto",
                    0,
                )
            ),
        )

        coluna_4.metric(
            "ROI otimizado",
            formatar_percentual(
                melhor_corte.get(
                    "roi",
                    0,
                )
            ),
        )

        st.metric(
            "Lucro líquido otimizado",
            formatar_moeda(
                melhor_corte.get(
                    "lucro_liquido",
                    0,
                )
            ),
        )

    else:
        st.warning(
            "Nenhum ponto de corte lucrativo com "
            "amostra suficiente foi encontrado."
        )

    alertas = recomendacao.get(
        "alertas",
        [],
    )

    if isinstance(alertas, list):
        for alerta in alertas:
            st.warning(
                str(alerta)
            )


def renderizar_recomendacoes(
    recomendacoes: Dict[str, Any],
) -> None:
    """
    Exibe as recomendações geradas pelo StrategyOptimizer.
    """

    st.subheader(
        "Recomendações do StrategyOptimizer"
    )

    if not recomendacoes:
        st.warning(
            "A seção de recomendações não foi localizada "
            "no relatório."
        )

        return

    coluna_over15, coluna_btts = st.columns(2)

    recomendacao_over15 = obter_mercado(
        mercados=recomendacoes,
        nomes=[
            "over15",
            "over_15",
            "over1_5",
        ],
    )

    recomendacao_btts = obter_mercado(
        mercados=recomendacoes,
        nomes=[
            "btts",
            "ambas_marcam",
        ],
    )

    with coluna_over15:
        if recomendacao_over15:
            renderizar_recomendacao_mercado(
                nome_visual="Over 1.5",
                recomendacao=recomendacao_over15,
            )
        else:
            st.warning(
                "Recomendação de Over 1.5 não localizada."
            )

    with coluna_btts:
        if recomendacao_btts:
            renderizar_recomendacao_mercado(
                nome_visual="BTTS",
                recomendacao=recomendacao_btts,
            )
        else:
            st.warning(
                "Recomendação de BTTS não localizada."
            )


def renderizar_pontos_corte(
    dataframe: pd.DataFrame,
) -> None:
    """
    Exibe a tabela completa dos pontos de corte.
    """

    st.subheader(
        "Simulação dos pontos de corte"
    )

    if dataframe.empty:
        st.warning(
            "As simulações dos pontos de corte "
            "não foram localizadas."
        )

        return

    mercados_disponiveis = sorted(
        dataframe["Mercado"].unique()
    )

    mercado_selecionado = st.selectbox(
        "Selecione o mercado",
        options=mercados_disponiveis,
    )

    somente_amostra_suficiente = st.checkbox(
        "Mostrar somente cortes com amostra suficiente",
        value=False,
    )

    tabela_filtrada = dataframe[
        dataframe["Mercado"]
        == mercado_selecionado
    ].copy()

    if somente_amostra_suficiente:
        tabela_filtrada = tabela_filtrada[
            tabela_filtrada[
                "Amostra suficiente"
            ]
        ].copy()

    tabela_visual = tabela_filtrada.copy()

    tabela_visual["Corte mínimo (%)"] = (
        tabela_visual[
            "Corte mínimo (%)"
        ].map(
            formatar_percentual
        )
    )

    tabela_visual["Taxa de acerto (%)"] = (
        tabela_visual[
            "Taxa de acerto (%)"
        ].map(
            formatar_percentual
        )
    )

    tabela_visual["Lucro líquido"] = (
        tabela_visual[
            "Lucro líquido"
        ].map(
            formatar_moeda
        )
    )

    tabela_visual["ROI (%)"] = (
        tabela_visual[
            "ROI (%)"
        ].map(
            formatar_percentual
        )
    )

    tabela_visual["Amostra suficiente"] = (
        tabela_visual[
            "Amostra suficiente"
        ].map(
            lambda valor: (
                "Sim"
                if valor
                else "Não"
            )
        )
    )

    st.dataframe(
        tabela_visual,
        use_container_width=True,
        hide_index=True,
    )

    if not tabela_filtrada.empty:
        grafico = (
            tabela_filtrada[
                [
                    "Corte mínimo (%)",
                    "ROI (%)",
                ]
            ]
            .sort_values(
                "Corte mínimo (%)"
            )
            .set_index(
                "Corte mínimo (%)"
            )
        )

        st.markdown(
            f"#### Evolução do ROI — {mercado_selecionado}"
        )

        st.line_chart(
            grafico
        )


def renderizar_diagnostico(
    diagnostico: Dict[str, Any],
) -> None:
    """
    Exibe o diagnóstico de consistência do relatório.
    """

    st.subheader(
        "Diagnóstico de consistência"
    )

    if not diagnostico:
        st.warning(
            "O diagnóstico não foi localizado."
        )

        return

    consistente = bool(
        diagnostico.get(
            "consistente",
            False,
        )
    )

    if consistente:
        st.success(
            "Resultado consistente: todas as validações "
            "principais foram aprovadas."
        )
    else:
        st.error(
            "Foram encontradas inconsistências no relatório."
        )

    validacoes = {
        "Total de apostas": diagnostico.get(
            "consistencia_total_apostas"
        ),
        "Lucro líquido": diagnostico.get(
            "consistencia_lucro"
        ),
        "Apostas Over 1.5": diagnostico.get(
            "consistencia_apostas_over15"
        ),
        "Apostas BTTS": diagnostico.get(
            "consistencia_apostas_btts"
        ),
    }

    colunas = st.columns(
        len(validacoes)
    )

    for coluna, (
        nome,
        resultado,
    ) in zip(
        colunas,
        validacoes.items(),
    ):
        if resultado is True:
            texto = "Aprovado"
        elif resultado is False:
            texto = "Reprovado"
        else:
            texto = "Não informado"

        coluna.metric(
            nome,
            texto,
        )

    alertas = diagnostico.get(
        "alertas",
        [],
    )

    if isinstance(alertas, list) and alertas:
        st.markdown(
            "#### Alertas"
        )

        for alerta in alertas:
            st.warning(
                str(alerta)
            )


def renderizar_json_completo(
    relatorio: Dict[str, Any],
) -> None:
    """
    Permite inspecionar o relatório bruto.
    """

    with st.expander(
        "Ver JSON completo do relatório"
    ):
        st.json(
            relatorio
        )


def main() -> None:
    """
    Ponto de entrada da página.
    """

    caminho_relatorio = localizar_relatorio()

    if caminho_relatorio is None:
        st.error(
            "O arquivo performance_report.json "
            "não foi encontrado."
        )

        st.code(
            "python src/backtest_main.py",
            language="powershell",
        )

        st.info(
            "Execute o backtest oficial para gerar "
            "o relatório e depois atualize esta página."
        )

        st.stop()

    try:
        relatorio = carregar_relatorio(
            caminho=str(
                caminho_relatorio
            ),
            data_modificacao=(
                caminho_relatorio.stat().st_mtime
            ),
        )

    except (
        OSError,
        json.JSONDecodeError,
        TypeError,
        ValueError,
    ) as erro:
        st.error(
            f"Erro ao carregar o relatório: {erro}"
        )

        st.stop()

    backtest = localizar_backtest(
        relatorio
    )

    analytics = localizar_analytics(
        relatorio
    )

    optimizer = localizar_optimizer(
        relatorio
    )

    geral = localizar_geral(
        optimizer=optimizer,
        analytics=analytics,
        backtest=backtest,
    )

    mercados = localizar_mercados(
        optimizer=optimizer,
        analytics=analytics,
    )

    comparacao_cortes = localizar_comparacao_cortes(
        optimizer
    )

    recomendacoes = localizar_recomendacoes(
        optimizer
    )

    diagnostico = localizar_diagnostico(
        optimizer=optimizer,
        analytics=analytics,
    )

    dataframe_mercados = criar_dataframe_mercados(
        mercados
    )

    dataframe_cortes = criar_dataframe_cortes(
        comparacao_cortes
    )

    renderizar_cabecalho(
        caminho_relatorio
    )

    renderizar_resumo_geral(
        geral
    )

    st.divider()

    renderizar_desempenho_mercados(
        dataframe_mercados
    )

    st.divider()

    renderizar_recomendacoes(
        recomendacoes
    )

    st.divider()

    renderizar_pontos_corte(
        dataframe_cortes
    )

    st.divider()

    renderizar_diagnostico(
        diagnostico
    )

    renderizar_json_completo(
        relatorio
    )


if __name__ == "__main__":
    main()