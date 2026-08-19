from data_storage import carregar_json
from footballai_engine import FootballAIEngine
from engines.recommendation_engine import RecommendationEngine


ARQUIVO_PARTIDAS = "brasileirao_serie_a_2024.json"
JANELA_ANALISE = 5

LIMITE_EXEMPLOS_POR_MERCADO = 5


def extrair_partidas(dados):
    """
    Extrai a lista de partidas do JSON da API-Football
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
    Retorna um dicionário no formato:

    {
        team_id: team_name
    }
    """

    times = {}

    for partida in partidas:
        dados_times = partida.get("teams", {})

        mandante = dados_times.get("home", {})
        visitante = dados_times.get("away", {})

        mandante_id = mandante.get("id")
        mandante_nome = mandante.get("name")

        visitante_id = visitante.get("id")
        visitante_nome = visitante.get("name")

        if mandante_id is not None:
            times[mandante_id] = (
                mandante_nome
                or f"Time {mandante_id}"
            )

        if visitante_id is not None:
            times[visitante_id] = (
                visitante_nome
                or f"Time {visitante_id}"
            )

    return times


def gerar_analises_times(partidas, times):
    """
    Executa o FootballAIEngine apenas uma vez por time.

    Isso evita recalcular a mesma análise em todos
    os confrontos.
    """

    analises = {}

    print("\nGerando análises dos times...")

    for team_id, team_name in sorted(
        times.items(),
        key=lambda item: item[1]
    ):
        resultado = FootballAIEngine(
            partidas=partidas,
            team_id=team_id,
            janela=JANELA_ANALISE
        ).analisar()

        if resultado.get("erro"):
            print(
                f"- {team_name}: análise ignorada "
                f"por erro: {resultado['erro']}"
            )
            continue

        analises[team_id] = resultado

        print(f"- {team_name}: análise concluída")

    return analises


def montar_registro(
    nome_mandante,
    nome_visitante,
    recomendacao
):
    return {
        "confronto": (
            f"{nome_mandante} x {nome_visitante}"
        ),
        "mercado": recomendacao.get(
            "mercado",
            "Não identificado"
        ),
        "indice_estatistico": recomendacao.get(
            "indice_estatistico",
            0.0
        ),
        "ajuste_contextual": recomendacao.get(
            "ajuste_contextual",
            0.0
        ),
        "indice_confianca": recomendacao.get(
            "indice_confianca",
            0.0
        ),
        "nivel_confianca": recomendacao.get(
            "nivel_confianca",
            "Não definido"
        ),
        "alertas": recomendacao.get(
            "alertas",
            []
        )
    }


def exibir_exemplo(numero, registro):
    print("\n" + "-" * 60)
    print(f"EXEMPLO {numero}")
    print("-" * 60)

    print(
        f"Confronto: {registro['confronto']}"
    )

    print(
        f"Mercado: {registro['mercado']}"
    )

    print(
        "Índice estatístico: "
        f"{registro['indice_estatistico']:.2f}"
    )

    print(
        "Ajuste contextual: "
        f"{registro['ajuste_contextual']:+.2f}"
    )

    print(
        "Índice final: "
        f"{registro['indice_confianca']:.2f}"
    )

    print(
        "Nível de confiança: "
        f"{registro['nivel_confianca']}"
    )

    alertas = registro["alertas"]

    if alertas:
        print("Alertas:")

        for alerta in alertas:
            print(f"- {alerta}")
    else:
        print("Alertas: nenhum")


