"""
Escudos dos times: como ainda não temos os brasões reais (viria da
API bloqueada), usamos um "escudo" ilustrativo — círculo colorido
com a sigla do time, nas cores reais de cada clube. Já cobre todos
os times do Brasileirão Série A do dataset local; qualquer time
fora dessa lista cai num estilo neutro.
"""

# cor_fundo, cor_texto, sigla - cores aproximadas do uniforme principal
ESCUDOS = {
    "Flamengo": ("#7a1f1f", "#f5c9c9", "FLA"),
    "Palmeiras": ("#0f3a1f", "#a8e0b8", "PAL"),
    "Corinthians": ("#1a1a2e", "#c9c9e8", "COR"),
    "Sao Paulo": ("#e6e6e6", "#333333", "SAO"),
    "Santos": ("#e6e6e6", "#1a1a1a", "SAN"),
    "Gremio": ("#0d3d8f", "#c9dcf5", "GRE"),
    "Internacional": ("#8f0d0d", "#f5c9c9", "INT"),
    "Fluminense": ("#7a1f2e", "#f0d9a8", "FLU"),
    "Botafogo": ("#1a1a1a", "#e0e0e0", "BOT"),
    "Vasco DA Gama": ("#1a1a1a", "#e0e0e0", "VAS"),
    "Atletico-MG": ("#1a1a1a", "#e0e0e0", "CAM"),
    "Cruzeiro": ("#0d3d8f", "#c9dcf5", "CRU"),
    "Bahia": ("#1a1a4e", "#e0e0f5", "BAH"),
    "Fortaleza EC": ("#0d3d8f", "#f5c9c9", "FOR"),
    "Atletico Goianiense": ("#7a1f1f", "#f0d9a8", "ACG"),
    "Atletico Paranaense": ("#8f0d0d", "#e0e0e0", "CAP"),
    "Criciuma": ("#7a1f1f", "#e0e0e0", "CRI"),
    "Cuiaba": ("#0d5c3d", "#f0d9a8", "CUI"),
    "Juventude": ("#0d3d1f", "#e0e0e0", "JUV"),
    "RB Bragantino": ("#e6e6e6", "#7a1f1f", "RBB"),
    "Vitoria": ("#8f0d0d", "#e0e0e0", "VIT"),
}

ESCUDO_PADRAO = ("#163627", "#909f88")


def obter_escudo(nome_time):
    """
    Retorna (cor_fundo, cor_texto, sigla) para um time. Times fora
    da lista conhecida recebem uma sigla derivada automaticamente
    das 3 primeiras letras, em estilo neutro.
    """
    if nome_time in ESCUDOS:
        return ESCUDOS[nome_time]

    cor_fundo, cor_texto = ESCUDO_PADRAO
    sigla = (nome_time or "?")[:3].upper()
    return (cor_fundo, cor_texto, sigla)


def html_escudo(nome_time):
    """Retorna o HTML pronto (span) do escudo circular de um time."""
    cor_fundo, cor_texto, sigla = obter_escudo(nome_time)

    return (
        f'<span class="escudo-time" '
        f'style="background:{cor_fundo};color:{cor_texto};">'
        f'{sigla}</span>'
    )
