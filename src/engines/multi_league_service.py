"""
MultiLeagueService: a "vitrine" de múltiplos campeonatos - mostra
jogos de várias competições (Champions League, Premier League,
La Liga, Bundesliga, Serie A da Itália, Ligue 1, Libertadores,
Brasileirão Série B), com placar ao vivo quando disponível.

IMPORTANTE: diferente do Brasileirão Série A (que tem análise
completa do EntradaPro), estes campeonatos aparecem só como
informação - sem probabilidade, Value ou recomendação, porque
não temos dados históricos locais para calcular isso ainda.

⚠️ CUSTO: consulta várias ligas de uma vez, então usa mais
chamadas de API do que as outras funcionalidades. Por isso tem
cache de 15 minutos aplicado na camada de UI.
"""

from engines.fixtures_engine import (
    buscar_liga_por_nome,
    buscar_jogos_futuros_liga,
)


LIGAS_VITRINE = (
    {"nome": "Champions League", "pais": None},
    {"nome": "Premier League", "pais": "England"},
    {"nome": "La Liga", "pais": "Spain"},
    {"nome": "Bundesliga", "pais": "Germany"},
    {"nome": "Serie A", "pais": "Italy"},
    {"nome": "Ligue 1", "pais": "France"},
    {"nome": "Libertadores", "pais": None},
    {"nome": "Serie B", "pais": "Brazil"},
)


def buscar_vitrine_campeonatos(dias_a_frente=3):
    """
    Busca os próximos jogos de cada campeonato da vitrine.
    Campeonatos que falharem (API fora do ar, nome não encontrado
    etc.) são simplesmente omitidos do resultado - não derrubam
    os demais.

    Retorna {"sucesso": True, "campeonatos": [
        {"nome": str, "jogos": [...]}, ...
    ]}
    """
    campeonatos_encontrados = []

    for config_liga in LIGAS_VITRINE:
        try:
            liga = buscar_liga_por_nome(
                config_liga["nome"], pais=config_liga["pais"]
            )
        except Exception:
            continue

        if not liga.get("sucesso"):
            continue

        try:
            busca_jogos = buscar_jogos_futuros_liga(
                liga["liga_id"],
                liga["temporada"],
                dias_a_frente=dias_a_frente,
            )
        except Exception:
            continue

        if not busca_jogos.get("sucesso"):
            continue

        jogos = busca_jogos.get("jogos", [])

        if not jogos:
            continue

        campeonatos_encontrados.append({
            "nome": liga.get("nome", config_liga["nome"]),
            "jogos": jogos,
        })

    return {
        "sucesso": True,
        "campeonatos": campeonatos_encontrados,
    }