def escanear_confrontos(times, analises):
    exemplos_over15 = []
    exemplos_btts = []

    total_confrontos = 0
    total_recomendacoes = 0
    total_recomendadas = 0
    total_nao_recomendadas = 0
    total_erros = 0

    times_disponiveis = [
        team_id
        for team_id in times
        if team_id in analises
    ]

    print("\nEscaneando confrontos...")

    for mandante_id in times_disponiveis:
        for visitante_id in times_disponiveis:
            if mandante_id == visitante_id:
                continue

            total_confrontos += 1

            resultado = RecommendationEngine(
                analise_mandante=analises[
                    mandante_id
                ],
                analise_visitante=analises[
                    visitante_id
                ]
            ).analisar()

            if resultado.get("erro"):
                total_erros += 1
                continue

            recomendacoes = resultado.get(
                "recomendacoes",
                []
            )

            for recomendacao in recomendacoes:
                total_recomendacoes += 1

                recomendado = recomendacao.get(
                    "recomendado",
                    False
                )

                if recomendado:
                    total_recomendadas += 1
                    continue

                total_nao_recomendadas += 1

                registro = montar_registro(
                    nome_mandante=times[
                        mandante_id
                    ],
                    nome_visitante=times[
                        visitante_id
                    ],
                    recomendacao=recomendacao
                )

                mercado = recomendacao.get(
                    "mercado",
                    ""
                )

                if (
                    mercado == "Over 1.5 gols"
                    and len(exemplos_over15)
                    < LIMITE_EXEMPLOS_POR_MERCADO
                ):
                    exemplos_over15.append(
                        registro
                    )

                if (
                    mercado == "BTTS - Ambos marcam"
                    and len(exemplos_btts)
                    < LIMITE_EXEMPLOS_POR_MERCADO
                ):
                    exemplos_btts.append(
                        registro
                    )

    return {
        "total_confrontos": total_confrontos,
        "total_recomendacoes": total_recomendacoes,
        "total_recomendadas": total_recomendadas,
        "total_nao_recomendadas": (
            total_nao_recomendadas
        ),
        "total_erros": total_erros,
        "exemplos_over15": exemplos_over15,
        "exemplos_btts": exemplos_btts
    }


def exibir_resultados(resultado):
    exemplos_over15 = resultado[
        "exemplos_over15"
    ]

    exemplos_btts = resultado[
        "exemplos_btts"
    ]

    print("\n")
    print("=" * 60)
    print("EXEMPLOS — OVER 1.5 NÃO RECOMENDADO")
    print("=" * 60)

    if exemplos_over15:
        for numero, registro in enumerate(
            exemplos_over15,
            start=1
        ):
            exibir_exemplo(numero, registro)
    else:
        print(
            "Nenhum exemplo de Over 1.5 não "
            "recomendado foi encontrado."
        )

    print("\n")
    print("=" * 60)
    print("EXEMPLOS — BTTS NÃO RECOMENDADO")
    print("=" * 60)

    if exemplos_btts:
        for numero, registro in enumerate(
            exemplos_btts,
            start=1
        ):
            exibir_exemplo(numero, registro)
    else:
        print(
            "Nenhum exemplo de BTTS não "
            "recomendado foi encontrado."
        )

    print("\n")
    print("=" * 60)
    print("RESUMO DO SCANNER")
    print("=" * 60)

    print(
        "Confrontos analisados: "
        f"{resultado['total_confrontos']}"
    )

    print(
        "Recomendações analisadas: "
        f"{resultado['total_recomendacoes']}"
    )

    print(
        "Recomendações positivas: "
        f"{resultado['total_recomendadas']}"
    )

    print(
        "Recomendações negativas: "
        f"{resultado['total_nao_recomendadas']}"
    )

    print(
        f"Erros encontrados: "
        f"{resultado['total_erros']}"
    )

    encontrou_over15 = bool(
        exemplos_over15
    )

    encontrou_btts = bool(
        exemplos_btts
    )

    print("\nValidações:")

    print(
        "Over 1.5 consegue dizer NÃO: "
        f"{'SIM' if encontrou_over15 else 'NÃO'}"
    )

    print(
        "BTTS consegue dizer NÃO: "
        f"{'SIM' if encontrou_btts else 'NÃO'}"
    )

    if (
        encontrou_over15
        and encontrou_btts
        and resultado["total_erros"] == 0
    ):
        print(
            "\nResultado geral: APROVADO"
        )
    else:
        print(
            "\nResultado geral: NECESSITA ANÁLISE"
        )


def main():
    dados = carregar_json(
        ARQUIVO_PARTIDAS
    )

    partidas = extrair_partidas(
        dados
    )

    times = extrair_times(
        partidas
    )

    print(
        f"Arquivo carregado: {ARQUIVO_PARTIDAS}"
    )

    print(
        f"Total de partidas: {len(partidas)}"
    )

    print(
        f"Total de times identificados: {len(times)}"
    )

    analises = gerar_analises_times(
        partidas=partidas,
        times=times
    )

    print(
        "Times com análise válida: "
        f"{len(analises)}"
    )

    resultado = escanear_confrontos(
        times=times,
        analises=analises
    )

    exibir_resultados(
        resultado
    )


if __name__ == "__main__":
    main()