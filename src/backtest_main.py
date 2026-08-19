from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from data_storage import carregar_json
from engines.backtest_engine import BacktestEngine
from engines.dataset_engine import DatasetEngine
from engines.performance_analytics import PerformanceAnalytics
from engines.strategy_optimizer import StrategyOptimizer


ARQUIVO_DATASET = "brasileirao_serie_a_2022.json"

ODD_OVER15 = 1.40
ODD_BTTS = 1.70

JANELA = 5
MINIMO_JOGOS_ANTERIORES = 5
STAKE_FIXA = 100.00
QUANTIDADE_RANKING = 10

MINIMO_APOSTAS_RECOMENDACAO = 10

PASTA_SAIDA = Path("data") / "processed"
ARQUIVO_SAIDA = PASTA_SAIDA / "performance_report_2022.json"


def salvar_json(
    dados: Dict[str, Any],
    caminho: Path,
) -> None:
    """
    Salva o relatório em um arquivo JSON.

    A pasta de destino é criada automaticamente
    caso ainda não exista.
    """

    caminho.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with caminho.open(
        mode="w",
        encoding="utf-8",
    ) as arquivo:
        json.dump(
            dados,
            arquivo,
            ensure_ascii=False,
            indent=4,
            default=str,
        )


def imprimir_resumo_dataset(
    resumo_dataset: Dict[str, Any],
) -> None:
    """
    Exibe as principais informações do DatasetEngine.
    """

    print("\n=== DATASET ENGINE ===")

    print(
        "Total recebido: "
        f"{resumo_dataset.get('total_recebido', 0)}"
    )

    print(
        "Partidas válidas: "
        f"{resumo_dataset.get('total_validas', 0)}"
    )

    print(
        "Partidas encerradas: "
        f"{resumo_dataset.get('total_encerradas', 0)}"
    )

    print(
        "Partidas não encerradas: "
        f"{resumo_dataset.get('total_nao_encerradas', 0)}"
    )

    print(
        "Times indexados: "
        f"{resumo_dataset.get('total_times_indexados', 0)}"
    )

    print(
        "Erros no dataset: "
        f"{resumo_dataset.get('total_erros', 0)}"
    )

    erros = resumo_dataset.get(
        "erros",
        [],
    )

    if erros:
        print("\nErros encontrados no dataset:")

        for erro in erros:
            print(f"- {erro}")


def imprimir_resumo_backtest(
    resultado_backtest: Dict[str, Any],
) -> None:
    """
    Exibe as principais métricas geradas
    pelo BacktestEngine.
    """

    print("\n=== BACKTEST ENGINE ===")

    print(
        "Partidas aptas: "
        f"{resultado_backtest.get('partidas_aptas', 0)}"
    )

    print(
        "Partidas processadas: "
        f"{resultado_backtest.get('partidas_processadas', 0)}"
    )

    print(
        "Partidas ignoradas: "
        f"{resultado_backtest.get('partidas_ignoradas', 0)}"
    )

    print(
        "Erros de processamento: "
        f"{resultado_backtest.get('erros_processamento', 0)}"
    )

    print(
        "Total de apostas: "
        f"{resultado_backtest.get('total_apostas', 0)}"
    )

    print(
        "Apostas de Over 1.5: "
        f"{resultado_backtest.get('apostas_over15', 0)}"
    )

    print(
        "Apostas de BTTS: "
        f"{resultado_backtest.get('apostas_btts', 0)}"
    )

    print(
        "Apostas vencedoras: "
        f"{resultado_backtest.get('apostas_vencedoras', 0)}"
    )

    print(
        "Apostas perdedoras: "
        f"{resultado_backtest.get('apostas_perdedoras', 0)}"
    )

    print(
        "Valor apostado: R$ "
        f"{resultado_backtest.get('valor_apostado', 0.0):.2f}"
    )

    print(
        "Retorno bruto: R$ "
        f"{resultado_backtest.get('retorno_bruto', 0.0):.2f}"
    )

    print(
        "Lucro líquido: R$ "
        f"{resultado_backtest.get('lucro_liquido', 0.0):.2f}"
    )

    print(
        "ROI: "
        f"{resultado_backtest.get('roi', 0.0):.2f}%"
    )


