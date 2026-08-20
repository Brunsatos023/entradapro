"""
FixturesEngine: busca partidas futuras reais do Brasileirão Série A
via API-Football — a base da Etapa A do roteiro "EntradaPro
Autônomo" (jogos futuros automáticos, sem escolha manual).

Diferente de "acertar" o ID da liga de cabeça (arriscado - um
número errado buscaria dados de outra competição sem avisar),
esta engine pergunta à própria API-Football qual é o ID correto
pelo nome, uma vez, e guarda em cache.

Uso típico:

    from engines.fixtures_engine import buscar_jogos_futuros

    resultado = buscar_jogos_futuros(dias_a_frente=7)

    if resultado["sucesso"]:
        for jogo in resultado["jogos"]:
            print(jogo["mandante"], "x", jogo["visitante"], jogo["data"])
"""

import os
from datetime import datetime, timedelta

import requests


BASE_URL = "https://v3.football.api-sports.io"

_CACHE_LIGA = {}


def _chave_api():
    return os.getenv("API_FOOTBALL_KEY")


def _cabecalhos():
    return {"x-apisports-key": _chave_api()}


def buscar_liga_por_nome(
    nome_liga, pais=None, tipo_esperado="League"
):
    """
    Descobre o ID e a temporada atual de qualquer liga/competição
    consultando a API-Football pelo nome (não usa um número fixo
    "chutado" - evita buscar a competição errada por engano).

    Retorna {"sucesso": True, "liga_id": int, "temporada": int}
    ou {"sucesso": False, "mensagem": "..."}.
    """
    chave_cache = f"{nome_liga}|{pais}"

    if chave_cache in _CACHE_LIGA:
        return _CACHE_LIGA[chave_cache]

    chave = _chave_api()
    if not chave:
        return {
            "sucesso": False,
            "mensagem": "API_FOOTBALL_KEY não configurada no .env.",
        }

    parametros = {"name": nome_liga}
    if pais:
        parametros["country"] = pais

    try:
        resposta = requests.get(
            f"{BASE_URL}/leagues",
            headers=_cabecalhos(),
            params=parametros,
            timeout=20,
        )
    except requests.RequestException as erro:
        return {
            "sucesso": False,
            "mensagem": f"Erro de conexão com a API-Football: {erro}",
        }

    if resposta.status_code != 200:
        return {
            "sucesso": False,
            "mensagem": (
                f"API-Football respondeu com status "
                f"{resposta.status_code}."
            ),
        }

    dados = resposta.json()
    ligas = dados.get("response", [])

    liga_encontrada = None
    for item in ligas:
        nome_encontrado = item.get("league", {}).get("name", "")
        tipo = item.get("league", {}).get("type", "")

        if (
            nome_liga.lower() in nome_encontrado.lower()
            and (not tipo_esperado or tipo == tipo_esperado)
        ):
            liga_encontrada = item
            break

    if not liga_encontrada:
        return {
            "sucesso": False,
            "mensagem": (
                f"Não encontrei '{nome_liga}' na resposta "
                "da API-Football."
            ),
        }

    liga_id = liga_encontrada["league"]["id"]

    temporada_atual = None
    for temporada in liga_encontrada.get("seasons", []):
        if temporada.get("current"):
            temporada_atual = temporada.get("year")
            break

    if temporada_atual is None:
        temporada_atual = datetime.now().year

    resultado = {
        "sucesso": True,
        "liga_id": liga_id,
        "temporada": temporada_atual,
        "nome": liga_encontrada["league"]["name"],
    }

    _CACHE_LIGA[chave_cache] = resultado
    return resultado


def buscar_liga_brasileirao_serie_a():
    """
    Atalho para o Brasileirão Série A especificamente (mantido
    para compatibilidade com o restante do projeto, que já
    depende desta função exata).
    """
    return buscar_liga_por_nome("Serie A", pais="Brazil")


def _formatar_jogo(item_fixture):
    fixture = item_fixture.get("fixture", {})
    teams = item_fixture.get("teams", {})
    league = item_fixture.get("league", {})

    data_iso = fixture.get("date", "")
    gols = item_fixture.get("goals", {})

    status_curto = fixture.get("status", {}).get("short")

    return {
        "fixture_id": fixture.get("id"),
        "data_iso": data_iso,
        "status": status_curto,
        "ao_vivo": status_curto in {"1H", "2H", "HT", "ET", "P"},
        "encerrado": status_curto in {"FT", "AET", "PEN"},
        "gols_casa": gols.get("home"),
        "gols_visitante": gols.get("away"),
        "liga": league.get("name"),
        "mandante": teams.get("home", {}).get("name"),
        "mandante_id": teams.get("home", {}).get("id"),
        "visitante": teams.get("away", {}).get("name"),
        "visitante_id": teams.get("away", {}).get("id"),
    }


