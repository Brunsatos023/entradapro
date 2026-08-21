"""
Escudos dos times: o dataset histórico já guarda o link do
escudo real de cada time (vem direto da API-Football, servido
publicamente, sem precisar de chave). Usamos a imagem de verdade
sempre que disponível; times fora da lista conhecida caem num
círculo com sigla, como reserva.
"""

# nome: (url_escudo_real, cor_fundo_reserva, cor_texto_reserva, sigla_reserva)
ESCUDOS = {
    "Flamengo": (
        "https://media.api-sports.io/football/teams/127.png",
        "#7a1f1f", "#f5c9c9", "FLA",
    ),
    "Palmeiras": (
        "https://media.api-sports.io/football/teams/121.png",
        "#0f3a1f", "#a8e0b8", "PAL",
    ),
    "Corinthians": (
        "https://media.api-sports.io/football/teams/131.png",
        "#1a1a2e", "#c9c9e8", "COR",
    ),
    "Sao Paulo": (
        "https://media.api-sports.io/football/teams/126.png",
        "#e6e6e6", "#333333", "SAO",
    ),
    "Gremio": (
        "https://media.api-sports.io/football/teams/130.png",
        "#0d3d8f", "#c9dcf5", "GRE",
    ),
    "Internacional": (
        "https://media.api-sports.io/football/teams/119.png",
        "#8f0d0d", "#f5c9c9", "INT",
    ),
    "Fluminense": (
        "https://media.api-sports.io/football/teams/124.png",
        "#7a1f2e", "#f0d9a8", "FLU",
    ),
    "Botafogo": (
        "https://media.api-sports.io/football/teams/120.png",
        "#1a1a1a", "#e0e0e0", "BOT",
    ),
    "Vasco DA Gama": (
        "https://media.api-sports.io/football/teams/133.png",
        "#1a1a1a", "#e0e0e0", "VAS",
    ),
    "Atletico-MG": (
        "https://media.api-sports.io/football/teams/1062.png",
        "#1a1a1a", "#e0e0e0", "CAM",
    ),
    "Cruzeiro": (
        "https://media.api-sports.io/football/teams/135.png",
        "#0d3d8f", "#c9dcf5", "CRU",
    ),
    "Bahia": (
        "https://media.api-sports.io/football/teams/118.png",
        "#1a1a4e", "#e0e0f5", "BAH",
    ),
    "Fortaleza EC": (
        "https://media.api-sports.io/football/teams/154.png",
        "#0d3d8f", "#f5c9c9", "FOR",
    ),
    "Atletico Goianiense": (
        "https://media.api-sports.io/football/teams/144.png",
        "#7a1f1f", "#f0d9a8", "ACG",
    ),
    "Atletico Paranaense": (
        "https://media.api-sports.io/football/teams/134.png",
        "#8f0d0d", "#e0e0e0", "CAP",
    ),
    "Criciuma": (
        "https://media.api-sports.io/football/teams/140.png",
        "#7a1f1f", "#e0e0e0", "CRI",
    ),
    "Cuiaba": (
        "https://media.api-sports.io/football/teams/1193.png",
        "#0d5c3d", "#f0d9a8", "CUI",
    ),
    "Juventude": (
        "https://media.api-sports.io/football/teams/152.png",
        "#0d3d1f", "#e0e0e0", "JUV",
    ),
    "RB Bragantino": (
        "https://media.api-sports.io/football/teams/794.png",
        "#e6e6e6", "#7a1f1f", "RBB",
    ),
    "Vitoria": (
        "https://media.api-sports.io/football/teams/136.png",
        "#8f0d0d", "#e0e0e0", "VIT",
    ),
}

ESCUDO_PADRAO = ("#163627", "#909f88")


def obter_url_escudo(nome_time):
    """Retorna a URL do escudo real, ou None se o time não for conhecido."""
    if nome_time in ESCUDOS:
        return ESCUDOS[nome_time][0]
    return None


def obter_escudo(nome_time):
    """
    Retorna (cor_fundo, cor_texto, sigla) - usado como reserva
    quando não há escudo real disponível (time desconhecido, ou
    imagem falhou ao carregar).
    """
    if nome_time in ESCUDOS:
        _, cor_fundo, cor_texto, sigla = ESCUDOS[nome_time]
        return (cor_fundo, cor_texto, sigla)

    cor_fundo, cor_texto = ESCUDO_PADRAO
    sigla = (nome_time or "?")[:3].upper()
    return (cor_fundo, cor_texto, sigla)


def html_escudo(nome_time, tamanho=30):
    """
    Retorna o HTML pronto do escudo de um time: a imagem real
    quando disponível, com um círculo de sigla como reserva
    (via onerror, caso a imagem falhe ao carregar).
    """
    url = obter_url_escudo(nome_time)
    cor_fundo, cor_texto, sigla = obter_escudo(nome_time)

    se_falhar = (
        f"this.style.display='none';"
        f"this.nextElementSibling.style.display='inline-flex';"
    )

    reserva = (
        f'<span class="escudo-time" '
        f'style="width:{tamanho}px;height:{tamanho}px;'
        f'display:{"none" if url else "inline-flex"};'
        f'background:{cor_fundo};color:{cor_texto};">'
        f'{sigla}</span>'
    )

    if not url:
        return reserva

    return (
        f'<img src="{url}" alt="{nome_time}" '
        f'style="width:{tamanho}px;height:{tamanho}px;'
        f'object-fit:contain;vertical-align:middle;" '
        f'onerror="{se_falhar}" />'
        f'{reserva}'
    )
