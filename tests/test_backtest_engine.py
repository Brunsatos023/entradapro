import os
import sys
import time
from math import isclose


DIRETORIO_TESTES = os.path.dirname(
    os.path.abspath(__file__)
)

DIRETORIO_PROJETO = os.path.dirname(
    DIRETORIO_TESTES
)

DIRETORIO_SRC = os.path.join(
    DIRETORIO_PROJETO,
    "src"
)

if DIRETORIO_SRC not in sys.path:
    sys.path.insert(
        0,
        DIRETORIO_SRC
    )


from data_storage import carregar_json
from engines.dataset_engine import DatasetEngine
from engines.backtest_engine import BacktestEngine


ARQUIVO_JSON = "brasileirao_serie_a_2024.json"

ODD_OVER15 = 1.40
ODD_BTTS = 1.70

JANELA = 5
MINIMO_JOGOS_ANTERIORES = 5
STAKE_FIXA = 100.00


def carregar_dataset():
    dados = carregar_json(
        ARQUIVO_JSON
    )

    if not isinstance(
        dados,
        dict
    ):
        raise TypeError(
            "O arquivo JSON precisa retornar "
            "um dicionário."
        )

    partidas = dados.get(
        "response"
    )

    if not isinstance(
        partidas,
        list
    ):
        raise TypeError(
            "A chave 'response' precisa conter "
            "uma lista de partidas."
        )

    if not partidas:
        raise ValueError(
            "Nenhuma partida foi encontrada "
            "no dataset."
        )

    return dados


def validar_chaves_principais(
    resultado
):
    if not isinstance(
        resultado,
        dict
    ):
        raise AssertionError(
            "O BacktestEngine não retornou "
            "um dicionário."
        )

    chaves_obrigatorias = {
        "partidas_aptas",
        "partidas_processadas",
        "partidas_ignoradas",
        "erros_processamento",

        "acertos_over15",
        "erros_over15",

        "acertos_btts",
        "erros_btts",

        "taxa_acerto_over15",
        "taxa_acerto_btts",
        "taxa_acerto_geral",

        "stake_fixa",

        "apostas_over15",
        "apostas_btts",
        "total_apostas",

        "apostas_vencedoras",
        "apostas_perdedoras",

        "valor_apostado",
        "retorno_bruto",
        "lucro_liquido",

        "lucro_over15",
        "lucro_btts",

        "roi",

        "maior_sequencia_vitorias",
        "maior_sequencia_derrotas",

        "historico_partidas",
        "curva_saldo",
        "detalhes_erros"
    }

    chaves_faltantes = (
        chaves_obrigatorias
        - set(resultado.keys())
    )

    if chaves_faltantes:
        raise AssertionError(
            "Chaves ausentes no resultado: "
            f"{sorted(chaves_faltantes)}"
        )


def validar_processamento(
    resultado
):
    partidas_aptas = resultado[
        "partidas_aptas"
    ]

    partidas_processadas = resultado[
        "partidas_processadas"
    ]

    partidas_ignoradas = resultado[
        "partidas_ignoradas"
    ]

    erros_processamento = resultado[
        "erros_processamento"
    ]

    total_classificado = (
        partidas_processadas
        + partidas_ignoradas
        + erros_processamento
    )

    if total_classificado != partidas_aptas:
        raise AssertionError(
            "A soma das partidas processadas, "
            "ignoradas e com erro não corresponde "
            "ao total de partidas aptas."
        )

    total_over15 = (
        resultado["acertos_over15"]
        + resultado["erros_over15"]
    )

    if total_over15 != partidas_processadas:
        raise AssertionError(
            "A soma dos acertos e erros de Over 1.5 "
            "não corresponde às partidas processadas."
        )

    total_btts = (
        resultado["acertos_btts"]
        + resultado["erros_btts"]
    )

    if total_btts != partidas_processadas:
        raise AssertionError(
            "A soma dos acertos e erros de BTTS "
            "não corresponde às partidas processadas."
        )


