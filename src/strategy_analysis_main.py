import json
from pathlib import Path


PASTA_RELATORIOS = Path("data") / "processed"

RELATORIOS = {
    2022: PASTA_RELATORIOS / "performance_report_2022.json",
    2023: PASTA_RELATORIOS / "performance_report_2023.json",
    2024: PASTA_RELATORIOS / "performance_report.json",
}

MERCADOS = {
    "over15": "Over 1.5",
    "btts": "BTTS",
}

CORTES_ANALISADOS = (
    50.0,
    55.0,
    60.0,
    65.0,
    70.0,
    75.0,
    80.0,
    85.0,
    90.0,
)


def carregar_relatorio(caminho):
    if not caminho.exists():
        raise FileNotFoundError(
            f"Relatório não encontrado: {caminho}"
        )

    with caminho.open(
        "r",
        encoding="utf-8"
    ) as arquivo:
        return json.load(arquivo)


def obter_cortes_mercado(
    relatorio,
    mercado
):
    try:
        return relatorio[
            "strategy_optimizer"
        ][
            "comparacao_pontos_corte"
        ][
            mercado
        ]

    except KeyError as erro:
        raise KeyError(
            f"Não foi possível localizar "
            f"os cortes do mercado '{mercado}'."
        ) from erro


def indexar_cortes(cortes):
    return {
        float(
            item["probabilidade_minima"]
        ): item
        for item in cortes
    }


def consolidar_corte(
    corte,
    dados_temporadas
):
    total_apostas = 0
    vencedoras = 0
    perdedoras = 0

    valor_apostado = 0.0
    retorno_bruto = 0.0
    lucro_liquido = 0.0

    temporadas_positivas = 0
    temporadas_negativas = 0
    temporadas_neutras = 0

    detalhes = []

    for ano, cortes in dados_temporadas.items():
        resultado = cortes.get(corte)

        if resultado is None:
            continue

        apostas = int(
            resultado.get(
                "total_apostas",
                0
            )
        )

        greens = int(
            resultado.get(
                "apostas_vencedoras",
                0
            )
        )

        reds = int(
            resultado.get(
                "apostas_perdedoras",
                0
            )
        )

        apostado = float(
            resultado.get(
                "valor_apostado",
                0.0
            )
        )

        retorno = float(
            resultado.get(
                "retorno_bruto",
                0.0
            )
        )

        lucro = float(
            resultado.get(
                "lucro_liquido",
                0.0
            )
        )

        roi = float(
            resultado.get(
                "roi",
                0.0
            )
        )

        total_apostas += apostas
        vencedoras += greens
        perdedoras += reds

        valor_apostado += apostado
        retorno_bruto += retorno
        lucro_liquido += lucro

        if roi > 0:
            temporadas_positivas += 1

        elif roi < 0:
            temporadas_negativas += 1

        else:
            temporadas_neutras += 1

        detalhes.append(
            {
                "ano": ano,
                "apostas": apostas,
                "greens": greens,
                "reds": reds,
                "taxa_acerto": float(
                    resultado.get(
                        "taxa_acerto",
                        0.0
                    )
                ),
                "roi": roi,
                "lucro": lucro,
                "amostra_suficiente": bool(
                    resultado.get(
                        "amostra_suficiente",
                        False
                    )
                ),
            }
        )

    taxa_acerto = (
        vencedoras
        * 100
        / total_apostas
        if total_apostas > 0
        else 0.0
    )

    roi_consolidado = (
        lucro_liquido
        * 100
        / valor_apostado
        if valor_apostado > 0
        else 0.0
    )

    return {
        "corte": corte,
        "total_apostas": total_apostas,
        "vencedoras": vencedoras,
        "perdedoras": perdedoras,
        "taxa_acerto": round(
            taxa_acerto,
            2
        ),
        "valor_apostado": round(
            valor_apostado,
            2
        ),
        "retorno_bruto": round(
            retorno_bruto,
            2
        ),
        "lucro_liquido": round(
            lucro_liquido,
            2
        ),
        "roi": round(
            roi_consolidado,
            2
        ),
        "temporadas_positivas": (
            temporadas_positivas
        ),
        "temporadas_negativas": (
            temporadas_negativas
        ),
        "temporadas_neutras": (
            temporadas_neutras
        ),
        "detalhes": detalhes,
    }


def classificar_robustez(resultado):
    apostas = resultado[
        "total_apostas"
    ]

    positivas = resultado[
        "temporadas_positivas"
    ]

    negativas = resultado[
        "temporadas_negativas"
    ]

    roi = resultado[
        "roi"
    ]

    if (
        apostas >= 100
        and positivas == 3
        and roi > 0
    ):
        return "ROBUSTA"

    if (
        apostas >= 50
        and positivas >= 2
        and negativas <= 1
        and roi > 0
    ):
        return "PROMISSORA"

    if (
        apostas >= 20
        and roi > 0
    ):
        return "EXPERIMENTAL"

    return "NÃO VALIDADA"


