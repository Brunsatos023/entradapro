"""
CornersEngine: análise do mercado de escanteios - diferente das
outras engines do EntradaPro, este dado NÃO vem do dataset
histórico local (que não tem escanteios). Precisa buscar direto
na API-Football, partida por partida, os últimos jogos de cada
time.

⚠️ CUSTO: esta engine faz bem mais chamadas à API do que as
outras (até ~12 por confronto, contra 1-2 das demais). Por isso,
diferente das outras engines, NÃO é chamada automaticamente pela
varredura de oportunidades - só quando o usuário pede
explicitamente a análise de escanteios de uma partida específica.
"""

import os

import requests

from engines.value_engine import ValueEngine


BASE_URL = "https://v3.football.api-sports.io"

LINHA_PADRAO = 9.5
JOGOS_ANALISADOS = 5


def _chave_api():
    return os.getenv("API_FOOTBALL_KEY")


def _cabecalhos():
    return {"x-apisports-key": _chave_api()}


def _buscar_ultimos_fixtures_do_time(team_id, quantidade):
    try:
        resposta = requests.get(
            f"{BASE_URL}/fixtures",
            headers=_cabecalhos(),
            params={"team": team_id, "last": quantidade},
            timeout=20,
        )
    except requests.RequestException as erro:
        return {
            "sucesso": False,
            "mensagem": f"Erro de conexão: {erro}",
        }

    if resposta.status_code != 200:
        return {
            "sucesso": False,
            "mensagem": f"API respondeu com status {resposta.status_code}.",
        }

    dados = resposta.json()
    return {"sucesso": True, "fixtures": dados.get("response", [])}


def _buscar_corners_da_partida(fixture_id, team_id):
    try:
        resposta = requests.get(
            f"{BASE_URL}/fixtures/statistics",
            headers=_cabecalhos(),
            params={"fixture": fixture_id, "team": team_id},
            timeout=20,
        )
    except requests.RequestException:
        return None

    if resposta.status_code != 200:
        return None

    dados = resposta.json()
    itens = dados.get("response", [])

    if not itens:
        return None

    estatisticas = itens[0].get("statistics", [])

    for estatistica in estatisticas:
        if estatistica.get("type") == "Corner Kicks":
            valor = estatistica.get("value")
            try:
                return int(valor)
            except (TypeError, ValueError):
                return None

    return None


def buscar_media_corners_time(team_id, ultimos_n=JOGOS_ANALISADOS):
    """
    Busca a média de escanteios (a favor) de um time nos últimos
    N jogos, consultando a API-Football diretamente (não usa o
    dataset local, que não tem esse dado).

    Retorna {"sucesso": True, "media_corners": float,
    "jogos_analisados": int} ou {"sucesso": False, "mensagem": "..."}.
    """
    chave = _chave_api()
    if not chave:
        return {
            "sucesso": False,
            "mensagem": "API_FOOTBALL_KEY não configurada no .env.",
        }

    busca_fixtures = _buscar_ultimos_fixtures_do_time(
        team_id, ultimos_n
    )

    if not busca_fixtures["sucesso"]:
        return busca_fixtures

    fixtures = busca_fixtures["fixtures"]

    if not fixtures:
        return {
            "sucesso": False,
            "mensagem": "Nenhuma partida recente encontrada para este time.",
        }

    valores_corners = []

    for item in fixtures:
        fixture_id = item.get("fixture", {}).get("id")

        if not fixture_id:
            continue

        corners = _buscar_corners_da_partida(fixture_id, team_id)

        if corners is not None:
            valores_corners.append(corners)

    if not valores_corners:
        return {
            "sucesso": False,
            "mensagem": (
                "Não foi possível obter dados de escanteios "
                "para este time (API pode não ter essa "
                "estatística disponível para essas partidas)."
            ),
        }

    media = sum(valores_corners) / len(valores_corners)

    return {
        "sucesso": True,
        "media_corners": round(media, 2),
        "jogos_analisados": len(valores_corners),
    }


def _calcular_probabilidade_over_corners(
    media_casa, media_fora, linha
):
    """
    Estimativa simples: soma as médias dos dois times como
    expectativa combinada de escanteios, e usa uma distribuição
    aproximada para estimar a chance de passar da linha.
    Abordagem conservadora e transparente (não é um modelo
    estatístico sofisticado - é uma primeira versão).
    """
    expectativa_total = media_casa + media_fora

    diferenca = expectativa_total - linha

    # Cada escanteio de diferença acima/abaixo da linha desloca a
    # probabilidade em ~7 pontos percentuais, partindo de 50%.
    probabilidade = 50 + (diferenca * 7)

    return max(5.0, min(95.0, round(probabilidade, 2)))


def analisar_corners(
    id_mandante,
    id_visitante,
    odd_over_corners=None,
    linha=LINHA_PADRAO,
):
    """
    Analisa o mercado de escanteios para um confronto. Se
    "odd_over_corners" for informada, também calcula o Value real
    (edge, valor esperado) desse mercado.

    Retorna um dicionário com o resultado, ou
    {"sucesso": False, "mensagem": "..."} se não conseguir os
    dados necessários de qualquer um dos dois times.
    """
    resultado_casa = buscar_media_corners_time(id_mandante)

    if not resultado_casa["sucesso"]:
        return {
            "sucesso": False,
            "mensagem": (
                f"Mandante: {resultado_casa['mensagem']}"
            ),
        }

    resultado_fora = buscar_media_corners_time(id_visitante)

    if not resultado_fora["sucesso"]:
        return {
            "sucesso": False,
            "mensagem": (
                f"Visitante: {resultado_fora['mensagem']}"
            ),
        }

    media_casa = resultado_casa["media_corners"]
    media_fora = resultado_fora["media_corners"]

    probabilidade = _calcular_probabilidade_over_corners(
        media_casa, media_fora, linha
    )

    resposta = {
        "sucesso": True,
        "linha": linha,
        "media_casa": media_casa,
        "media_fora": media_fora,
        "expectativa_total": round(media_casa + media_fora, 2),
        "probabilidade_over": probabilidade,
        "resultado_value": None,
    }

    if odd_over_corners:
        analise_value = ValueEngine(
            probabilidade_footballai=probabilidade,
            odd_casa=odd_over_corners,
        ).analisar()

        if not analise_value.get("erro"):
            resposta["resultado_value"] = analise_value

    return resposta