def buscar_jogos_futuros_liga(liga_id, temporada, dias_a_frente=7):
    """
    Versão genérica de buscar_jogos_futuros: busca jogos de
    QUALQUER liga (dado o ID e a temporada), não só o
    Brasileirão. Usada pela "vitrine" de múltiplos campeonatos.

    Retorna o mesmo formato de buscar_jogos_futuros().
    """
    chave = _chave_api()
    if not chave:
        return {
            "sucesso": False,
            "mensagem": "API_FOOTBALL_KEY não configurada no .env.",
        }

    hoje = datetime.now().date()
    ate = hoje + timedelta(days=dias_a_frente)

    try:
        resposta = requests.get(
            f"{BASE_URL}/fixtures",
            headers=_cabecalhos(),
            params={
                "league": liga_id,
                "season": temporada,
                "from": hoje.isoformat(),
                "to": ate.isoformat(),
            },
            timeout=20,
        )
    except requests.RequestException as erro:
        return {
            "sucesso": False,
            "mensagem": f"Erro de conexão com a API-Football: {erro}",
        }

    if resposta.status_code != 200:
        return {
            "sucesso": False,
            "mensagem": (
                f"API-Football respondeu com status "
                f"{resposta.status_code}."
            ),
        }

    dados = resposta.json()
    itens = dados.get("response", [])

    jogos = [_formatar_jogo(item) for item in itens]

    return {
        "sucesso": True,
        "jogos": jogos,
        "total": len(jogos),
    }


def buscar_resultado_fixture(fixture_id):
    """
    Consulta o placar final de uma partida específica já
    encerrada (usado para conferir se uma previsão feita
    anteriormente deu Green ou Red).

    Retorna {"sucesso": True, "gols_casa": int, "gols_visitante":
    int, "encerrado": bool} ou {"sucesso": False, "mensagem": "..."}.
    """
    chave = _chave_api()

    if not chave:
        return {
            "sucesso": False,
            "mensagem": "API_FOOTBALL_KEY não configurada no .env.",
        }

    try:
        resposta = requests.get(
            f"{BASE_URL}/fixtures",
            headers=_cabecalhos(),
            params={"id": fixture_id},
            timeout=20,
        )
    except requests.RequestException as erro:
        return {
            "sucesso": False,
            "mensagem": f"Erro de conexão com a API-Football: {erro}",
        }

    if resposta.status_code != 200:
        return {
            "sucesso": False,
            "mensagem": (
                f"API-Football respondeu com status "
                f"{resposta.status_code}."
            ),
        }

    dados = resposta.json()
    itens = dados.get("response", [])

    if not itens:
        return {
            "sucesso": False,
            "mensagem": "Partida não encontrada.",
        }

    item = itens[0]
    status_curto = item.get("fixture", {}).get("status", {}).get("short")

    # Códigos de status da API-Football que indicam jogo encerrado
    encerrado = status_curto in {"FT", "AET", "PEN"}

    gols = item.get("goals", {})

    return {
        "sucesso": True,
        "encerrado": encerrado,
        "status": status_curto,
        "gols_casa": gols.get("home"),
        "gols_visitante": gols.get("away"),
    }


def buscar_jogos_futuros(dias_a_frente=7):
    """
    Busca as partidas futuras do Brasileirão Série A entre hoje e
    "dias_a_frente" dias a partir de agora.

    Retorna:
        {"sucesso": True, "jogos": [ {...}, {...} ]}
    ou
        {"sucesso": False, "mensagem": "..."}
    """
    liga = buscar_liga_brasileirao_serie_a()

    if not liga["sucesso"]:
        return liga

    hoje = datetime.now().date()
    ate = hoje + timedelta(days=dias_a_frente)

    try:
        resposta = requests.get(
            f"{BASE_URL}/fixtures",
            headers=_cabecalhos(),
            params={
                "league": liga["liga_id"],
                "season": liga["temporada"],
                "from": hoje.isoformat(),
                "to": ate.isoformat(),
            },
            timeout=20,
        )
    except requests.RequestException as erro:
        return {
            "sucesso": False,
            "mensagem": f"Erro de conexão com a API-Football: {erro}",
        }

    if resposta.status_code != 200:
        return {
            "sucesso": False,
            "mensagem": (
                f"API-Football respondeu com status "
                f"{resposta.status_code}."
            ),
        }

    dados = resposta.json()
    itens = dados.get("response", [])

    jogos = [_formatar_jogo(item) for item in itens]

    return {
        "sucesso": True,
        "jogos": jogos,
        "total": len(jogos),
    }