def imprimir_resumo_analytics(
    resultado_analytics: Dict[str, Any],
) -> None:
    """
    Exibe o resumo consolidado produzido
    pelo PerformanceAnalytics.
    """

    geral = resultado_analytics.get(
        "geral",
        {},
    )

    mercados = resultado_analytics.get(
        "mercados",
        {},
    )

    diagnostico = resultado_analytics.get(
        "diagnostico",
        {},
    )

    print("\n=== PERFORMANCE ANALYTICS ===")

    print(
        "Total de apostas analisadas: "
        f"{geral.get('total_apostas', 0)}"
    )

    print(
        "Taxa de acerto geral: "
        f"{geral.get('taxa_acerto', 0.0):.2f}%"
    )

    print(
        "Valor apostado analisado: R$ "
        f"{geral.get('valor_apostado', 0.0):.2f}"
    )

    print(
        "Lucro líquido analisado: R$ "
        f"{geral.get('lucro_liquido', 0.0):.2f}"
    )

    print(
        "ROI geral: "
        f"{geral.get('roi', 0.0):.2f}%"
    )

    print("\n=== MERCADOS ===")

    for codigo_mercado in (
        "over15",
        "btts",
    ):
        metricas = mercados.get(
            codigo_mercado,
            {},
        )

        nome = metricas.get(
            "nome",
            codigo_mercado,
        )

        print(f"\n{nome}")

        print(
            "  Total de apostas: "
            f"{metricas.get('total_apostas', 0)}"
        )

        print(
            "  Apostas vencedoras: "
            f"{metricas.get('apostas_vencedoras', 0)}"
        )

        print(
            "  Apostas perdedoras: "
            f"{metricas.get('apostas_perdedoras', 0)}"
        )

        print(
            "  Taxa de acerto: "
            f"{metricas.get('taxa_acerto', 0.0):.2f}%"
        )

        print(
            "  Valor apostado: R$ "
            f"{metricas.get('valor_apostado', 0.0):.2f}"
        )

        print(
            "  Lucro líquido: R$ "
            f"{metricas.get('lucro_liquido', 0.0):.2f}"
        )

        print(
            "  ROI: "
            f"{metricas.get('roi', 0.0):.2f}%"
        )

    print("\n=== DIAGNÓSTICO DO ANALYTICS ===")

    consistente = diagnostico.get(
        "consistente",
        False,
    )

    print(
        "Diagnóstico consistente: "
        f"{'SIM' if consistente else 'NÃO'}"
    )

    print(
        "Consistência do total de apostas: "
        f"{'SIM' if diagnostico.get('consistencia_total_apostas') else 'NÃO'}"
    )

    print(
        "Consistência do lucro: "
        f"{'SIM' if diagnostico.get('consistencia_lucro') else 'NÃO'}"
    )

    print(
        "Consistência do valor apostado: "
        f"{'SIM' if diagnostico.get('consistencia_valor_apostado') else 'NÃO'}"
    )

    alertas = diagnostico.get(
        "alertas",
        [],
    )

    if alertas:
        print("\nAlertas do Analytics:")

        for alerta in alertas:
            print(f"- {alerta}")
    else:
        print("Alertas do Analytics: nenhum")