def validar_taxas_acerto(
    resultado
):
    for chave_taxa in (
        "taxa_acerto_over15",
        "taxa_acerto_btts",
        "taxa_acerto_geral"
    ):
        taxa = resultado[
            chave_taxa
        ]

        if not isinstance(
            taxa,
            (int, float)
        ):
            raise AssertionError(
                f"A métrica '{chave_taxa}' "
                "não é numérica."
            )

        if taxa < 0 or taxa > 100:
            raise AssertionError(
                f"A métrica '{chave_taxa}' "
                "está fora do intervalo de 0 a 100."
            )

    partidas_processadas = resultado[
        "partidas_processadas"
    ]

    if partidas_processadas == 0:
        return

    taxa_over15_esperada = round(
        resultado["acertos_over15"]
        * 100
        / partidas_processadas,
        2
    )

    taxa_btts_esperada = round(
        resultado["acertos_btts"]
        * 100
        / partidas_processadas,
        2
    )

    total_acertos = (
        resultado["acertos_over15"]
        + resultado["acertos_btts"]
    )

    taxa_geral_esperada = round(
        total_acertos
        * 100
        / (partidas_processadas * 2),
        2
    )

    if resultado["taxa_acerto_over15"] != (
        taxa_over15_esperada
    ):
        raise AssertionError(
            "A taxa de acerto de Over 1.5 "
            "não corresponde aos totais registrados."
        )

    if resultado["taxa_acerto_btts"] != (
        taxa_btts_esperada
    ):
        raise AssertionError(
            "A taxa de acerto de BTTS "
            "não corresponde aos totais registrados."
        )

    if resultado["taxa_acerto_geral"] != (
        taxa_geral_esperada
    ):
        raise AssertionError(
            "A taxa de acerto geral "
            "não corresponde aos totais registrados."
        )


def validar_apostas(
    resultado
):
    apostas_over15 = resultado[
        "apostas_over15"
    ]

    apostas_btts = resultado[
        "apostas_btts"
    ]

    total_apostas = resultado[
        "total_apostas"
    ]

    if (
        apostas_over15
        + apostas_btts
        != total_apostas
    ):
        raise AssertionError(
            "A soma das apostas de Over 1.5 e BTTS "
            "não corresponde ao total de apostas."
        )

    apostas_vencedoras = resultado[
        "apostas_vencedoras"
    ]

    apostas_perdedoras = resultado[
        "apostas_perdedoras"
    ]

    if (
        apostas_vencedoras
        + apostas_perdedoras
        != total_apostas
    ):
        raise AssertionError(
            "A soma das apostas vencedoras e perdedoras "
            "não corresponde ao total de apostas."
        )

    if apostas_over15 > resultado[
        "partidas_processadas"
    ]:
        raise AssertionError(
            "O número de apostas em Over 1.5 "
            "é maior que o número de partidas processadas."
        )

    if apostas_btts > resultado[
        "partidas_processadas"
    ]:
        raise AssertionError(
            "O número de apostas em BTTS "
            "é maior que o número de partidas processadas."
        )


def validar_financeiro(
    resultado
):
    campos_financeiros = (
        "stake_fixa",
        "valor_apostado",
        "retorno_bruto",
        "lucro_liquido",
        "lucro_over15",
        "lucro_btts",
        "roi"
    )

    for campo in campos_financeiros:
        valor = resultado[
            campo
        ]

        if not isinstance(
            valor,
            (int, float)
        ):
            raise AssertionError(
                f"O campo financeiro '{campo}' "
                "não é numérico."
            )

    if resultado["stake_fixa"] <= 0:
        raise AssertionError(
            "A stake fixa precisa ser maior que zero."
        )

    valor_apostado_esperado = round(
        resultado["total_apostas"]
        * resultado["stake_fixa"],
        2
    )

    if not isclose(
        resultado["valor_apostado"],
        valor_apostado_esperado,
        abs_tol=0.01
    ):
        raise AssertionError(
            "O valor apostado não corresponde ao total "
            "de apostas multiplicado pela stake fixa."
        )

    lucro_esperado = round(
        resultado["retorno_bruto"]
        - resultado["valor_apostado"],
        2
    )

    if not isclose(
        resultado["lucro_liquido"],
        lucro_esperado,
        abs_tol=0.01
    ):
        raise AssertionError(
            "O lucro líquido não corresponde ao retorno "
            "bruto menos o valor apostado."
        )

    lucro_mercados = round(
        resultado["lucro_over15"]
        + resultado["lucro_btts"],
        2
    )

    if not isclose(
        resultado["lucro_liquido"],
        lucro_mercados,
        abs_tol=0.01
    ):
        raise AssertionError(
            "A soma do lucro de Over 1.5 e BTTS "
            "não corresponde ao lucro líquido total."
        )

    if resultado["valor_apostado"] > 0:
        roi_esperado = round(
            resultado["lucro_liquido"]
            * 100
            / resultado["valor_apostado"],
            2
        )
    else:
        roi_esperado = 0.0

    if not isclose(
        resultado["roi"],
        roi_esperado,
        abs_tol=0.01
    ):
        raise AssertionError(
            "O ROI não corresponde ao lucro líquido "
            "dividido pelo valor apostado."
        )


