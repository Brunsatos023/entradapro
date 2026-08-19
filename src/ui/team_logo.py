from pathlib import Path


PASTA_ESCUDOS = (
    Path(__file__).resolve().parent.parent
    / "assets"
    / "teams"
)


MAPA_NOMES = {
    "Atletico-MG": "atletico_mg.png",
    "Atletico Goianiense": "atletico_goianiense.png",
    "Athletico-PR": "athletico_pr.png",
    "Bahia": "bahia.png",
    "Botafogo": "botafogo.png",
    "RB Bragantino": "rb_bragantino.png",
    "Corinthians": "corinthians.png",
    "Criciuma": "criciuma.png",
    "Cruzeiro": "cruzeiro.png",
    "Cuiaba": "cuiaba.png",
    "Flamengo": "flamengo.png",
    "Fluminense": "fluminense.png",
    "Fortaleza EC": "fortaleza.png",
    "Gremio": "gremio.png",
    "Internacional": "internacional.png",
    "Juventude": "juventude.png",
    "Palmeiras": "palmeiras.png",
    "Sao Paulo": "sao_paulo.png",
    "Vasco DA Gama": "vasco.png",
    "Vitoria": "vitoria.png"
}


def obter_caminho_escudo(nome_time):
    nome_arquivo = MAPA_NOMES.get(nome_time)

    if not nome_arquivo:
        return None

    caminho = PASTA_ESCUDOS / nome_arquivo

    if not caminho.exists():
        return None

    return str(caminho)