def imprimir_melhor_corte(
    nome_mercado: str,
    recomendacao: Dict[str, Any],
) -> None:
    """
    Exibe o melhor ponto de corte localizado
    para um mercado.
    """

    print(f"\n{nome_mercado}")

    print(
        "  ROI da configuração atual: "
        f"{recomendacao.get('roi_configuracao_atual', 0.0):.2f}%"
    )

    print(
        "  Lucro da configuração atual: R$ "
        f"{recomendacao.get('lucro_configuracao_atual', 0.0):.2f}"
    )

    melhor_corte = recomendacao.get(
        "melhor_ponto_corte"
    )

    if melhor_corte is None:
        print(
            "  Melhor ponto de corte: "
            "nenhum corte lucrativo com amostra suficiente"
        )
    else:
        print(
            "  Probabilidade mínima sugerida: "
            f"{melhor_corte.get('probabilidade_minima', 0.0):.2f}%"
        )

        print(
            "  Total de apostas no corte: "
            f"{melhor_corte.get('total_apostas', 0)}"
        )

        print(
            "  Taxa de acerto no corte: "
            f"{melhor_corte.get('taxa_acerto', 0.0):.2f}%"
        )

        print(
            "  Lucro no corte: R$ "
            f"{melhor_corte.get('lucro_liquido', 0.0):.2f}"
        )

        print(
            "  ROI no corte: "
            f"{melhor_corte.get('roi', 0.0):.2f}%"
        )

    alertas = recomendacao.get(
        "alertas",
        [],
    )

    if alertas:
        print("  Alertas:")

        for alerta in alertas:
            print(f"  - {alerta}")
    else:
        print("  Alertas: nenhum")


def imprimir_resumo_optimizer(
    resultado_optimizer: Dict[str, Any],
) -> None:
    """
    Exibe os principais resultados do StrategyOptimizer.
    """

    geral = resultado_optimizer.get(
        "geral",
        {},
    )

    recomendacoes = resultado_optimizer.get(
        "recomendacoes",
        {},
    )

    diagnostico = resultado_optimizer.get(
        "diagnostico",
        {},
    )

    print("\n=== STRATEGY OPTIMIZER ===")

    print(
        "Total de apostas analisadas: "
        f"{geral.get('total_apostas', 0)}"
    )

    print(
        "Lucro líquido analisado: R$ "
        f"{geral.get('lucro_liquido', 0.0):.2f}"
    )

    print(
        "ROI analisado: "
        f"{geral.get('roi', 0.0):.2f}%"
    )

    print("\n=== RECOMENDAÇÕES DE CORTE ===")

    for mercado in (
        "over15",
        "btts",
    ):
        recomendacao = recomendacoes.get(
            mercado,
            {},
        )

        nome_mercado = recomendacao.get(
            "nome",
            mercado,
        )

        imprimir_melhor_corte(
            nome_mercado=nome_mercado,
            recomendacao=recomendacao,
        )

    print("\n=== DIAGNÓSTICO DO OPTIMIZER ===")

    print(
        "Diagnóstico consistente: "
        f"{'SIM' if diagnostico.get('consistente') else 'NÃO'}"
    )

    print(
        "Consistência do total de apostas: "
        f"{'SIM' if diagnostico.get('consistencia_total_apostas') else 'NÃO'}"
    )

    print(
        "Consistência do lucro: "
        f"{'SIM' if diagnostico.get('consistencia_lucro') else 'NÃO'}"
    )

    print(
        "Consistência do Over 1.5: "
        f"{'SIM' if diagnostico.get('consistencia_apostas_over15') else 'NÃO'}"
    )

    print(
        "Consistência do BTTS: "
        f"{'SIM' if diagnostico.get('consistencia_apostas_btts') else 'NÃO'}"
    )

    alertas = diagnostico.get(
        "alertas",
        [],
    )

    if alertas:
        print("\nAlertas do Optimizer:")

        for alerta in alertas:
            print(f"- {alerta}")
    else:
        print("Alertas do Optimizer: nenhum")