def validar_historico_partidas(
    resultado
):
    historico = resultado[
        "historico_partidas"
    ]

    if not isinstance(
        historico,
        list
    ):
        raise AssertionError(
            "O histórico de partidas não é uma lista."
        )

    if len(historico) != resultado[
        "partidas_processadas"
    ]:
        raise AssertionError(
            "A quantidade de registros no histórico "
            "não corresponde às partidas processadas."
        )

    chaves_registro = {
        "fixture_id",
        "data",

        "mandante_id",
        "visitante_id",

        "mandante",
        "visitante",

        "gols_mandante",
        "gols_visitante",

        "probabilidade_over15",
        "probabilidade_btts",

        "over15_real",
        "btts_real",

        "over15_previsto",
        "btts_previsto",

        "acertou_over15",
        "acertou_btts",

        "odd_over15",
        "odd_btts",

        "aposta_over15_realizada",
        "aposta_btts_realizada",

        "lucro_over15",
        "lucro_btts",
        "lucro_total_partida",
        "saldo_apos_partida"
    }

    total_apostas_historico = 0

    for indice, registro in enumerate(
        historico,
        start=1
    ):
        if not isinstance(
            registro,
            dict
        ):
            raise AssertionError(
                f"O registro {indice} do histórico "
                "não é um dicionário."
            )

        faltantes = (
            chaves_registro
            - set(registro.keys())
        )

        if faltantes:
            raise AssertionError(
                f"O registro {indice} do histórico "
                "não contém as chaves: "
                f"{sorted(faltantes)}"
            )

        if registro[
            "aposta_over15_realizada"
        ]:
            total_apostas_historico += 1

        if registro[
            "aposta_btts_realizada"
        ]:
            total_apostas_historico += 1

        lucro_partida_esperado = round(
            registro["lucro_over15"]
            + registro["lucro_btts"],
            2
        )

        if not isclose(
            registro["lucro_total_partida"],
            lucro_partida_esperado,
            abs_tol=0.01
        ):
            raise AssertionError(
                f"O lucro total da partida no registro "
                f"{indice} está inconsistente."
            )

    if total_apostas_historico != resultado[
        "total_apostas"
    ]:
        raise AssertionError(
            "O total de apostas encontrado no histórico "
            "não corresponde ao total geral."
        )


