from data_storage import carregar_json
from footballai_engine import FootballAIEngine
from engines.recommendation_engine import RecommendationEngine


ARQUIVO_PARTIDAS = "brasileirao_serie_a_2024.json"
JANELA_ANALISE = 5

MANDANTE_ID = 127
MANDANTE_NOME = "Flamengo"

VISITANTE_ID = 121
VISITANTE_NOME = "Palmeiras"


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


def formatar_numero(valor, casas=2):
    """
    Converte um valor numérico para texto.
    """

    try:
        return f"{float(valor):.{casas}f}"
    except (TypeError, ValueError):
        return "0.00"


def definir_risco(recomendacao):
    """
    Converte o nível de confiança em uma classificação
    simples de risco.

    Essa classificação é apenas informativa.
    """

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


def formatar_status_recomendacao(recomendado):
    return "SIM" if recomendado else "NÃO"


def exibir_cabecalho():
    print("\n")
    print("=" * 60)
    print("FOOTBALLAI — ANÁLISE DO CONFRONTO")
    print("=" * 60)

    print(
        f"\n{MANDANTE_NOME} x {VISITANTE_NOME}"
    )

    print(
        f"Janela estatística: últimos "
        f"{JANELA_ANALISE} jogos"
    )


def exibir_resumo_times(dados_base):
    mandante = dados_base.get(
        "mandante",
        {}
    )

    visitante = dados_base.get(
        "visitante",
        {}
    )

    print("\n")
    print("-" * 60)
    print("RESUMO DOS TIMES")
    print("-" * 60)

    print(f"\n{MANDANTE_NOME}")

    print(
        "Inteligência FootballAI: "
        f"{formatar_numero(
            mandante.get('intelligence_score')
        )}"
    )

    print(
        "Rating: "
        f"{formatar_numero(
            mandante.get('rating')
        )}"
    )

    print(
        "Forma: "
        f"{formatar_numero(
            mandante.get('nota_forma')
        )}"
    )

    print(
        "Pulse: "
        f"{formatar_numero(
            mandante.get('pulse_score')
        )}"
    )

    print(
        "Tendência: "
        f"{mandante.get('tendencia', 'Não definida')}"
    )

    print(f"\n{VISITANTE_NOME}")

    print(
        "Inteligência FootballAI: "
        f"{formatar_numero(
            visitante.get('intelligence_score')
        )}"
    )

    print(
        "Rating: "
        f"{formatar_numero(
            visitante.get('rating')
        )}"
    )

    print(
        "Forma: "
        f"{formatar_numero(
            visitante.get('nota_forma')
        )}"
    )

    print(
        "Pulse: "
        f"{formatar_numero(
            visitante.get('pulse_score')
        )}"
    )

    print(
        "Tendência: "
        f"{visitante.get('tendencia', 'Não definida')}"
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

    print("\n")
    print("-" * 60)
    print(mercado.upper())
    print("-" * 60)

    print(
        "Recomendação: "
        f"{formatar_status_recomendacao(recomendado)}"
    )

    print(
        "Índice estatístico: "
        f"{formatar_numero(indice_estatistico)}%"
    )

    print(
        "Ajuste contextual: "
        f"{float(ajuste_contextual):+.2f}"
    )

    print(
        "Confiança final: "
        f"{formatar_numero(indice_confianca)}%"
    )

    print(
        f"Nível de confiança: {nivel_confianca}"
    )

    print(
        f"Risco estimado: {risco}"
    )

    motivos = recomendacao.get(
        "motivos",
        []
    )

    print("\nMotivos:")

    if motivos:
        for motivo in motivos:
            print(f"- {motivo}")
    else:
        print("- Nenhum motivo informado.")

    alertas = recomendacao.get(
        "alertas",
        []
    )

    print("\nAlertas:")

    if alertas:
        for alerta in alertas:
            print(f"- {alerta}")
    else:
        print("- Nenhum alerta identificado.")


def exibir_aviso_final():
    print("\n")
    print("=" * 60)
    print("AVISO DE RISCO")
    print("=" * 60)

    print(
        "As análises do FootballAI são baseadas em "
        "dados estatísticos históricos."
    )

    print(
        "Nenhuma recomendação representa garantia "
        "de acerto ou retorno financeiro."
    )

    print("=" * 60)


def gerar_analise():
    dados = carregar_json(
        ARQUIVO_PARTIDAS
    )

    partidas = extrair_partidas(
        dados
    )

    analise_mandante = FootballAIEngine(
        partidas=partidas,
        team_id=MANDANTE_ID,
        janela=JANELA_ANALISE
    ).analisar()

    if analise_mandante.get("erro"):
        raise ValueError(
            "Erro na análise do mandante: "
            f"{analise_mandante['erro']}"
        )

    analise_visitante = FootballAIEngine(
        partidas=partidas,
        team_id=VISITANTE_ID,
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


def main():
    try:
        resultado = gerar_analise()

        dados_base = resultado.get(
            "dados_base",
            {}
        )

        recomendacoes = resultado.get(
            "recomendacoes",
            []
        )

        exibir_cabecalho()

        exibir_resumo_times(
            dados_base
        )

        print("\n")
        print("=" * 60)
        print("RECOMENDAÇÕES DE MERCADO")
        print("=" * 60)

        for recomendacao in recomendacoes:
            exibir_recomendacao(
                recomendacao
            )

        exibir_aviso_final()

    except FileNotFoundError:
        print(
            "\nERRO: o arquivo de partidas "
            "não foi encontrado."
        )

    except ValueError as erro:
        print(f"\nERRO: {erro}")

    except Exception as erro:
        print(
            "\nERRO INESPERADO AO GERAR O PAINEL:"
        )

        print(erro)


if __name__ == "__main__":
    main()