def imprimir_resultado(resultado):
    print(
        f"\n=== CORTE >= "
        f"{resultado['corte']:.0f} ==="
    )

    print(
        "Total de apostas: "
        f"{resultado['total_apostas']}"
    )

    print(
        "Greens: "
        f"{resultado['vencedoras']}"
    )

    print(
        "Reds: "
        f"{resultado['perdedoras']}"
    )

    print(
        "Taxa de acerto: "
        f"{resultado['taxa_acerto']:.2f}%"
    )

    print(
        "Lucro líquido: "
        f"R$ {resultado['lucro_liquido']:.2f}"
    )

    print(
        "ROI consolidado: "
        f"{resultado['roi']:.2f}%"
    )

    print(
        "Temporadas positivas: "
        f"{resultado['temporadas_positivas']}/3"
    )

    print(
        "Robustez: "
        f"{classificar_robustez(resultado)}"
    )

    print("\nPor temporada:")

    for detalhe in resultado["detalhes"]:
        print(
            f"  {detalhe['ano']} | "
            f"{detalhe['apostas']} apostas | "
            f"{detalhe['taxa_acerto']:.2f}% acerto | "
            f"ROI {detalhe['roi']:+.2f}%"
        )


def analisar_mercado(
    mercado,
    nome_mercado
):
    print(
        "\n\n###################################"
    )
    print(
        f"MERCADO: {nome_mercado}"
    )
    print(
        "###################################"
    )

    dados_temporadas = {}

    for ano, caminho in RELATORIOS.items():
        relatorio = carregar_relatorio(
            caminho
        )

        cortes = obter_cortes_mercado(
            relatorio=relatorio,
            mercado=mercado
        )

        dados_temporadas[ano] = (
            indexar_cortes(
                cortes
            )
        )

    resultados = []

    for corte in CORTES_ANALISADOS:
        resultado = consolidar_corte(
            corte=corte,
            dados_temporadas=(
                dados_temporadas
            )
        )

        resultados.append(
            resultado
        )

        imprimir_resultado(
            resultado
        )

    validos = [
        resultado
        for resultado in resultados
        if (
            resultado[
                "total_apostas"
            ] >= 50
            and resultado[
                "roi"
            ] > 0
            and resultado[
                "temporadas_negativas"
            ] <= 1
        )
    ]

    print(
        "\n==================================="
    )
    print(
        f"RESULTADO ESTRATÉGICO — "
        f"{nome_mercado}"
    )
    print(
        "==================================="
    )

    if not validos:
        print(
            "Nenhum corte atingiu os "
            "critérios mínimos definidos."
        )

        return None

    melhor = max(
        validos,
        key=lambda item: (
            item[
                "temporadas_positivas"
            ],
            item[
                "roi"
            ],
            item[
                "total_apostas"
            ],
        )
    )

    print(
        "\nCorte mais consistente: "
        f">= {melhor['corte']:.0f}"
    )

    print(
        "Total de apostas: "
        f"{melhor['total_apostas']}"
    )

    print(
        "Taxa de acerto: "
        f"{melhor['taxa_acerto']:.2f}%"
    )

    print(
        "ROI consolidado: "
        f"{melhor['roi']:.2f}%"
    )

    print(
        "Temporadas positivas: "
        f"{melhor['temporadas_positivas']}/3"
    )

    print(
        "Classificação: "
        f"{classificar_robustez(melhor)}"
    )

    return melhor


def main():
    print(
        "\n=== FOOTBALLAI — "
        "VALIDAÇÃO MULTITEMPORADA ==="
    )

    resultados_finais = {}

    for mercado, nome_mercado in MERCADOS.items():
        resultados_finais[
            mercado
        ] = analisar_mercado(
            mercado=mercado,
            nome_mercado=nome_mercado
        )

    print(
        "\n\n==================================="
    )
    print(
        "RESUMO FINAL FOOTBALLAI"
    )
    print(
        "==================================="
    )

    for mercado, nome_mercado in MERCADOS.items():
        resultado = resultados_finais[
            mercado
        ]

        print(
            f"\n{nome_mercado}:"
        )

        if resultado is None:
            print(
                "  Nenhum corte validado."
            )

            continue

        print(
            "  Corte: >= "
            f"{resultado['corte']:.0f}"
        )

        print(
            "  Total de apostas: "
            f"{resultado['total_apostas']}"
        )

        print(
            "  Taxa de acerto: "
            f"{resultado['taxa_acerto']:.2f}%"
        )

        print(
            "  ROI: "
            f"{resultado['roi']:.2f}%"
        )

        print(
            "  Robustez: "
            f"{classificar_robustez(resultado)}"
        )


if __name__ == "__main__":
    main()