def validar_curva_saldo(
    resultado
):
    curva = resultado[
        "curva_saldo"
    ]

    if not isinstance(
        curva,
        list
    ):
        raise AssertionError(
            "A curva de saldo não é uma lista."
        )

    if len(curva) != resultado[
        "total_apostas"
    ]:
        raise AssertionError(
            "A quantidade de pontos da curva de saldo "
            "não corresponde ao total de apostas."
        )

    chaves_curva = {
        "numero_aposta",
        "fixture_id",
        "mercado",
        "venceu",
        "odd",
        "stake",
        "lucro",
        "saldo"
    }

    saldo_calculado = 0.0

    for indice, aposta in enumerate(
        curva,
        start=1
    ):
        if not isinstance(
            aposta,
            dict
        ):
            raise AssertionError(
                f"O ponto {indice} da curva de saldo "
                "não é um dicionário."
            )

        faltantes = (
            chaves_curva
            - set(aposta.keys())
        )

        if faltantes:
            raise AssertionError(
                f"O ponto {indice} da curva de saldo "
                "não contém as chaves: "
                f"{sorted(faltantes)}"
            )

        if aposta[
            "numero_aposta"
        ] != indice:
            raise AssertionError(
                "A numeração da curva de saldo "
                "não está em ordem sequencial."
            )

        if aposta[
            "mercado"
        ] not in {
            "over15",
            "btts"
        }:
            raise AssertionError(
                f"Mercado inválido encontrado "
                f"na aposta {indice}."
            )

        saldo_calculado = round(
            saldo_calculado
            + aposta["lucro"],
            2
        )

        if not isclose(
            aposta["saldo"],
            saldo_calculado,
            abs_tol=0.01
        ):
            raise AssertionError(
                f"O saldo acumulado da aposta {indice} "
                "está inconsistente."
            )

    if curva:
        saldo_final = curva[
            -1
        ]["saldo"]

        if not isclose(
            saldo_final,
            resultado["lucro_liquido"],
            abs_tol=0.01
        ):
            raise AssertionError(
                "O último saldo da curva não corresponde "
                "ao lucro líquido total."
            )
    else:
        if resultado["lucro_liquido"] != 0:
            raise AssertionError(
                "Não existem apostas, mas o lucro líquido "
                "é diferente de zero."
            )


def validar_sequencias(
    resultado
):
    maior_vitorias = resultado[
        "maior_sequencia_vitorias"
    ]

    maior_derrotas = resultado[
        "maior_sequencia_derrotas"
    ]

    if not isinstance(
        maior_vitorias,
        int
    ):
        raise AssertionError(
            "A maior sequência de vitórias "
            "não é um número inteiro."
        )

    if not isinstance(
        maior_derrotas,
        int
    ):
        raise AssertionError(
            "A maior sequência de derrotas "
            "não é um número inteiro."
        )

    if maior_vitorias < 0:
        raise AssertionError(
            "A maior sequência de vitórias "
            "não pode ser negativa."
        )

    if maior_derrotas < 0:
        raise AssertionError(
            "A maior sequência de derrotas "
            "não pode ser negativa."
        )

    if maior_vitorias > resultado[
        "apostas_vencedoras"
    ]:
        raise AssertionError(
            "A maior sequência de vitórias é maior "
            "que o total de apostas vencedoras."
        )

    if maior_derrotas > resultado[
        "apostas_perdedoras"
    ]:
        raise AssertionError(
            "A maior sequência de derrotas é maior "
            "que o total de apostas perdedoras."
        )


def validar_detalhes_erros(
    resultado
):
    detalhes_erros = resultado[
        "detalhes_erros"
    ]

    if not isinstance(
        detalhes_erros,
        list
    ):
        raise AssertionError(
            "Os detalhes de erros não estão "
            "armazenados em uma lista."
        )

    if len(detalhes_erros) != resultado[
        "erros_processamento"
    ]:
        raise AssertionError(
            "A quantidade de detalhes de erros "
            "não corresponde ao total de erros."
        )


def validar_resultado(
    resultado
):
    validar_chaves_principais(
        resultado
    )

    validar_processamento(
        resultado
    )

    validar_taxas_acerto(
        resultado
    )

    validar_apostas(
        resultado
    )

    validar_financeiro(
        resultado
    )

    validar_historico_partidas(
        resultado
    )

    validar_curva_saldo(
        resultado
    )

    validar_sequencias(
        resultado
    )

    validar_detalhes_erros(
        resultado
    )