def montar_relatorio_completo(
    resumo_dataset: Dict[str, Any],
    resultado_backtest: Dict[str, Any],
    resultado_analytics: Dict[str, Any],
    resultado_optimizer: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Monta o relatório final com configurações,
    dataset, backtest, analytics e optimizer.
    """

    return {
        "configuracao": {
            "arquivo_dataset": ARQUIVO_DATASET,
            "odd_over15": ODD_OVER15,
            "odd_btts": ODD_BTTS,
            "janela": JANELA,
            "minimo_jogos_anteriores": (
                MINIMO_JOGOS_ANTERIORES
            ),
            "stake_fixa": STAKE_FIXA,
            "quantidade_ranking": QUANTIDADE_RANKING,
            "minimo_apostas_recomendacao": (
                MINIMO_APOSTAS_RECOMENDACAO
            ),
        },
        "dataset": resumo_dataset,
        "backtest": resultado_backtest,
        "analytics": resultado_analytics,
        "strategy_optimizer": resultado_optimizer,
    }


def main() -> None:
    """
    Executa o fluxo oficial de backtest do FootballAI.
    """

    print("=== FOOTBALLAI — BACKTEST OFICIAL ===")

    print(
        f"\nCarregando arquivo: {ARQUIVO_DATASET}"
    )

    dados = carregar_json(
        ARQUIVO_DATASET
    )

    dataset_engine = DatasetEngine(
        dados=dados
    )

    resumo_dataset = dataset_engine.resumo()

    imprimir_resumo_dataset(
        resumo_dataset
    )

    print("\nExecutando BacktestEngine...")

    backtest_engine = BacktestEngine(
        dataset_engine=dataset_engine,
        odd_over15=ODD_OVER15,
        odd_btts=ODD_BTTS,
        janela=JANELA,
        minimo_jogos_anteriores=(
            MINIMO_JOGOS_ANTERIORES
        ),
        stake_fixa=STAKE_FIXA,
    )

    resultado_backtest = (
        backtest_engine.executar()
    )

    imprimir_resumo_backtest(
        resultado_backtest
    )

    print("\nExecutando PerformanceAnalytics...")

    performance_analytics = PerformanceAnalytics(
        resultado_backtest=resultado_backtest,
        quantidade_ranking=QUANTIDADE_RANKING,
    )

    resultado_analytics = (
        performance_analytics.executar()
    )

    imprimir_resumo_analytics(
        resultado_analytics
    )

    print("\nExecutando StrategyOptimizer...")

    strategy_optimizer = StrategyOptimizer(
        resultado_backtest=resultado_backtest,
        minimo_apostas_recomendacao=(
            MINIMO_APOSTAS_RECOMENDACAO
        ),
    )

    resultado_optimizer = (
        strategy_optimizer.executar()
    )

    imprimir_resumo_optimizer(
        resultado_optimizer
    )

    relatorio_completo = montar_relatorio_completo(
        resumo_dataset=resumo_dataset,
        resultado_backtest=resultado_backtest,
        resultado_analytics=resultado_analytics,
        resultado_optimizer=resultado_optimizer,
    )

    salvar_json(
        dados=relatorio_completo,
        caminho=ARQUIVO_SAIDA,
    )

    print("\nRelatório salvo com sucesso em:")

    print(
        ARQUIVO_SAIDA.resolve()
    )

    diagnostico_analytics = resultado_analytics.get(
        "diagnostico",
        {},
    )

    diagnostico_optimizer = resultado_optimizer.get(
        "diagnostico",
        {},
    )

    erros_processamento = resultado_backtest.get(
        "erros_processamento",
        0,
    )

    aprovado = all(
        (
            diagnostico_analytics.get(
                "consistente",
                False,
            ),
            diagnostico_optimizer.get(
                "consistente",
                False,
            ),
            erros_processamento == 0,
        )
    )

    if aprovado:
        print("\nRESULTADO FINAL: APROVADO")
    else:
        print(
            "\nRESULTADO FINAL: "
            "REVISÃO NECESSÁRIA"
        )


if __name__ == "__main__":
    main()