"""
RiskManagementService: a Etapa E do roteiro "EntradaPro Autônomo" -
o sistema detecta sozinho sequências recentes ruins de resultados
por mercado e gera um alerta.

REGRA MAIS IMPORTANTE (definida pelo Bruno): isto é SEMPRE um
alerta/sugestão para o usuário ver, NUNCA uma ação automática que
mexe com dinheiro de verdade. O EntradaPro não aposta por
ninguém - só avisa quando os últimos resultados de um mercado não
andam bem, para o usuário decidir com mais informação.
"""

from db import conectar_banco


LIMITE_SEQUENCIA_RUIM = 5
JANELA_ANALISE = 15

MERCADOS_MONITORADOS = (
    "Mais de 1,5 gols",
    "Mais de 2,5 gols",
    "Ambas marcam — Sim",
)


def _buscar_ultimos_resultados(mercado, janela):
    with conectar_banco() as conexao:
        previsoes = conexao.execute(
            """
            SELECT status FROM previsoes
            WHERE mercado = ? AND status IN ('GREEN', 'RED')
            ORDER BY verificado_em DESC
            LIMIT ?
            """,
            (mercado, janela),
        ).fetchall()

    return [p["status"] for p in previsoes]


def _contar_sequencia_ruim_atual(resultados_recentes_primeiro):
    """
    Conta quantos RED seguidos existem a partir do resultado mais
    recente (para assim que aparecer um GREEN, a sequência é
    interrompida - é a "forma atual", não o total histórico).
    """
    sequencia = 0

    for status in resultados_recentes_primeiro:
        if status == "RED":
            sequencia += 1
        else:
            break

    return sequencia


def avaliar_sequencia_recente(
    mercado,
    limite_sequencia_ruim=LIMITE_SEQUENCIA_RUIM,
    janela=JANELA_ANALISE,
):
    """
    Avalia a sequência mais recente de resultados de um mercado
    específico. Retorna um alerta (não uma ação) quando a
    sequência ruim atual atinge o limite.
    """
    resultados = _buscar_ultimos_resultados(mercado, janela)

    sequencia_ruim = _contar_sequencia_ruim_atual(resultados)

    alerta_ativo = sequencia_ruim >= limite_sequencia_ruim

    if len(resultados) < limite_sequencia_ruim:
        mensagem = (
            f"Ainda não há resultados recentes suficientes de "
            f"'{mercado}' para avaliar a forma atual."
        )
    elif alerta_ativo:
        mensagem = (
            f"⚠️ Os últimos {sequencia_ruim} resultados de "
            f"'{mercado}' foram negativos. Considere mais "
            f"cautela com este mercado nos próximos dias."
        )
    else:
        mensagem = f"'{mercado}' está com forma recente normal."

    return {
        "mercado": mercado,
        "sequencia_ruim_atual": sequencia_ruim,
        "amostra_disponivel": len(resultados),
        "alerta_ativo": alerta_ativo,
        "mensagem": mensagem,
    }


def obter_status_risco_geral():
    """
    Avalia todos os mercados monitorados de uma vez. Retorna a
    lista de avaliações e quais têm alerta ativo no momento -
    para exibir na tela como aviso, nunca como bloqueio silencioso.
    """
    avaliacoes = [
        avaliar_sequencia_recente(mercado)
        for mercado in MERCADOS_MONITORADOS
    ]

    alertas_ativos = [a for a in avaliacoes if a["alerta_ativo"]]

    return {
        "avaliacoes": avaliacoes,
        "alertas_ativos": alertas_ativos,
        "tem_alerta": len(alertas_ativos) > 0,
    }