def exibir_relatorio(
    resultado,
    tempo_execucao
):
    print()
    print("=== BACKTEST ANALYTICS FOOTBALLAI ===")

    print()
    print("PROCESSAMENTO")

    print(
        f"Partidas aptas: "
        f"{resultado['partidas_aptas']}"
    )

    print(
        f"Partidas processadas: "
        f"{resultado['partidas_processadas']}"
    )

    print(
        f"Partidas ignoradas: "
        f"{resultado['partidas_ignoradas']}"
    )

    print(
        f"Erros de processamento: "
        f"{resultado['erros_processamento']}"
    )

    print()
    print("PRECISÃO")

    print(
        f"Over 1.5: "
        f"{resultado['taxa_acerto_over15']}%"
    )

    print(
        f"BTTS: "
        f"{resultado['taxa_acerto_btts']}%"
    )

    print(
        f"Taxa geral: "
        f"{resultado['taxa_acerto_geral']}%"
    )

    print()
    print("APOSTAS")

    print(
        f"Total de apostas: "
        f"{resultado['total_apostas']}"
    )

    print(
        f"Apostas Over 1.5: "
        f"{resultado['apostas_over15']}"
    )

    print(
        f"Apostas BTTS: "
        f"{resultado['apostas_btts']}"
    )

    print(
        f"Apostas vencedoras: "
        f"{resultado['apostas_vencedoras']}"
    )

    print(
        f"Apostas perdedoras: "
        f"{resultado['apostas_perdedoras']}"
    )

    print()
    print("RESULTADO FINANCEIRO")

    print(
        f"Stake fixa: "
        f"R$ {resultado['stake_fixa']:.2f}"
    )

    print(
        f"Valor apostado: "
        f"R$ {resultado['valor_apostado']:.2f}"
    )

    print(
        f"Retorno bruto: "
        f"R$ {resultado['retorno_bruto']:.2f}"
    )

    print(
        f"Lucro líquido: "
        f"R$ {resultado['lucro_liquido']:.2f}"
    )

    print(
        f"ROI: "
        f"{resultado['roi']}%"
    )

    print()
    print("LUCRO POR MERCADO")

    print(
        f"Over 1.5: "
        f"R$ {resultado['lucro_over15']:.2f}"
    )

    print(
        f"BTTS: "
        f"R$ {resultado['lucro_btts']:.2f}"
    )

    print()
    print("SEQUÊNCIAS")

    print(
        f"Maior sequência de vitórias: "
        f"{resultado['maior_sequencia_vitorias']}"
    )

    print(
        f"Maior sequência de derrotas: "
        f"{resultado['maior_sequencia_derrotas']}"
    )

    print()
    print("REGISTROS")

    print(
        f"Histórico de partidas: "
        f"{len(resultado['historico_partidas'])}"
    )

    print(
        f"Pontos na curva de saldo: "
        f"{len(resultado['curva_saldo'])}"
    )

    print()
    print(
        f"Tempo de execução: "
        f"{tempo_execucao:.2f} segundos"
    )

    detalhes_erros = resultado[
        "detalhes_erros"
    ]

    if detalhes_erros:
        print()
        print("PRIMEIROS ERROS ENCONTRADOS")

        for erro in detalhes_erros[:5]:
            print(
                f"Fixture "
                f"{erro.get('fixture_id')}: "
                f"{erro.get('erro')}"
            )

    print()
    print(
        "TESTE APROVADO: "
        "Backtest Analytics executado "
        "e validado com sucesso."
    )


def executar_teste():
    dados = carregar_dataset()

    dataset_engine = DatasetEngine(
        dados
    )

    resumo_dataset = (
        dataset_engine.resumo()
    )

    print()
    print("Dataset carregado")

    print(
        f"Partidas válidas: "
        f"{resumo_dataset['total_validas']}"
    )

    print(
        f"Partidas encerradas: "
        f"{resumo_dataset['total_encerradas']}"
    )

    print()
    print(
        "Executando o Backtest Analytics. "
        "Aguarde até a conclusão..."
    )

    inicio = time.perf_counter()

    resultado = BacktestEngine(
        dataset_engine=dataset_engine,
        odd_over15=ODD_OVER15,
        odd_btts=ODD_BTTS,
        janela=JANELA,
        minimo_jogos_anteriores=(
            MINIMO_JOGOS_ANTERIORES
        ),
        stake_fixa=STAKE_FIXA
    ).executar()

    fim = time.perf_counter()

    tempo_execucao = (
        fim - inicio
    )

    validar_resultado(
        resultado
    )

    exibir_relatorio(
        resultado=resultado,
        tempo_execucao=tempo_execucao
    )


if __name__ == "__main__":
    executar_teste()