"""
AutoTuningService: a Etapa D do roteiro "EntradaPro Autônomo" - o
sistema analisa seu próprio histórico de acerto (guardado pela
Etapa C) e ajusta sozinho o critério mínimo para considerar uma
oportunidade "validada" em cada mercado.

IMPORTANTE: só ajusta um mercado quando há amostra estatística
mínima (padrão: 20 previsões já conferidas naquele mercado
específico). Com poucos dados, qualquer "ajuste" seria só ruído
- por isso o sistema prefere não mexer em nada a mexer errado.

Como funciona, na prática:
- Cada mercado tem um "limiar mínimo de score" para ser
  considerado validado (hoje, fixo em 70 no código, igual ao
  status "APTO").
- Se o desempenho real de um mercado estiver consistentemente
  ruim (ROI bem negativo, amostra suficiente), o limiar sobe -
  o sistema fica mais exigente com esse mercado.
- Se o desempenho estiver consistentemente bom, o limiar pode
  descer um pouco - mas de forma conservadora, para não
  "superajustar" com base em sorte de amostra pequena.
"""

from db import conectar_banco


AMOSTRA_MINIMA_PADRAO = 20

LIMIAR_PADRAO = 70.0
LIMIAR_MINIMO = 60.0
LIMIAR_MAXIMO = 90.0

PASSO_AJUSTE = 3.0

CHAVE_LIMIAR_OVER15 = "limiar_validacao_over15"


def obter_parametro(chave, valor_padrao):
    with conectar_banco() as conexao:
        linha = conexao.execute(
            "SELECT valor FROM config_dinamica WHERE chave = ?",
            (chave,),
        ).fetchone()

    if not linha:
        return valor_padrao

    return float(linha["valor"])


def definir_parametro(chave, valor, motivo=""):
    with conectar_banco() as conexao:
        existente = conexao.execute(
            "SELECT chave FROM config_dinamica WHERE chave = ?",
            (chave,),
        ).fetchone()

        if existente:
            conexao.execute(
                """
                UPDATE config_dinamica
                SET valor = ?, motivo_ultima_atualizacao = ?,
                    atualizado_em = CURRENT_TIMESTAMP
                WHERE chave = ?
                """,
                (float(valor), motivo, chave),
            )
        else:
            conexao.execute(
                """
                INSERT INTO config_dinamica (chave, valor, motivo_ultima_atualizacao)
                VALUES (?, ?, ?)
                """,
                (chave, float(valor), motivo),
            )
        conexao.commit()


def obter_limiar_validacao_over15():
    """
    O valor que match_analysis_engine.py consulta para decidir
    se uma previsão de "+1,5 gols" é forte o bastante para ser
    recomendada. Começa em 70 (igual ao comportamento original,
    antes de qualquer ajuste automático) e só muda depois que
    houver dados reais suficientes.
    """
    return obter_parametro(CHAVE_LIMIAR_OVER15, LIMIAR_PADRAO)


def _estatisticas_do_mercado(mercado, amostra_minima):
    with conectar_banco() as conexao:
        previsoes = conexao.execute(
            """
            SELECT status, odd FROM previsoes
            WHERE mercado = ? AND status IN ('GREEN', 'RED')
            """,
            (mercado,),
        ).fetchall()

    total = len(previsoes)

    if total < amostra_minima:
        return {
            "amostra_suficiente": False,
            "total": total,
        }

    greens = [p for p in previsoes if p["status"] == "GREEN"]
    stake_total = total * 1.0
    retorno_total = sum(float(p["odd"]) for p in greens)
    roi = (retorno_total - stake_total) / stake_total * 100

    return {
        "amostra_suficiente": True,
        "total": total,
        "green": len(greens),
        "roi": round(roi, 2),
    }


def avaliar_e_ajustar_criterios(amostra_minima=AMOSTRA_MINIMA_PADRAO):
    """
    Analisa o desempenho real do mercado "+1,5 gols" (o único
    mercado com recomendação validada na V1) e ajusta o limiar se
    houver dados suficientes e um sinal claro.

    Retorna um relatório do que foi feito (ou por que não foi
    feito nada) - nunca lança exceção.
    """
    stats = _estatisticas_do_mercado(
        "Mais de 1,5 gols", amostra_minima
    )

    if not stats["amostra_suficiente"]:
        return {
            "ajustado": False,
            "motivo": (
                f"Amostra insuficiente ainda "
                f"({stats['total']}/{amostra_minima} previsões "
                f"conferidas) - nenhum ajuste é feito até "
                f"acumular dados reais suficientes."
            ),
        }

    limiar_atual = obter_limiar_validacao_over15()
    roi = stats["roi"]

    if roi <= -10:
        novo_limiar = min(
            limiar_atual + PASSO_AJUSTE, LIMIAR_MAXIMO
        )
        motivo = (
            f"ROI real de {roi}% em {stats['total']} previsões - "
            f"critério fica mais exigente (de {limiar_atual} "
            f"para {novo_limiar})."
        )
    elif roi >= 15:
        novo_limiar = max(
            limiar_atual - PASSO_AJUSTE, LIMIAR_MINIMO
        )
        motivo = (
            f"ROI real de {roi}% em {stats['total']} previsões - "
            f"critério fica um pouco menos exigente (de "
            f"{limiar_atual} para {novo_limiar})."
        )
    else:
        return {
            "ajustado": False,
            "motivo": (
                f"ROI real de {roi}% em {stats['total']} "
                f"previsões está dentro do esperado - nenhum "
                f"ajuste necessário."
            ),
        }

    if novo_limiar == limiar_atual:
        return {
            "ajustado": False,
            "motivo": "Limiar já está no limite permitido.",
        }

    definir_parametro(
        CHAVE_LIMIAR_OVER15, novo_limiar, motivo
    )

    return {
        "ajustado": True,
        "limiar_anterior": limiar_atual,
        "limiar_novo": novo_limiar,
        "motivo": motivo,
    }
