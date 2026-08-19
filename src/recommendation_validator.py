from data_storage import carregar_json
from footballai_engine import FootballAIEngine
from engines.recommendation_engine import RecommendationEngine


ARQUIVO_PARTIDAS = "brasileirao_serie_a_2024.json"

JANELA_ANALISE = 5


CONFRONTOS_TESTE = [
    {
        "nome": "Flamengo x Palmeiras",
        "mandante_id": 127,
        "visitante_id": 121
    },
    {
        "nome": "Internacional x Flamengo",
        "mandante_id": 119,
        "visitante_id": 127
    },
    {
        "nome": "Palmeiras x Internacional",
        "mandante_id": 121,
        "visitante_id": 119
    }
]


def extrair_partidas(dados):
    """
    Extrai as partidas do JSON completo da API-Football
    ou aceita diretamente uma lista de partidas.
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


def formatar_recomendacao(recomendacao):
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
        "Não definido"
    )

    status_recomendacao = (
        "SIM"
        if recomendado
        else "NÃO"
    )

    print(f"\nMercado: {mercado}")
    print(f"Recomendado: {status_recomendacao}")

    print(
        "Índice estatístico: "
        f"{indice_estatistico:.2f}"
    )

    print(
        "Ajuste contextual: "
        f"{ajuste_contextual:+.2f}"
    )

    print(
        "Índice final: "
        f"{indice_confianca:.2f}"
    )

    print(
        "Nível de confiança: "
        f"{nivel_confianca}"
    )

    alertas = recomendacao.get(
        "alertas",
        []
    )

    if alertas:
        print("Alertas:")

        for alerta in alertas:
            print(f"- {alerta}")

    else:
        print("Alertas: nenhum")


def validar_contextos(resultado):
    analise_contextual = resultado.get(
        "analise_contextual",
        {}
    )

    contexto_over15 = analise_contextual.get(
        "over15"
    )

    contexto_btts = analise_contextual.get(
        "btts"
    )

    if not isinstance(contexto_over15, dict):
        return False, (
            "Contexto específico de Over 1.5 "
            "não encontrado."
        )

    if not isinstance(contexto_btts, dict):
        return False, (
            "Contexto específico de BTTS "
            "não encontrado."
        )

    ajuste_over15 = contexto_over15.get(
        "ajuste_contextual"
    )

    ajuste_btts = contexto_btts.get(
        "ajuste_contextual"
    )

    if ajuste_over15 is None:
        return False, (
            "Ajuste contextual de Over 1.5 "
            "não encontrado."
        )

    if ajuste_btts is None:
        return False, (
            "Ajuste contextual de BTTS "
            "não encontrado."
        )

    if not -5.0 <= float(ajuste_over15) <= 5.0:
        return False, (
            "Ajuste de Over 1.5 fora do "
            "intervalo permitido."
        )

    if not -5.0 <= float(ajuste_btts) <= 5.0:
        return False, (
            "Ajuste de BTTS fora do "
            "intervalo permitido."
        )

    return True, "Contextos válidos."


def analisar_confronto(
    partidas,
    nome,
    mandante_id,
    visitante_id
):
    print("\n")
    print("=" * 60)
    print(f"CONFRONTO: {nome}")
    print("=" * 60)

    analise_mandante = FootballAIEngine(
        partidas=partidas,
        team_id=mandante_id,
        janela=JANELA_ANALISE
    ).analisar()

    analise_visitante = FootballAIEngine(
        partidas=partidas,
        team_id=visitante_id,
        janela=JANELA_ANALISE
    ).analisar()

    recommendation_engine = RecommendationEngine(
        analise_mandante=analise_mandante,
        analise_visitante=analise_visitante
    )

    resultado = recommendation_engine.analisar()

    if resultado.get("erro"):
        print(
            "ERRO NA RECOMMENDATION ENGINE:"
        )
        print(resultado["erro"])

        return False

    contextos_validos, mensagem_contexto = (
        validar_contextos(resultado)
    )

    print(
        "\nValidação dos contextos: "
        f"{mensagem_contexto}"
    )

    recomendacoes = resultado.get(
        "recomendacoes",
        []
    )

    if len(recomendacoes) != 2:
        print(
            "ERRO: eram esperadas exatamente "
            "duas recomendações."
        )

        return False

    for recomendacao in recomendacoes:
        formatar_recomendacao(
            recomendacao
        )

    return contextos_validos


def main():
    dados = carregar_json(
        ARQUIVO_PARTIDAS
    )

    partidas = extrair_partidas(
        dados
    )

    print(
        f"Arquivo carregado: {ARQUIVO_PARTIDAS}"
    )

    print(
        f"Total de partidas: {len(partidas)}"
    )

    total_aprovados = 0
    total_reprovados = 0

    for confronto in CONFRONTOS_TESTE:
        aprovado = analisar_confronto(
            partidas=partidas,
            nome=confronto["nome"],
            mandante_id=confronto["mandante_id"],
            visitante_id=confronto["visitante_id"]
        )

        if aprovado:
            total_aprovados += 1
        else:
            total_reprovados += 1

    print("\n")
    print("=" * 60)
    print("RESUMO DA VALIDAÇÃO")
    print("=" * 60)

    print(
        f"Confrontos aprovados: {total_aprovados}"
    )

    print(
        f"Confrontos reprovados: {total_reprovados}"
    )

    if total_reprovados == 0:
        print(
            "Resultado geral: APROVADO"
        )
    else:
        print(
            "Resultado geral: REPROVADO"
        )


if __name__ == "__main__":
    main()