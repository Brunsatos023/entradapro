"""
Utilitário compartilhado: casar nomes de times vindos da API-Football
(com acentos, formatação própria) com os nomes exatos usados no
dataset histórico local (sem acentos).

Usado tanto pela lista de "jogos futuros" (src/ui/jogos_futuros.py)
quanto pelo motor de varredura de oportunidades
(src/engines/opportunity_scanner.py) - centralizado aqui para não
duplicar a mesma lógica em dois lugares.
"""

import unicodedata


def normalizar_nome_time(nome):
    """
    Remove acentos e caixa para comparar nomes de times com
    segurança (ex: "São Paulo" da API vs "Sao Paulo" do dataset
    local precisam ser reconhecidos como o mesmo time).
    """
    sem_acento = unicodedata.normalize("NFKD", str(nome or ""))
    sem_acento = "".join(
        c for c in sem_acento if not unicodedata.combining(c)
    )
    return sem_acento.strip().lower()


def encontrar_time_local(nome_externo, nomes_times_locais):
    """
    Tenta casar um nome de time (vindo de uma API externa) com o
    nome correspondente no dataset local. Retorna o nome local
    exato, ou None se esse time não estiver no dataset local.
    """
    alvo = normalizar_nome_time(nome_externo)

    for nome_local in nomes_times_locais:
        candidato = normalizar_nome_time(nome_local)

        if alvo == candidato:
            return nome_local

        if alvo in candidato or candidato in alvo:
            return nome_local

    return None
