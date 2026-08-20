"""
PredictionHistoryService: a Etapa C do roteiro "EntradaPro
Autônomo" - guarda toda previsão feita (pela varredura automática
ou manualmente) e depois confere com o resultado real, marcando
Green/Red/Void.

É a base necessária para a Etapa D (autoajuste de critérios): sem
saber o que o sistema acertou ou errou, não tem como ele aprender
sozinho.
"""

from datetime import datetime

from db import conectar_banco
from engines.fixtures_engine import buscar_resultado_fixture


STATUS_PENDENTE = "PENDENTE"
STATUS_GREEN = "GREEN"
STATUS_RED = "RED"
STATUS_VOID = "VOID"


def registrar_previsao(
    fixture_id,
    mandante,
    visitante,
    mercado,
    odd,
    probabilidade,
    edge,
    data_jogo=None,
):
    """
    Registra uma previsão feita pelo sistema. Seguro de chamar
    mais de uma vez para o mesmo jogo/mercado - não duplica
    (fixture_id + mercado é uma combinação única).

    Retorna {"sucesso": True, "ja_existia": bool, "previsao_id": int}
    """
    fixture_id = str(fixture_id)

    with conectar_banco() as conexao:
        existente = conexao.execute(
            """
            SELECT id FROM previsoes
            WHERE fixture_id = ? AND mercado = ?
            """,
            (fixture_id, mercado),
        ).fetchone()

        if existente:
            return {
                "sucesso": True,
                "ja_existia": True,
                "previsao_id": existente["id"],
            }

        cursor = conexao.execute(
            """
            INSERT INTO previsoes (
                fixture_id, mandante, visitante, mercado,
                odd, probabilidade, edge, data_jogo, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                fixture_id, mandante, visitante, mercado,
                float(odd), float(probabilidade), float(edge),
                data_jogo, STATUS_PENDENTE,
            ),
        )
        conexao.commit()

        return {
            "sucesso": True,
            "ja_existia": False,
            "previsao_id": cursor.lastrowid,
        }


def _mercado_bateu(mercado, gols_casa, gols_visitante):
    """
    Decide se um mercado específico deu Green (True) ou Red
    (False), dado o placar final real.
    """
    total_gols = gols_casa + gols_visitante

    if mercado == "Mais de 1,5 gols":
        return total_gols >= 2

    if mercado == "Mais de 2,5 gols":
        return total_gols >= 3

    if mercado == "Ambas marcam — Sim":
        return gols_casa > 0 and gols_visitante > 0

    return None  # mercado desconhecido - fica como Void


def verificar_previsoes_pendentes(limite=50):
    """
    Procura previsões PENDENTES cujo jogo já deveria ter
    acontecido, consulta o resultado real na API-Football, e
    marca Green/Red (ou Void, se o jogo foi cancelado/adiado).

    Retorna {"sucesso": True, "verificadas": int, "green": int,
    "red": int, "void": int}.
    """
    with conectar_banco() as conexao:
        pendentes = conexao.execute(
            """
            SELECT id, fixture_id, mercado
            FROM previsoes
            WHERE status = ?
            LIMIT ?
            """,
            (STATUS_PENDENTE, limite),
        ).fetchall()

    contagem = {"green": 0, "red": 0, "void": 0}

    for previsao in pendentes:
        try:
            resultado_fixture = buscar_resultado_fixture(
                previsao["fixture_id"]
            )
        except Exception:
            continue

        if not resultado_fixture.get("sucesso"):
            continue

        if not resultado_fixture.get("encerrado"):
            continue  # ainda não aconteceu ou está rolando, tenta depois

        gols_casa = resultado_fixture.get("gols_casa")
        gols_visitante = resultado_fixture.get("gols_visitante")

        if gols_casa is None or gols_visitante is None:
            continue

        bateu = _mercado_bateu(
            previsao["mercado"], gols_casa, gols_visitante
        )

        if bateu is None:
            novo_status = STATUS_VOID
            contagem["void"] += 1
        elif bateu:
            novo_status = STATUS_GREEN
            contagem["green"] += 1
        else:
            novo_status = STATUS_RED
            contagem["red"] += 1

        with conectar_banco() as conexao:
            conexao.execute(
                """
                UPDATE previsoes
                SET status = ?, gols_casa_real = ?,
                    gols_visitante_real = ?,
                    verificado_em = ?
                WHERE id = ?
                """,
                (
                    novo_status, gols_casa, gols_visitante,
                    datetime.now().isoformat(timespec="seconds"),
                    previsao["id"],
                ),
            )
            conexao.commit()

    return {
        "sucesso": True,
        "verificadas": sum(contagem.values()),
        **contagem,
    }


def obter_estatisticas_historico():
    """
    Calcula as estatísticas gerais do histórico de previsões já
    conferidas: total, greens, reds, taxa de acerto, ROI, yield e
    odd média - a base para a Etapa D (autoajuste).

    Considera stake fixa de 1 unidade por previsão para o cálculo
    de ROI/yield (métrica relativa, não depende de valor real
    apostado por ninguém).
    """
    with conectar_banco() as conexao:
        previsoes = conexao.execute(
            """
            SELECT status, odd FROM previsoes
            WHERE status IN (?, ?)
            """,
            (STATUS_GREEN, STATUS_RED),
        ).fetchall()

    total = len(previsoes)

    if total == 0:
        return {
            "total": 0,
            "green": 0,
            "red": 0,
            "taxa_acerto": None,
            "roi": None,
            "yield_": None,
            "odd_media": None,
        }

    greens = [p for p in previsoes if p["status"] == STATUS_GREEN]
    reds = [p for p in previsoes if p["status"] == STATUS_RED]

    quantidade_green = len(greens)
    quantidade_red = len(reds)

    stake_total = total * 1.0
    retorno_total = sum(float(p["odd"]) for p in greens)
    lucro = retorno_total - stake_total

    odd_media = sum(float(p["odd"]) for p in previsoes) / total

    return {
        "total": total,
        "green": quantidade_green,
        "red": quantidade_red,
        "taxa_acerto": round(quantidade_green / total * 100, 2),
        "roi": round(lucro / stake_total * 100, 2),
        "yield_": round(lucro / stake_total * 100, 2),
        "odd_media": round(odd_media, 2),
    }
